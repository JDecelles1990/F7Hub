"""Policy, strict collection contracts and whole-sequence concurrency."""
from dataclasses import replace
import itertools
import json
import threading
import unittest

from f7hub.domain.diagnostic_results import LOCAL_BASELINE_PACK, PowerShellProcessResult
from f7hub.services.powershell_service import (
    APPROVED_DIAGNOSTICS, PowerShellService, NETWORK_WARNINGS, SERVICES_WARNINGS,
    validate_network_snapshot, validate_services_snapshot,
)
from f7hub.services.script_service import ScriptCatalogEntry, VerifiedScriptCandidate
from test_powershell_service import record, envelope


def output(code, status='PASS'):
    spec = APPROVED_DIAGNOSTICS[code]
    if spec.operation == 'Get-SystemSnapshot':
        return envelope(status)
    network = spec.operation == 'Get-NetworkSnapshot'
    return dict(schemaVersion=1, operation=spec.operation, success=status!='ERROR', status=status,
        message=(('Local Windows network configuration snapshot collected.', 'Network configuration collected with incomplete or bounded data.', 'Unable to collect required local Windows network configuration.') if network else
                 ('Local Windows services snapshot collected.', 'Services snapshot collected with incomplete or bounded data.', 'Unable to collect required local Windows services information.'))[('PASS','WARNING','ERROR').index(status)],
        data=dict(computerName='PC', **({'interfaces':[]} if network else {'services':[]})),
        warnings=[(NETWORK_WARNINGS if network else SERVICES_WARNINGS)[-1]] if status=='WARNING' else [],
        errors=[('Required local network configuration is unavailable.' if network else 'Required local services information is unavailable.')] if status=='ERROR' else [])


class Scripts:
    def __init__(self):
        self.records = {code: replace(record(), script_code=code, relative_path=spec.relative_path, checksum_sha256=spec.digest) for code,spec in APPROVED_DIAGNOSTICS.items()}
        self.prepares = []
        self.drift = None

    def get_script(self, code):
        value = self.records.get(code)
        return ScriptCatalogEntry(value, 'AVAILABLE') if value is not None else None

    def prepare_verified_script(self, code, *, for_execution):
        assert for_execution
        self.prepares.append(code)
        return VerifiedScriptCandidate(self.drift or self.records[code], b'reviewed', None)


class Gateway:
    def __init__(self):
        self.calls = []
        self.statuses = ['PASS']*3
        self.failure = None
        self.hook = None

    def execute(self, candidate, timeout, revalidate):
        code = candidate.metadata.script_code
        index = len(self.calls)
        self.calls.append(code)
        if self.hook:
            self.hook(code)
        if not revalidate():
            return PowerShellProcessResult('REGISTRATION_CHANGED')
        if self.failure and self.failure[0] == index:
            return PowerShellProcessResult(self.failure[1], cleanup_verified=self.failure[1]!='CLEANUP_FAILED')
        status = self.statuses[index]
        return PowerShellProcessResult('COMPLETED', json.dumps(output(code,status)).encode(), exit_code=int(status=='ERROR'))


