"""PowerShell fixture-to-production-validator contract tests, never service control."""
import base64
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from f7hub.services.powershell_service import validate_services_snapshot

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'PowerShell/Diagnostics/Get-ServicesSnapshot.ps1'
PWSH = shutil.which('pwsh')


def service(name='Example', **changes):
    value = dict(Name=name, DisplayName='Example service', State='Stopped', StartMode='Auto')
    value.update(changes)
    return value


@unittest.skipUnless(PWSH, 'PowerShell 7 required')
class ServicesSnapshotTests(unittest.TestCase):
    def fixture(self, rows=None, *, body=None, modify='', prefix=''):
        if body is None:
            payload = base64.b64encode(json.dumps(rows).encode()).decode()
            body = "$rows=@([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('" + payload + "')) | ConvertFrom-Json); " + modify + '; $rows'
        command = prefix + "function Get-CimInstance { param($Namespace,$ClassName,$Property,$OperationTimeoutSec,$ErrorAction) "
        command += "if ($Namespace -ne 'root/cimv2' -or $ClassName -ne 'Win32_Service' -or ($Property -join ',') -ne 'Name,DisplayName,State,StartMode' -or $OperationTimeoutSec -ne 20 -or $ErrorAction -ne 'Stop') { throw 'Bad query' }; "
        command += body + " }; . '" + str(SCRIPT).replace("'", "''") + "'; exit $LASTEXITCODE"
        with tempfile.TemporaryDirectory() as temporary:
            fixture = Path(temporary)/'fixture.ps1'
            fixture.write_text(command, encoding='utf-8')
            before = tuple(Path(temporary).iterdir())
            process = subprocess.run([PWSH, '-NoProfile', '-NonInteractive', '-File', str(fixture)],
                                     cwd=temporary, capture_output=True, timeout=30)
            self.assertEqual(tuple(Path(temporary).iterdir()), before)
        self.assertEqual(process.stderr, b'')
        self.assertLessEqual(len(process.stdout), 524290)
        validated = validate_services_snapshot(process.stdout, process.stderr, process.returncode)
        self.assertNotIn('private fixture error', process.stdout.decode())
        return validated

    def test_stopped_auto_is_not_a_fault_and_empty_is_valid(self):
        self.assertEqual(self.fixture([service()]).status, 'PASS')
        self.assertEqual(self.fixture([]).data['services'], [])

    def test_every_supported_state_and_startup_mode(self):
        states = ['Running','Stopped','Start Pending','Stop Pending','Continue Pending','Pause Pending','Paused']
        modes = ['Auto','Manual','Disabled','Boot','System']
        rows = [service(str(i), State=state, StartMode=mode) for i,(state,mode) in enumerate((s,m) for s in states for m in modes)]
        self.assertEqual(self.fixture(rows).status, 'PASS')

    def test_optional_absent_unknown_invalid_and_throwing_values(self):
        result = self.fixture([service(DisplayName=None, State='Unknown', StartMode='Unknown')])
        self.assertEqual(result.status, 'WARNING')
        self.assertEqual(result.data['services'][0], dict(name='Example', displayName=None, state=None, startupMode=None))
        self.assertEqual(len(result.warnings), 1)
        for row in [dict(Name='Example'), service(DisplayName=1, State=True, StartMode=False), service(DisplayName='\u202eunsafe')]:
            self.assertEqual(self.fixture([row]).status, 'WARNING')
        self.assertEqual(self.fixture([service()], modify="$rows[0].PSObject.Properties.Remove('DisplayName'); $rows[0] | Add-Member ScriptProperty DisplayName { throw 'private fixture error' }").status, 'WARNING')

    def test_required_identity_and_partial_query_failures(self):
        for rows in ([service(None)], [service(' ')], [service('x'*257)], [service('x\n')],
                     [service('one'), service('ONE')]):
            with self.subTest(rows=repr(rows)):
                result = self.fixture(rows)
                self.assertEqual(result.status, 'ERROR')
                self.assertEqual(result.data['services'], [])
        self.assertEqual(self.fixture(body="[pscustomobject]@{Name='partial'}; throw 'private fixture error'").status, 'ERROR')
        # ConvertFrom-Json replaces an unpaired surrogate: inject the actual .NET
        # string directly so the fixture reaches the intended producer boundary.
        self.assertEqual(self.fixture(body="[pscustomobject]@{Name=('x'+[char]0xD800);DisplayName='Service';State='Running';StartMode='Auto'}").status, 'ERROR')

    def test_bounds_surrogates_and_invalid_identity_beyond_cap(self):
        rows = [service(f'{i:04d}', DisplayName='x'*255+'\U0001f600') for i in reversed(range(513))]
        result = self.fixture(rows)
        self.assertEqual(len(result.data['services']), 512)
        self.assertEqual(result.data['services'][0]['name'], '0000')
        self.assertEqual(result.data['services'][0]['displayName'], 'x'*255)
        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(self.fixture(rows+[service(None)]).status, 'ERROR')

    def test_non_ascii_ordinal_order_and_valid_supplementary_text(self):
        result = self.fixture([service(name) for name in ('é', 'Z', 'a', '\U0001f600')])
        self.assertEqual([r['name'] for r in result.data['services']], ['Z','a','é','\U0001f600'])

    def test_output_size_fallback(self):
        # Worst-case valid multibyte name/display inventory exceeds the JSON cap.
        body = "0..511 | ForEach-Object { [pscustomobject]@{Name=('{0:0000}' -f $_)+('界'*252); DisplayName=('界'*256); State='Running'; StartMode='Auto'} }"
        result = self.fixture(body=body)
        self.assertEqual(result.status, 'ERROR')
        self.assertEqual(result.errors, ('Services snapshot exceeded its output size limit.',))

    def test_ast_only_read_commands_and_no_parameters(self):
        command = "$t=$null;$e=$null;$a=[Management.Automation.Language.Parser]::ParseFile('"+str(SCRIPT).replace("'","''")+"',[ref]$t,[ref]$e); if($e.Count -or $a.ParamBlock){exit 1}; $a.FindAll({param($n)$n -is [Management.Automation.Language.CommandAst]},$true)|ForEach-Object {$_.GetCommandName()}"
        result = subprocess.run([PWSH,'-NoProfile','-NonInteractive','-Command',command],capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0)
        self.assertEqual(result.stderr,'')
        self.assertEqual(set(result.stdout.splitlines()), {'Read-ServicesSnapshotProperty','Convert-ServicesSnapshotText','Get-CimInstance','Select-Object','ConvertTo-Json'})
