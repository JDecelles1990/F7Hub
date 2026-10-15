"""Synthetic contract/security tests; never read the Windows Clipboard."""

import ast
from copy import deepcopy
from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import re
import subprocess
import sys
import traceback
import unittest

from f7hub.infrastructure import clipboard_snapshot_protocol as p


ROOT = Path(__file__).resolve().parents[2]
UUIDS = [f'{i:08x}-0000-4000-8000-000000000000' for i in range(1, 12)]
NOW = '2026-10-14T23:00:00.000Z'
SYNTHETIC_SECRET = 'SYNTHETIC_SECRET_SENTINEL_DO_NOT_LOG'
BINDING = p.SnapshotBinding(UUIDS[1], UUIDS[2])


def request_document():
    # Hand-authored producer fixture, independent of the module encoder.
    return {'contract': 'clipboard.snapshot_read', 'schema_version': '1.0',
            'message_class': 'COMMAND', 'message_id': UUIDS[0], 'created_at': NOW,
            'producer': {'component': 'f7hub.clipboard'},
            'payload': {'operation_id': UUIDS[3], 'admission_generation': UUIDS[1],
                        'producer_binding': UUIDS[2]}}


def result_document(text='Synthetic ordinary text', status='SUCCESS'):
    value = request_document()
    value.update(contract='clipboard.snapshot_read_result', message_class='RESULT',
                 message_id=UUIDS[4], correlation_id=UUIDS[0],
                 producer={'component': 'ahk.clipboard'})
    value['payload']['status'] = status
    if status == 'SUCCESS':
        value['payload'].update(observed_at=NOW, format='text/plain', text=text)
    return value


def error_document():
    value = result_document()
    value.update(contract='contract.error', message_class='ERROR',
                 payload={'code': 'TIMEOUT', 'message': 'The snapshot request failed.'})
    return value


def wire(value, ascii=False):
    return json.dumps(value, ensure_ascii=ascii, separators=(',', ':')).encode('utf-8')


def schema_accepts(value, spec, schema):
    """Fixture-only evaluator for the small keyword subset in this local schema.

    Not a JSON Schema implementation or runtime dependency. Assert the keyword
    subset separately; byte budgets, correlation and real dates are Python gates.
    """
    if '$ref' in spec:
        return schema_accepts(value, schema['$defs'][spec['$ref'].split('/')[-1]], schema)
    if 'oneOf' in spec and sum(schema_accepts(value, part, schema) for part in spec['oneOf']) != 1:
        return False
    if 'const' in spec and (type(value) is not type(spec['const']) or value != spec['const']):
        return False
    if 'enum' in spec and value not in spec['enum']:
        return False
    kind = spec.get('type')
    if kind == 'object':
        if type(value) is not dict or not set(spec['required']) <= value.keys():
            return False
        if spec.get('additionalProperties') is False and not value.keys() <= spec['properties'].keys():
            return False
        return all(schema_accepts(item, spec['properties'][key], schema) for key, item in value.items())
    if kind == 'string':
        return (type(value) is str and spec.get('minLength', 0) <= len(value) <= spec.get('maxLength', sys.maxsize)
                and ('pattern' not in spec or re.search(spec['pattern'], value) is not None))
    if kind == 'boolean':
        return type(value) is bool
    return True