class DiagnosticPackTests(unittest.TestCase):
    def setUp(self):
        self.scripts, self.gateway = Scripts(), Gateway()
        self.service = PowerShellService(self.scripts,self.gateway)

    def test_all_27_severity_combinations_continue(self):
        for statuses in itertools.product(('PASS','WARNING','ERROR'), repeat=3):
            self.setUp()
            self.gateway.statuses = statuses
            result = self.service.execute_diagnostic_pack(LOCAL_BASELINE_PACK.code)
            self.assertEqual(result.classification, 'COMPLETED')
            self.assertEqual(result.collection_status, max(statuses,key=('PASS','WARNING','ERROR').index))
            self.assertEqual(tuple(self.gateway.calls), LOCAL_BASELINE_PACK.diagnostic_codes)
            self.assertEqual(result.skipped_codes,())

    def test_every_boundary_failure_aborts_at_every_member(self):
        failures = ('NOT_ELIGIBLE','INTEGRITY_FAILED','REGISTRATION_CHANGED','PRIVILEGE_BLOCKED','RUNTIME_UNAVAILABLE','PREPARATION_FAILED','LAUNCH_FAILED','TIMEOUT','OUTPUT_LIMIT_EXCEEDED','OUTPUT_CAPTURE_FAILED','INVALID_OUTPUT','CLEANUP_FAILED','EXECUTION_BUSY')
        for index,failure in itertools.product(range(3),failures):
            with self.subTest(index=index,failure=failure):
                self.setUp(); self.gateway.failure=(index,failure)
                result=self.service.execute_diagnostic_pack(LOCAL_BASELINE_PACK.code)
                self.assertEqual((result.classification,result.collection_status,result.failure_classification),('ABORTED',None,failure))
                self.assertEqual(tuple(self.gateway.calls), LOCAL_BASELINE_PACK.diagnostic_codes[:index+1])
                self.assertEqual(result.aborted_at, LOCAL_BASELINE_PACK.diagnostic_codes[index])
                self.assertEqual(result.skipped_codes, LOCAL_BASELINE_PACK.diagnostic_codes[index+1:])
                if failure=='CLEANUP_FAILED':
                    count=len(self.scripts.prepares)
                    self.assertEqual(self.service.execute_diagnostic(LOCAL_BASELINE_PACK.diagnostic_codes[0]).classification,'CLEANUP_FAILED')
                    self.assertEqual(self.service.execute_diagnostic_pack(LOCAL_BASELINE_PACK.code).failure_classification,'CLEANUP_FAILED')
                    self.assertFalse(self.service.pack_readiness()[0])
                    self.assertEqual(len(self.scripts.prepares),count)

    def test_all_types_and_unknown_diagnostic_never_prepare(self):
        for code,kind in itertools.product(APPROVED_DIAGNOSTICS,('REMEDIATION','ADMINISTRATIVE','REPORT','UTILITY','INTEGRATION')):
            self.scripts.records[code]=replace(self.scripts.records[code],script_type=kind)
            self.assertEqual(self.service.execute_diagnostic(code).classification,'NOT_ELIGIBLE')
        unknown='diagnostic.windows.unapproved'
        self.scripts.records[unknown]=replace(record(),script_code=unknown)
        for code in (unknown, unknown.upper(), None, [], ''):
            self.assertEqual(self.service.execute_diagnostic(code).classification,'NOT_ELIGIBLE')
        self.assertEqual(self.scripts.prepares,[])
        self.assertEqual(self.gateway.calls,[])

    def test_metadata_negatives_all_approved_codes(self):
        for code in APPROVED_DIAGNOSTICS:
            original=self.scripts.records[code]
            for field,value in (('relative_path','wrong'),('version','2'),('runtime','WINDOWS_POWERSHELL_5_1'),('risk_level','HIGH'),('privilege_level','LOCAL_ADMIN'),('checksum_sha256','0'*64),('requires_structured_output',0),('is_enabled',0),('is_enabled',True),('timeout_seconds',True),('timeout_seconds',61)):
                self.scripts.records[code]=replace(original,**{field:value})
                self.assertEqual(self.service.execute_diagnostic(code).classification,'NOT_ELIGIBLE')
            self.scripts.records[code]=original
        self.assertEqual(self.scripts.prepares,[])

    def test_registration_drift_and_between_member_disable(self):
        self.scripts.drift=replace(record(),updated_at='changed')
        self.assertEqual(self.service.execute_diagnostic_pack(LOCAL_BASELINE_PACK.code).failure_classification,'REGISTRATION_CHANGED')
        self.assertEqual(self.gateway.calls,[])
        self.setUp()
        self.gateway.hook=lambda code: self.scripts.records.pop(LOCAL_BASELINE_PACK.diagnostic_codes[1],None)
        result=self.service.execute_diagnostic_pack(LOCAL_BASELINE_PACK.code)
        self.assertEqual(result.failure_classification,'NOT_ELIGIBLE')
        self.assertEqual(len(self.gateway.calls),1)

    def test_lookup_cannot_substitute_another_approved_identity(self):
        code=LOCAL_BASELINE_PACK.diagnostic_codes[1]
        self.scripts.records[code]=record()
        self.assertEqual(self.service.execute_diagnostic(code).classification,'NOT_ELIGIBLE')
        self.assertEqual(self.scripts.prepares,[])
        self.assertEqual(self.gateway.calls,[])

    def test_single_pack_contention_and_exception_release(self):
        for initial in ('single','pack'):
            self.setUp()
            entered,release=threading.Event(),threading.Event()
            self.gateway.hook=lambda code: (entered.set(), release.wait(5))
            work=(lambda:self.service.execute_diagnostic_pack(LOCAL_BASELINE_PACK.code)) if initial=='pack' else (lambda:self.service.execute_diagnostic(LOCAL_BASELINE_PACK.diagnostic_codes[0]))
            thread=threading.Thread(target=work);thread.start()
            try:
                self.assertTrue(entered.wait(3))
                self.assertEqual(self.service.execute_diagnostic(LOCAL_BASELINE_PACK.diagnostic_codes[0]).classification,'EXECUTION_BUSY')
                self.assertEqual(self.service.execute_diagnostic_pack(LOCAL_BASELINE_PACK.code).failure_classification,'EXECUTION_BUSY')
            finally:
                release.set();thread.join(5)
            self.assertFalse(thread.is_alive())
        self.setUp()
        def broken(code): raise RuntimeError('synthetic programming error')
        self.gateway.hook=broken
        with self.assertRaises(RuntimeError): self.service.execute_diagnostic_pack(LOCAL_BASELINE_PACK.code)
        self.gateway.hook=None;self.gateway.calls=[]
        self.assertEqual(self.service.execute_diagnostic_pack(LOCAL_BASELINE_PACK.code).classification,'COMPLETED')

    def test_direct_execution_during_each_member_cannot_interleave(self):
        observed=[]
        def hook(code):
            observed.append(self.service.execute_diagnostic(code).classification)
        self.gateway.hook=hook
        self.assertEqual(self.service.execute_diagnostic_pack(LOCAL_BASELINE_PACK.code).classification,'COMPLETED')
        self.assertEqual(observed,['EXECUTION_BUSY']*3)

    def test_unknown_pack_and_immutable_policy(self):
        for code in ('unknown',None,[],LOCAL_BASELINE_PACK.diagnostic_codes):
            result=self.service.execute_diagnostic_pack(code)
            self.assertEqual(result.failure_classification,'NOT_ELIGIBLE')
            self.assertEqual(result.skipped_codes,LOCAL_BASELINE_PACK.diagnostic_codes)
        with self.assertRaises(TypeError): APPROVED_DIAGNOSTICS['unknown']=None
        self.assertEqual(self.gateway.calls,[])


