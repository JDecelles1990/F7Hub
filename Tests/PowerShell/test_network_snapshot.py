"""Deterministic standalone contract checks; no application execution gateway."""
from __future__ import annotations

import base64
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / 'PowerShell/Diagnostics/Get-NetworkSnapshot.ps1'
PWSH = shutil.which('pwsh')
FIELDS = {'interfaceIndex', 'interfaceDescription', 'ipv4Addresses', 'ipv6Addresses',
          'ipv4DefaultGateways', 'ipv6DefaultGateways', 'dnsServerAddresses', 'dhcpEnabled'}

def interface(index=1, **changes):
    row = dict(InterfaceIndex=index, Description='Synthetic adapter',
               IPAddress=['192.0.2.20', '2001:db8::20'], DefaultIPGateway=['192.0.2.1', '2001:db8::1'],
               DNSServerSearchOrder=['192.0.2.53', '2001:db8::53'], DHCPEnabled=False)
    row.update(changes)
    return row

@unittest.skipUnless(PWSH, 'PowerShell 7 is required')
class NetworkSnapshotTests(unittest.TestCase):
    def run_fixture(self, rows=None, *, body=None, modify=''):
        if body is None:
            payload = base64.b64encode(json.dumps(rows).encode()).decode()
            body = ("$rows=@([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('" + payload +
                    "')) | ConvertFrom-Json); " + modify + '; $rows')
        command = ("function Get-CimInstance { param($Namespace,$ClassName,$Filter,$Property,$OperationTimeoutSec,$ErrorAction) "
                   "if ($Namespace -ne 'root/cimv2' -or $ClassName -ne 'Win32_NetworkAdapterConfiguration' "
                   "-or $Filter -ne 'IPEnabled=True' -or $OperationTimeoutSec -ne 20 -or $ErrorAction -ne 'Stop' "
                   "-or ($Property -join ',') -ne 'InterfaceIndex,Description,IPAddress,DefaultIPGateway,DNSServerSearchOrder,DHCPEnabled') "
                   "{ throw 'unexpected source contract' }; " + body + " }; . '" + str(SCRIPT).replace("'", "''") + "'; exit $LASTEXITCODE")
        with tempfile.TemporaryDirectory() as temporary:
            cwd = Path(temporary)
            # Large synthetic inventories exceed Windows' command-line limit.
            fixture = cwd / 'fixture.ps1'
            fixture.write_text(command, encoding='utf-8')
            before = tuple(cwd.iterdir())
            process = subprocess.run([PWSH, '-NoProfile', '-NonInteractive', '-File', str(fixture)],
                                     cwd=cwd, capture_output=True, timeout=30)
            self.assertEqual(tuple(cwd.iterdir()), before)
        self.assertEqual(process.stderr, b'')
        self.assertLessEqual(len(process.stdout), 524288)
        text = process.stdout.decode('utf-8').strip()
        value, end = json.JSONDecoder().raw_decode(text)
        self.assertEqual(text[end:], '')
        self.assertEqual(set(value), {'schemaVersion', 'operation', 'success', 'status', 'message', 'data', 'warnings', 'errors'})
        self.assertEqual(value['schemaVersion'], 1)
        self.assertIs(type(value['schemaVersion']), int)
        self.assertEqual(value['operation'], 'Get-NetworkSnapshot')
        self.assertEqual(set(value['data']), {'computerName', 'interfaces'})
        self.assertIsInstance(value['data']['interfaces'], list)
        self.assertIs(type(value['success']), bool)
        self.assertIsInstance(value['warnings'], list)
        self.assertIsInstance(value['errors'], list)
        self.assertNotIn('private synthetic failure', text)
        self.assertEqual(process.returncode, 0 if value['success'] else 1)
        for row in value['data']['interfaces']:
            self.assertEqual(set(row), FIELDS)
        return value

    def test_parser_and_read_only_command_surface(self):
        command = ("$tokens=$null; $errors=$null; $ast=[Management.Automation.Language.Parser]::ParseFile('" +
                   str(SCRIPT).replace("'", "''") + "',[ref]$tokens,[ref]$errors); "
                   "if ($errors.Count) { exit 1 }; "
                   "$ast.FindAll({param($n) $n -is [Management.Automation.Language.CommandAst]},$true) "
                   "| ForEach-Object { $_.GetCommandName() }")
        process = subprocess.run([PWSH, '-NoProfile', '-NonInteractive', '-Command', command],
                                 capture_output=True, text=True, timeout=15)
        self.assertEqual(process.returncode, 0)
        self.assertEqual(process.stderr, '')
        self.assertEqual(set(process.stdout.splitlines()), {
            'Read-NetworkSnapshotProperty', 'Convert-NetworkSnapshotText', 'Convert-NetworkSnapshotAddresses',
            'Get-CimInstance', 'Sort-Object', 'Select-Object', 'ConvertTo-Json'})

    def test_dual_stack_success_and_numeric_interface_order(self):
        value = self.run_fixture([interface(11), interface(2)])
        self.assertEqual(value['status'], 'PASS')
        self.assertEqual(value['warnings'], [])
        self.assertEqual(value['errors'], [])
        self.assertEqual([r['interfaceIndex'] for r in value['data']['interfaces']], [2, 11])
        row = value['data']['interfaces'][0]
        self.assertEqual(row['ipv4Addresses'], ['192.0.2.20'])
        self.assertEqual(row['ipv6Addresses'], ['2001:db8::20'])
        self.assertIs(row['dhcpEnabled'], False)

    def test_zero_interfaces_is_successful_empty_inventory(self):
        value = self.run_fixture([])
        self.assertEqual(value['status'], 'PASS')
        self.assertEqual(value['data']['interfaces'], [])

    def test_query_failure_discards_partially_emitted_inventory(self):
        value = self.run_fixture(body="[pscustomobject]@{InterfaceIndex=1}; throw 'private synthetic failure'")
        self.assertEqual(value['status'], 'ERROR')
        self.assertEqual(value['data']['interfaces'], [])
        self.assertFalse(value['success'])
        self.assertEqual(value['warnings'], [])
        self.assertEqual(value['errors'], ['Required local network configuration is unavailable.'])

    def test_invalid_and_duplicate_indices_fail_required_inventory(self):
        for rows in ([interface(None)], [interface(-1)], [interface(2**32)], [interface(True)],
                     [interface('1')], [interface(1.5)], [interface(2), interface(2)], [None]):
            with self.subTest(rows=rows):
                value = self.run_fixture(rows)
                self.assertEqual(value['status'], 'ERROR')
                self.assertEqual(value['data']['interfaces'], [])

    def test_optional_nulls_remain_null_with_bounded_warnings(self):
        value = self.run_fixture([interface(Description=None, IPAddress=None, DefaultIPGateway=None,
                                           DNSServerSearchOrder=None, DHCPEnabled=None)] * 1)
        row = value['data']['interfaces'][0]
        self.assertEqual(value['status'], 'WARNING')
        for key in FIELDS - {'interfaceIndex'}:
            self.assertIsNone(row[key], key)
        self.assertEqual(len(value['warnings']), 4)

    def test_missing_properties_and_throwing_optional_getter(self):
        value = self.run_fixture([{'InterfaceIndex': 1}])
        self.assertEqual(value['status'], 'WARNING')
        value = self.run_fixture([interface()], modify=(
            "$rows[0].PSObject.Properties.Remove('Description'); "
            "$rows[0] | Add-Member ScriptProperty Description { throw 'private synthetic failure' }"))
        self.assertEqual(value['status'], 'WARNING')
        self.assertIsNone(value['data']['interfaces'][0]['interfaceDescription'])

    def test_explicit_empty_arrays_and_false_are_not_unavailable(self):
        value = self.run_fixture([interface(IPAddress=[], DefaultIPGateway=[], DNSServerSearchOrder=[])])
        self.assertEqual(value['status'], 'PASS')
        row = value['data']['interfaces'][0]
        for key in ('ipv4Addresses', 'ipv6Addresses', 'ipv4DefaultGateways', 'ipv6DefaultGateways', 'dnsServerAddresses'):
            self.assertEqual(row[key], [])
        self.assertIs(row['dhcpEnabled'], False)

    def test_malformed_optional_values_do_not_become_fake_defaults(self):
        for field, invalid in [('IPAddress', ['bad address']), ('IPAddress', '192.0.2.1'),
                               ('DefaultIPGateway', [1]), ('DNSServerSearchOrder', [None]),
                               ('Description', 1), ('DHCPEnabled', 'false')]:
            with self.subTest(field=field):
                value = self.run_fixture([interface(**{field: invalid})])
                self.assertEqual(value['status'], 'WARNING')
                target = {'IPAddress': 'ipv4Addresses', 'DefaultIPGateway': 'ipv4DefaultGateways',
                          'DNSServerSearchOrder': 'dnsServerAddresses', 'Description': 'interfaceDescription',
                          'DHCPEnabled': 'dhcpEnabled'}[field]
                self.assertIsNone(value['data']['interfaces'][0][target])

    def test_normalization_sorting_deduplication_and_dns_order(self):
        addresses = ['192.0.2.2', '2001:0DB8:0000::2', '192.0.2.10', '2001:db8::2', 'fe80::1%12']
        value = self.run_fixture([interface(IPAddress=addresses, DefaultIPGateway=list(reversed(addresses)),
                                           DNSServerSearchOrder=['192.0.2.2', '192.0.2.10', '192.0.2.2'])])
        row = value['data']['interfaces'][0]
        self.assertEqual(row['ipv4Addresses'], ['192.0.2.10', '192.0.2.2'])
        self.assertEqual(row['ipv6Addresses'], ['2001:db8::2', 'fe80::1%12'])
        self.assertEqual(row['ipv4DefaultGateways'], row['ipv4Addresses'])
        self.assertEqual(row['dnsServerAddresses'], ['192.0.2.2', '192.0.2.10'])
        other = self.run_fixture([interface(IPAddress=list(reversed(addresses)), DefaultIPGateway=addresses,
                                           DNSServerSearchOrder=['192.0.2.2', '192.0.2.10', '192.0.2.2'])])
        self.assertEqual(value, other)

    def test_all_bounds_and_deterministic_truncation(self):
        addresses = [f'192.0.2.{i}' for i in range(1, 21)] + [f'2001:db8::{i:x}' for i in range(1, 21)]
        rows = [interface(i, Description='x' * 300, IPAddress=addresses, DefaultIPGateway=addresses,
                          DNSServerSearchOrder=addresses) for i in reversed(range(70))]
        value = self.run_fixture(rows)
        self.assertEqual(value['status'], 'WARNING')
        self.assertEqual(len(value['data']['interfaces']), 64)
        self.assertEqual([r['interfaceIndex'] for r in value['data']['interfaces']], list(range(64)))
        for row in value['data']['interfaces']:
            self.assertEqual(len(row['interfaceDescription']), 256)
            for key, limit in [('ipv4Addresses', 16), ('ipv6Addresses', 16), ('ipv4DefaultGateways', 8),
                               ('ipv6DefaultGateways', 8), ('dnsServerAddresses', 16)]:
                self.assertEqual(len(row[key]), limit)
        self.assertEqual(value['warnings'], ['Network snapshot output was limited to documented bounds.'])

    def test_invalid_index_beyond_output_cap_still_fails(self):
        value = self.run_fixture([interface(i) for i in range(64)] + [interface(None)])
        self.assertEqual(value['status'], 'ERROR')
        self.assertEqual(value['data']['interfaces'], [])

    def test_non_bmp_description_boundary_is_valid_utf8(self):
        value = self.run_fixture([interface(Description='x' * 255 + '\U0001f600')])
        self.assertEqual(value['status'], 'WARNING')
        self.assertEqual(value['data']['interfaces'][0]['interfaceDescription'], 'x' * 255)

if __name__ == '__main__':
    unittest.main()