class SnapshotProtocolTests(unittest.TestCase):
    def setUp(self):
        self.request = p.decode_request(wire(request_document()), binding=BINDING)

    def result(self, value):
        return p.decode_result(wire(value), request=self.request, binding=BINDING)

    def reject(self, raw, kind='result', binding=BINDING):
        with self.assertRaises(p.ProtocolError) as caught:
            if kind == 'request':
                p.decode_request(raw, binding=binding)
            elif kind == 'error':
                p.decode_error(raw, request=self.request, binding=binding)
            else:
                p.decode_result(raw, request=self.request, binding=binding)
        error = caught.exception
        self.assertNotIn(SYNTHETIC_SECRET, str(error))
        self.assertNotIn(SYNTHETIC_SECRET, repr(error))
        self.assertIsNone(error.__context__)
        return error

    def test_request_and_result_roundtrip_and_immutable(self):
        result = self.result(result_document())
        self.assertEqual(json.loads(p.encode(self.request)), request_document())
        self.assertEqual(json.loads(p.encode(result)), result_document())
        with self.assertRaises(FrozenInstanceError):
            result.text = 'changed'
        with self.assertRaises(FrozenInstanceError):
            result.binding.producer_binding = UUIDS[9]

    def test_all_content_free_statuses(self):
        for status in p.STATUSES - {'SUCCESS'}:
            with self.subTest(status=status):
                result = self.result(result_document(status=status))
                self.assertIsNone(result.text)
                self.assertEqual(json.loads(p.encode(result)), result_document(status=status))

    def test_error_roundtrip_unknown_retryability_and_explicit_false(self):
        for retryable in (None, False, True):
            value = error_document()
            if retryable is not None:
                value['payload']['retryable'] = retryable
            error = p.decode_error(wire(value), request=self.request, binding=BINDING)
            self.assertIs(error.retryable, retryable)
            self.assertEqual(json.loads(p.encode(error)), value)

    def test_exact_profile_class_version_and_component(self):
        for field, bads in {'contract': ['clipboard.capture', 'clipboard.snapshot_read'],
                            'schema_version': [1, True, '1.1', '01.0', '1.0.0'],
                            'message_class': ['result', 'COMMAND', None]}.items():
            for bad in bads:
                value = result_document()
                value[field] = bad
                with self.subTest(field=field, bad=bad):
                    self.reject(wire(value))
        value = result_document()
        value['producer']['component'] = 'f7hub.clipboard'
        self.reject(wire(value))

    def test_unknown_and_missing_fields_at_each_layer(self):
        for shape in ('root', 'producer', 'payload'):
            value = result_document()
            target = value if shape == 'root' else value[shape]
            target['extra'] = SYNTHETIC_SECRET
            self.reject(wire(value))
        for key in result_document():
            value = result_document()
            del value[key]
            self.reject(wire(value))
        for key in result_document()['payload']:
            value = result_document()
            del value['payload'][key]
            self.reject(wire(value))

    def test_uuid_semantics_across_header_and_binding(self):
        bads = (True, 1, None, '', UUIDS[0].upper().replace('00000001', 'ABCDEF01'),
                '00000001-0000-1000-8000-000000000000',
                '00000001-0000-4000-7000-000000000000', UUIDS[0] + '\n')
        for key in ('message_id', 'correlation_id', 'operation_id', 'admission_generation', 'producer_binding'):
            for bad in bads:
                value = result_document()
                target = value if key in value else value['payload']
                target[key] = bad
                with self.subTest(key=key, bad=bad):
                    self.reject(wire(value))

    def test_timestamp_real_calendar_precision_and_utc(self):
        bads = ('2026-02-30T00:00:00.000Z', '2026-10-14T24:00:00.000Z',
                '2026-10-14T00:00:60.000Z', '2026-10-14T00:00:00Z',
                '2026-10-14T00:00:00.000+00:00', '0000-01-01T00:00:00.000Z', None)
        for key in ('created_at', 'observed_at'):
            for bad in bads:
                value = result_document()
                (value if key == 'created_at' else value['payload'])[key] = bad
                self.reject(wire(value))

    def test_correlation_fresh_reply_and_operation(self):
        for field in ('message_id', 'correlation_id', 'operation_id'):
            value = result_document()
            if field == 'message_id':
                value[field] = self.request.header.message_id
            elif field == 'correlation_id':
                value[field] = UUIDS[9]
            else:
                value['payload'][field] = UUIDS[9]
            self.reject(wire(value))

    def test_binding_and_generation_consistency_all_reply_types(self):
        for field in ('admission_generation', 'producer_binding'):
            value = result_document()
            value['payload'][field] = UUIDS[9]
            self.reject(wire(value))
            request = request_document()
            request['payload'][field] = UUIDS[9]
            self.reject(wire(request), 'request')
        revoked = p.SnapshotBinding(UUIDS[8], UUIDS[9])
        self.reject(wire(result_document()), binding=revoked)
        self.reject(wire(error_document()), 'error', revoked)

    def test_no_raw_body_in_any_non_success_status(self):
        for status in p.STATUSES - {'SUCCESS'}:
            for field, content in (('text', SYNTHETIC_SECRET), ('format', 'text/plain'), ('observed_at', NOW)):
                value = result_document(status=status)
                value['payload'][field] = content
                self.reject(wire(value))

    def test_success_requires_nonempty_supported_text_and_exact_status(self):
        for key, bads in {'status': ['success', 'PERMITTED', '', None, True],
                          'format': ['text/html', None, True], 'text': ['', None, True, 1, []]}.items():
            for bad in bads:
                value = result_document()
                value['payload'][key] = bad
                self.reject(wire(value))

    def test_unicode_preserved_without_normalization(self):
        text = '  e\u0301 é 😀\t\n\r[end]  '
        result = self.result(result_document(text))
        self.assertEqual(result.text, text)
        self.assertEqual(self.result(json.loads(p.encode(result))).text, text)

    def test_invalid_utf8_bom_and_surrogate_escapes(self):
        self.reject(b'\xef\xbb\xbf' + wire(result_document()))
        self.reject(b'\xff' + wire(result_document()))
        for text in ('\ud800', '\udfff', '\ud800X', SYNTHETIC_SECRET + '\ud800'):
            self.reject(wire(result_document(text), ascii=True))

    def test_prohibited_controls_and_allowed_text_controls(self):
        for number in list(range(32)) + list(range(127, 160)):
            text = chr(number)
            if text in '\t\n\r':
                self.assertEqual(self.result(result_document(text)).text, text)
            else:
                self.reject(wire(result_document(text)))

    def test_duplicate_keys_at_root_and_nested_levels(self):
        raw = wire(result_document())
        for old, new in ((b'"schema_version":"1.0"', b'"schema_version":"1.0","schema_version":"1.0"'),
                         (b'"status":"SUCCESS"', b'"status":"SUCCESS","status":"SUCCESS"'),
                         (b'"component":"ahk.clipboard"', b'"component":"ahk.clipboard","component":"ahk.clipboard"')):
            self.reject(raw.replace(old, new))

    def test_malformed_and_nonfinite_documents_are_content_free(self):
        for raw in (b'', b'null', b'[]', b'1', b'{', b'{}{}', wire(result_document()) + b'garbage',
                    b'{"text":"' + SYNTHETIC_SECRET.encode() + b'",}', b'{"x":NaN}',
                    b'{"x":Infinity}', b'{"x":1.1}', b'{"x":1e1}', b'{"x":' + b'9' * 1000 + b'}'):
            error = self.reject(raw)
            self.assertNotIn(SYNTHETIC_SECRET, ''.join(traceback.format_exception(error)))

    def test_bounded_nesting_and_members_and_wrong_container_types(self):
        self.reject(b'{"x":' * 100 + b'0' + b'}' * 100)
        self.reject(wire({str(i): i for i in range(p.MAX_MEMBERS + 1)}))
        for location in ('producer', 'payload'):
            for bad in (None, [], 'text', 1):
                value = result_document()
                value[location] = bad
                self.reject(wire(value))

    def test_bytes_only_no_implicit_conversion(self):
        for raw in (wire(result_document()).decode(), bytearray(wire(result_document())), memoryview(b'{}'), None):
            self.reject(raw)

    def test_utf8_text_boundary_ascii_and_multibyte(self):
        for text in ('a' * 65535, 'a' * 65536, '😀' * 16384):
            result = self.result(result_document(text))
            self.assertEqual(result.text, text)
            self.assertLessEqual(len(p.encode(result)), p.MAX_RESULT_BYTES)
        for text in ('a' * 65537, '😀' * 16384 + 'a'):
            self.reject(wire(result_document(text)))

    def test_complete_result_document_including_whitespace_boundary(self):
        raw = wire(result_document())
        for size in (p.MAX_RESULT_BYTES - 1, p.MAX_RESULT_BYTES):
            padded = raw + b' ' * (size - len(raw))
            self.assertEqual(p.decode_result(padded, request=self.request, binding=BINDING).text,
                             'Synthetic ordinary text')
        self.reject(raw + b' ' * (p.MAX_RESULT_BYTES + 1 - len(raw)))

    def test_ordinary_request_and_error_document_boundaries(self):
        for kind, value in (('request', request_document()), ('error', error_document())):
            raw = wire(value)
            for size in (p.MAX_ORDINARY_BYTES - 1, p.MAX_ORDINARY_BYTES):
                padded = raw + b' ' * (size - len(raw))
                if kind == 'request':
                    p.decode_request(padded, binding=BINDING)
                else:
                    p.decode_error(padded, request=self.request, binding=BINDING)
            self.reject(raw + b' ' * (p.MAX_ORDINARY_BYTES + 1 - len(raw)), kind)

    def test_serialization_expansion_rejected_never_truncated(self):
        # Fits text cap, exceeds full document after escaping; construction is
        # structurally valid but outgoing document admission must fail.
        value = result_document('"' * 65536)
        self.reject(wire(value))
        result = p.SnapshotResult(p.SnapshotHeader(p.RESULT_CONTRACT, 'RESULT', UUIDS[4], NOW,
                                                  p.REPLY_COMPONENT, UUIDS[0]), UUIDS[3], BINDING,
                                  'SUCCESS', NOW, value['payload']['text'])
        with self.assertRaises(p.ProtocolError):
            p.encode(result)
        smaller = self.result(result_document('"' * 65000))
        self.assertEqual(json.loads(p.encode(smaller))['payload']['text'], '"' * 65000)

    def test_sensitive_text_hidden_from_representations_and_errors(self):
        result = self.result(result_document(SYNTHETIC_SECRET))
        self.assertNotIn(SYNTHETIC_SECRET, repr(result))
        self.assertNotIn(SYNTHETIC_SECRET, str(result))
        # Structural validity is deliberately not a privacy verdict.
        self.assertEqual(result.text, SYNTHETIC_SECRET)
        for field in ('message', 'code', 'details', 'text'):
            value = error_document()
            value['payload'][field] = SYNTHETIC_SECRET
            self.reject(wire(value), 'error')

    def test_error_types_codes_and_correlation(self):
        for key, bads in {'retryable': [None, 0, 1, 'true'], 'code': ['TIMEOUT\n', 'UNKNOWN', True]}.items():
            for bad in bads:
                value = error_document()
                value['payload'][key] = bad
                self.reject(wire(value), 'error')
        value = error_document()
        value['correlation_id'] = UUIDS[9]
        self.reject(wire(value), 'error')
        value['correlation_id'] = value['message_id']
        self.reject(wire(value), 'error')

    def test_public_dto_constructors_reject_invalid_shapes(self):
        with self.assertRaises(p.ProtocolError):
            p.SnapshotBinding(True, UUIDS[2])
        with self.assertRaises(p.ProtocolError):
            p.SnapshotRequest(self.request.header, 'invalid', BINDING)
        header = p.SnapshotHeader(p.RESULT_CONTRACT, 'RESULT', UUIDS[4], NOW, p.REPLY_COMPONENT, UUIDS[0])
        with self.assertRaises(p.ProtocolError):
            p.SnapshotResult(header, UUIDS[3], BINDING, 'DENIED', text=SYNTHETIC_SECRET)
        with self.assertRaises(p.ProtocolError):
            p.encode({'text': SYNTHETIC_SECRET})

    def test_schema_structural_fixture_parity_and_declared_semantic_limits(self):
        schema = json.loads((ROOT / 'Config/JSON/clipboard_snapshot_v1.schema.json').read_text(encoding='utf-8'))
        self.assertEqual(schema['$schema'], 'https://json-schema.org/draft/2020-12/schema')
        self.assertEqual(schema['x-max-result-document-bytes'], p.MAX_RESULT_BYTES)
        self.assertEqual(schema['x-max-ordinary-document-bytes'], p.MAX_ORDINARY_BYTES)
        self.assertEqual(schema['x-max-depth'], p.MAX_DEPTH)
        self.assertEqual(schema['x-max-object-members'], p.MAX_MEMBERS)
        self.assertEqual(schema['x-max-nodes'], p.MAX_NODES)
        self.assertEqual(schema['x-future-snapshot-lifetime-seconds'], p.FUTURE_SNAPSHOT_LIFETIME_SECONDS)
        valid = [request_document(), result_document(), error_document()]
        valid += [result_document(status=s) for s in p.STATUSES - {'SUCCESS'}]
        for value in valid:
            self.assertTrue(schema_accepts(value, schema, schema))
        invalid = []
        for field in ('schema_version', 'message_class', 'contract'):
            value = result_document()
            value[field] = 'INVALID'
            invalid.append(value)
        for status in p.STATUSES - {'SUCCESS'}:
            value = result_document(status=status)
            value['payload']['text'] = SYNTHETIC_SECRET
            invalid.append(value)
        for text in ('', '\x00', '\ud800'):
            invalid.append(result_document(text))
        for value in invalid:
            self.assertFalse(schema_accepts(value, schema, schema))
            self.reject(wire(value, ascii=True))
        # Schema annotation limitations are explicit; Python rejects these.
        value = result_document()
        value['payload']['observed_at'] = '2026-02-30T00:00:00.000Z'
        self.assertTrue(schema_accepts(value, schema, schema))
        self.reject(wire(value))
        value = result_document('😀' * 16385)
        self.assertTrue(schema_accepts(value, schema, schema))
        self.reject(wire(value))

    def test_schema_has_only_local_refs_and_fixture_evaluator_supported_keywords(self):
        schema = json.loads((ROOT / 'Config/JSON/clipboard_snapshot_v1.schema.json').read_text(encoding='utf-8'))
        allowed = {'$schema', '$defs', '$ref', '$comment', 'title', 'description', 'type', 'properties',
                   'required', 'additionalProperties', 'const', 'enum', 'oneOf', 'pattern', 'format',
                   'minLength', 'maxLength'}
        def inspect(spec):
            self.assertFalse(set(spec) - allowed - {k for k in spec if k.startswith('x-')})
            if '$ref' in spec:
                self.assertTrue(spec['$ref'].startswith('#/$defs/'))
                self.assertIn(spec['$ref'].split('/')[-1], schema['$defs'])
            for key in ('$defs', 'properties'):
                for part in spec.get(key, {}).values():
                    inspect(part)
            for part in spec.get('oneOf', []):
                inspect(part)
        inspect(schema)

    def test_dependency_direction_and_import_use_are_inert_in_clean_process(self):
        path = ROOT / 'Python/f7hub/infrastructure/clipboard_snapshot_protocol.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        imports = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        imports.update(a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names)
        self.assertEqual(imports, {'dataclasses', 'datetime', 'json', 're'})
        script = '''
import sys, builtins
original = builtins.__import__
forbidden = ('PySide6', 'sqlite3', 'socket', 'ctypes', 'subprocess', 'logging',
             'f7hub.services', 'f7hub.domain', 'f7hub.repositories', 'f7hub.gui', 'f7hub.app')
def guarded(name, *args, **kwargs):
    if any(name == x or name.startswith(x + '.') for x in forbidden):
        raise AssertionError('Forbidden dependency')
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
def audit(event, args):
    if event.startswith(('socket.', 'sqlite3.', 'subprocess.', 'os.system', 'os.spawn')):
        raise AssertionError('Forbidden effect')
sys.addaudithook(audit)
from f7hub.infrastructure import clipboard_snapshot_protocol as p
binding = p.SnapshotBinding('00000002-0000-4000-8000-000000000000', '00000003-0000-4000-8000-000000000000')
header = p.SnapshotHeader(p.REQUEST_CONTRACT, 'COMMAND', '00000001-0000-4000-8000-000000000000', '2026-10-14T23:00:00.000Z', p.REQUEST_COMPONENT)
request = p.SnapshotRequest(header, '00000004-0000-4000-8000-000000000000', binding)
assert p.decode_request(p.encode(request), binding=binding) == request
assert not any(any(n == x or n.startswith(x + '.') for x in forbidden) for n in sys.modules)
print('INERT_IMPORT_USE_PASS')
'''
        result = subprocess.run([sys.executable, '-B', '-c', script], cwd=ROOT,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'INERT_IMPORT_USE_PASS')


if __name__ == '__main__':
    unittest.main()