class NewContractTests(unittest.TestCase):
    def test_shared_untrusted_envelopes(self):
        for code,validator in list(zip(LOCAL_BASELINE_PACK.diagnostic_codes[1:],(validate_network_snapshot,validate_services_snapshot))):
            value=output(code)
            invalid=[b'\xff',b'{}\n{}',b'banner',b'['*13+b']'*13,b'{"x":NaN}',b'{"x":Infinity}',b'{"x":1,"x":2}',b'x'*524291]
            for data in invalid:
                with self.subTest(code=code,data=data[:30]),self.assertRaises((ValueError,UnicodeError)):
                    validator(data,b'',0)
            for field,bad in (('schemaVersion',True),('operation','wrong'),('success',1),('status','FAIL'),('message','wrong'),('warnings',['unknown']),('errors',['unknown'])):
                changed=dict(value,**{field:bad})
                with self.subTest(field=field),self.assertRaises(ValueError):validator(json.dumps(changed).encode(),b'',0)
            for changed in (dict(value,extra=1),{k:v for k,v in value.items() if k!='data'}):
                with self.assertRaises(ValueError):validator(json.dumps(changed).encode(),b'',0)
            for stderr,exit_code in ((b'secret',0),(b'',1),(b'',True)):
                with self.assertRaises(ValueError):validator(json.dumps(value).encode(),stderr,exit_code)

    def test_network_typed_values_numeric_scopes_nulls_and_dns_order(self):
        code=LOCAL_BASELINE_PACK.diagnostic_codes[1]
        row=dict(interfaceIndex=0,interfaceDescription='Adapter',ipv4Addresses=['192.0.2.1'],ipv6Addresses=['fe80::1%12'],ipv4DefaultGateways=[],ipv6DefaultGateways=[],dnsServerAddresses=['2001:db8::2','192.0.2.1'],dhcpEnabled=False)
        value=output(code);value['data']['interfaces']=[row]
        def validate(v): return validate_network_snapshot(json.dumps(v).encode(),b'',0)
        self.assertIs(validate(value).data['interfaces'][0]['dhcpEnabled'],False)
        for field,bad in (('interfaceIndex',True),('interfaceIndex',2**32),('dhcpEnabled','false'),('ipv4Addresses',['::1']),('ipv6Addresses',['fe80::1%eth']),('dnsServerAddresses',['::1','0:0:0:0:0:0:0:1']),('ipv4Addresses',None)):
            value['data']['interfaces']=[dict(row,**{field:bad})]
            with self.subTest(field=field),self.assertRaises(ValueError):validate(value)
        warning=output(code,'WARNING');warning['warnings']=[NETWORK_WARNINGS[0],NETWORK_WARNINGS[1]]
        warning['data']['interfaces']=[dict(row,interfaceDescription=None,ipv4Addresses=None,ipv6Addresses=None)]
        self.assertIsNone(validate(warning).data['interfaces'][0]['ipv4Addresses'])

    def test_every_existing_network_fixture_crosses_python_validator(self):
        # Reuse unchanged standalone script cases with an additional strict boundary.
        from test_network_snapshot import NetworkSnapshotTests
        fixture=NetworkSnapshotTests()
        original=fixture.run_fixture
        def bridge(*args,**kwargs):
            value=original(*args,**kwargs)
            validate_network_snapshot(json.dumps(value,ensure_ascii=False).encode(),b'',int(not value['success']))
            return value
        fixture.run_fixture=bridge
        for name in unittest.defaultTestLoader.getTestCaseNames(NetworkSnapshotTests):
            with self.subTest(fixture=name):getattr(fixture,name)()

    def test_service_rows_order_duplicates_unicode_nulls_and_enum(self):
        code=LOCAL_BASELINE_PACK.diagnostic_codes[2]
        good=dict(name='A',displayName='Service',state='Stopped',startupMode='Auto')
        value=output(code);value['data']['services']=[good]
        def validate(v):return validate_services_snapshot(json.dumps(v).encode(),b'',0)
        self.assertEqual(validate(value).status,'PASS')
        for field,bad in (('name',''),('name','x'*257),('name','\ud800'),('displayName','\u202eunsafe'),('state','Unknown'),('startupMode','Automatic'),('displayName',None)):
            value['data']['services']=[dict(good,**{field:bad})]
            with self.subTest(field=field),self.assertRaises((ValueError,UnicodeError)):validate(value)
        for rows in ([good,good],[dict(good,name='B'),good],[good,dict(good,name='a')],[good]*513):
            value['data']['services']=rows
            with self.assertRaises(ValueError):validate(value)
