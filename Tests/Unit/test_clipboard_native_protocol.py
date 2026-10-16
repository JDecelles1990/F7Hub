"""H01-A inert wire conformance; all content and identities are synthetic."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

from f7hub.infrastructure import clipboard_native_protocol as p


ROOT = Path(__file__).resolve().parents[2]
IDS = [f'{i:08x}-0000-4000-8000-000000000000' for i in range(1, 30)]
NOW = '2026-10-15T12:00:00.000Z'
SENTINEL = 'SYNTHETIC_SECRET_MUST_NOT_APPEAR'


def document(contract, payload, *, correlation=None, identity=0):
    message_class, producer, *_ = p._PROFILES[contract]
    value = {'contract': contract, 'schema_version': '1.0', 'message_class': message_class,
             'message_id': IDS[identity], 'created_at': NOW,
             'producer': {'component': producer}, 'payload': payload}
    if correlation is not None:
        value['correlation_id'] = correlation
    return value


def wire(value, *, ascii=False):
    return json.dumps(value, ensure_ascii=ascii, separators=(',', ':')).encode('utf-8')


class NativeProtocolTests(unittest.TestCase):
    def setUp(self):
        self.begin = document('clipboard.capture_begin',
                              {'press_id': IDS[2], 'action': 'clipboard.capture_selection',
                               'target_token': IDS[3]})
        self.request = p.decode_message(wire(self.begin), expected_producer='ahk.clipboard')

    def reject(self, value, *, raw=False, request=None):
        with self.assertRaises(p.NativeProtocolError) as error:
            p.decode_message(value if raw else wire(value), request=request)
        self.assertEqual(str(error.exception), 'NATIVE_PROTOCOL_REJECTED')
        self.assertNotIn(SENTINEL, str(error.exception))

    def test_closed_profiles_and_schema_inventory(self):
        schema = json.loads((ROOT / 'Config/JSON/clipboard_native_v1.schema.json').read_text(encoding='utf-8'))
        self.assertEqual({item['properties']['contract']['const'] for item in schema['oneOf']}, set(p._PROFILES))
        self.assertEqual(schema['x-max-depth'], p.MAX_DEPTH)
        for contract, (kind, producer, required, optional, conditional) in p._PROFILES.items():
            spec = next(item for item in schema['oneOf'] if item['properties']['contract']['const'] == contract)
            self.assertEqual(spec['properties']['producer']['properties']['component']['const'], producer)
            self.assertEqual(spec['properties']['message_class']['const'], kind)
            payload = spec['properties']['payload']
            variants = payload.get('oneOf', [payload])
            self.assertEqual(set(variants[0]['properties']), set(required) | set(optional))
            self.assertTrue(all(variant['additionalProperties'] is False for variant in variants))
            self.assertTrue(spec['additionalProperties'] is False)
            self.assertEqual(len(variants), 2 if conditional else 1)
            if contract in p._RESULT_STATUSES:
                declared = set()
                for variant in variants:
                    status = variant['properties']['status']
                    declared.update(status.get('enum', [status['const']] if 'const' in status else []))
                self.assertEqual(declared, set(p._RESULT_STATUSES[contract]))

    def test_cross_language_json_vectors_and_exact_unicode(self):
        fixtures = json.loads((ROOT / 'Tests/Unit/fixtures/clipboard_native_v1_vectors.json').read_text(encoding='utf-8'))
        self.assertEqual(fixtures['version'], p.VERSION)
        parsed = {}
        for vector in fixtures['vectors']:
            raw = vector['wire_utf8'].encode('utf-8')
            if not vector['valid']:
                self.reject(raw, raw=True)
                continue
            request = parsed.get(vector.get('request'))
            parsed[vector['name']] = p.decode_message(raw, request=request)
            if 'text' in vector:
                self.assertEqual(parsed[vector['name']].payload['text'], vector['text'])
        sample = 'A\tB\r\nÉ界😀'
        submit = document('clipboard.capture_submit',
                          {'operation_id': IDS[4], 'producer_generation': IDS[5],
                           'mode': 'selection', 'observed_at': NOW, 'format': 'text/plain',
                           'text': sample})
        for ascii_encoded in (False, True):
            message = p.decode_message(wire(submit, ascii=ascii_encoded))
            self.assertEqual(message.payload['text'], sample)
            self.assertEqual(p.decode_message(p.encode_message(message)).payload['text'], sample)
        result = document('clipboard.capture_begin_result',
                          {'press_id': IDS[2], 'status': 'READY', 'operation_id': IDS[4],
                           'producer_generation': IDS[5]}, correlation=IDS[0], identity=1)
        self.assertEqual(p.decode_message(wire(result), request=self.request).payload['operation_id'], IDS[4])
        self.reject(result, request=p.decode_message(wire({**self.begin, 'message_id': IDS[8]})))
        wrong = deepcopy(result)
        wrong['payload']['press_id'] = IDS[7]
        self.reject(wrong, request=self.request)
        error = document('contract.error', {'code': 'TIMEOUT', 'message': p.SAFE_ERROR_MESSAGE},
                         correlation=IDS[0], identity=1)
        self.assertEqual(p.decode_message(wire(error), request=self.request).payload['code'], 'TIMEOUT')

    def test_all_fixed_actions_and_result_shapes(self):
        paste = document('clipboard.paste_prepare',
                         {'press_id': IDS[2], 'action': 'clipboard.paste_latest', 'target_token': IDS[3]})
        self.assertEqual(p.decode_message(wire(paste)).payload['action'], 'clipboard.paste_latest')
        for value in (self.begin, paste):
            wrong = deepcopy(value)
            wrong['payload']['action'] = 'clipboard.paste_active'
            self.reject(wrong)
        consumed = document('clipboard.paste_consume_result',
                            {'prepared_id': IDS[3], 'status': 'READY', 'text': 'literal\ntext',
                             'format': 'text/plain', 'effect_lease_expires_at': NOW},
                            correlation=IDS[0], identity=1)
        self.assertEqual(p.decode_message(wire(consumed)).payload['text'], 'literal\ntext')
        for field in ('text', 'format', 'effect_lease_expires_at'):
            missing = deepcopy(consumed)
            del missing['payload'][field]
            self.reject(missing)
        denied = deepcopy(consumed)
        denied['payload']['status'] = 'DENIED'
        self.reject(denied)
        for field in ('text', 'format', 'effect_lease_expires_at'):
            del denied['payload'][field]
        self.assertEqual(p.decode_message(wire(denied)).payload['status'], 'DENIED')
        receipt = document('clipboard.capture_submit_result',
                           {'operation_id': IDS[4], 'status': 'SUCCESS', 'replayed': False,
                            'item_id': '1', 'event_id': '2', 'receipt_id': '3'},
                           correlation=IDS[0], identity=1)
        self.assertEqual(p.decode_message(wire(receipt)).payload['event_id'], '2')
        receipt['payload']['item_id'] = '01'
        self.reject(receipt)
        receipt['payload']['item_id'] = '1'
        receipt['payload']['status'] = 'READY'
        self.reject(receipt)

    def test_malformed_identity_encoding_and_structure(self):
        variants = []
        for field, bad in (('schema_version', '1.1'), ('message_class', 'RESULT'),
                           ('message_id', 'FFFFFFFF-0000-4000-8000-000000000000'), ('created_at', '2026-02-30T12:00:00.000Z')):
            item = deepcopy(self.begin); item[field] = bad; variants.append(item)
        for field, bad in (('press_id', 1), ('target_token', 'FFFFFFFF-0000-4000-8000-000000000000')):
            item = deepcopy(self.begin); item['payload'][field] = bad; variants.append(item)
        item = deepcopy(self.begin); item['payload']['command'] = 'do_anything'; variants.append(item)
        item = deepcopy(self.begin); item['producer']['component'] = 'f7hub.clipboard'; variants.append(item)
        item = deepcopy(self.begin); item['payload']['target_token'] = SENTINEL; variants.append(item)
        for item in variants:
            self.reject(item)
        for raw in (b'\xef\xbb\xbf' + wire(self.begin), b'\xff', wire(self.begin) + b'{}',
                    wire(self.begin).replace(b'"press_id":', b'"press_id":"x","press_id":'),
                    wire(self.begin).replace(b'"target_token":', b'"x":[1],"target_token":'),
                    b' ' * (p.MAX_ORDINARY_BYTES + 1),
                    wire(self.begin).replace(b'"1.0"', b'NaN')):
            self.reject(raw, raw=True)
        item = deepcopy(self.begin); item['payload']['target_token'] = IDS[3] + '\ud800'
        self.reject(wire(item, ascii=True), raw=True)

    def test_limits_and_content_free_failure(self):
        submit = document('clipboard.capture_submit',
                          {'operation_id': IDS[4], 'producer_generation': IDS[5],
                           'mode': 'selection', 'observed_at': NOW, 'format': 'text/plain',
                           'text': '😀' * 16384})
        self.assertEqual(len(p.decode_message(wire(submit)).payload['text'].encode('utf-8')), 65536)
        submit['payload']['text'] += 'a'
        self.reject(submit)
        submit['payload']['text'] = 'X' * 65536
        self.assertLess(len(wire(submit)), p.MAX_CONTENT_BYTES)
        self.assertIsNotNone(p.decode_message(wire(submit)))
        submit['payload']['text'] = '😀' * 16384
        submit['payload']['text'] += SENTINEL
        self.reject(submit)
        for raw in (wire(self.begin).replace(b'"payload":{', b'"payload":' + b'{' * 7),
                    wire(self.begin).replace(b'"payload":{', b'"payload":' + b'{"x":0,' * 17)):
            self.reject(raw, raw=True)

    def test_frame_layout_only_no_implicit_authentication(self):
        body = wire(self.begin)
        frame = p.NativeFrame(1, body, b'\x00' * 32)
        raw = p.pack_frame(frame)
        self.assertEqual(len(raw), len(body) + 44)
        self.assertEqual(p.unpack_frame(raw), frame)
        # A zero MAC is accepted structurally; no caller may treat this as authenticated.
        for bad in (raw[:-1], raw + b'!', b'\xff\xff\xff\xff' + raw[4:],
                    b'\x00\x00\x00\x00' + raw[4:],
                    raw[:4] + b'\x00' * 8 + raw[12:]):
            with self.assertRaises(p.NativeProtocolError):
                p.unpack_frame(bad)
        with self.assertRaises(p.NativeProtocolError):
            p.NativeFrame(1, body, b'bad')


if __name__ == '__main__':
    unittest.main()
