"""Bounded pure HBR-01 security tests. Every key/identity/document is synthetic.

No native adapters, processes, Clipboard, database, Qt or AHK are used. Wire
construction here follows the adopted bytes independently of production helpers.
"""

from dataclasses import replace
import hashlib
import hmac
import json
import struct
import unittest
from unittest.mock import patch

from f7hub.infrastructure import clipboard_native_protocol as wire
from f7hub.infrastructure import clipboard_native_session as s


KEY = bytes(range(32))
GEN = bytes(range(0x60, 0x70))
CONTEXT = bytes.fromhex(
    '606162636465666768696a6b6c6d6e6f92100000ab89674523a1dc0184140000'
    'ab99674523a1dc01030000009ceb227ffdf00cc596386e11816d907611e3482f'
    '7093de4d1e6db5c975361e2b588d9ab4103a08bc090835a1bc99981546911212'
    'f9e5c1a4e54e595f7b75b28000200000')
FREQUENCY = 1_000_000
U64 = 2**64 - 1
ZERO = bytes(16)


def ident(n):
    return n.to_bytes(16, 'little')


def enrollment(epoch=0):
    r = s.RetirementIdentity(GEN, 5252, 0x1dca123456799ab, epoch,
                             GEN if epoch == 0 else ident(99), epoch)
    return s.EnrollmentContext(r, KEY, CONTEXT,
                               ident(50) if epoch else ZERO, 0 if epoch else 255)


def digest(key, label, *parts):
    return hmac.new(key, label + b'\0' + b''.join(parts), hashlib.sha256).digest()


def control(kind, body, key=KEY):
    header = b'F7H01CTL' + bytes((1, kind)) + struct.pack('<H', len(body) + 44)
    return header + body + digest(key, b'F7H01CTL/mac', header, body)


def transcript(e):
    def header(kind, length):
        return b'F7H01C01' + bytes((1, kind)) + struct.pack('<H', length)
    ch = header(1, 156) + e.pinned_context + bytes(range(0x20, 0x40))
    sh0 = header(2, 188) + e.pinned_context + bytes(range(0x40, 0x60))
    key = KEY if e.identity.epoch == 0 else digest(
        KEY, b'F7H01C01/epoch-key', struct.pack('<Q', e.identity.epoch), e.identity.offer_id)
    sp = digest(key, b'F7H01C01/server-proof', ch, sh0)
    sh = sh0 + sp
    cf = header(3, 44) + digest(key, b'F7H01C01/client-proof', ch, sh0, sp)
    sf = header(4, 44) + digest(key, b'F7H01C01/server-finish', ch, sh0, sp, cf)
    salt = hashlib.sha256(b'F7H01C01/salt\0' + ch + sh0).digest()
    prk = hmac.new(salt, key, hashlib.sha256).digest()
    base = b'F7H01C01/session\0' + hashlib.sha256(ch + sh + cf + sf).digest()
    c2s = hmac.new(prk, base + b'/client-to-server\0\x01', hashlib.sha256).digest()
    sid = hmac.new(prk, base + b'/session-id\0\x01', hashlib.sha256).digest()[:16]
    return (ch, sh, cf, sf), c2s, sid


def document(contract='clipboard.native_status', *, payload=None):
    return json.dumps({'contract': contract, 'schema_version': '1.0',
                       'message_class': 'QUERY',
                       'message_id': '123e4567-e89b-42d3-a456-426614174000',
                       'created_at': '2026-10-16T12:00:00.000Z',
                       'producer': {'component': 'ahk.clipboard'},
                       'payload': {'supported_version': '1.0'} if payload is None else payload},
                      separators=(',', ':')).encode()


def data_frame(key, sid, sequence=1, raw=None, *, direction=1):
    raw = document() if raw is None else raw
    header = struct.pack('<IQ', len(raw), sequence)
    return header + raw + digest(key, b'F7H01C01/frame', sid, bytes((1, direction)), header, raw)


def ack(e, *, receipt=ident(50), outcome=0, **changes):
    r = e.identity
    values = {'generation': r.generation, 'pid': r.child_pid, 'creation': r.child_creation,
              'epoch': r.epoch, 'offer': r.offer_id, 'owner': r.owner_gen,
              'outcome': outcome, 'receipt': receipt}
    values.update(changes)
    return control(9, struct.pack('<16sIQQ16sQB16s', *values.values()))


def reply(e, query=ident(10), *, state=0, outcome=0, receipt=ident(50), **changes):
    r = e.identity
    values = {'generation': r.generation, 'query': query, 'pid': r.child_pid,
              'creation': r.child_creation, 'highwater': r.epoch, 'epoch': r.epoch,
              'offer': r.offer_id, 'owner': r.owner_gen, 'state': state,
              'outcome': outcome, 'receipt': receipt}
    values.update(changes)
    return control(11, struct.pack('<16s16sIQQQ16sQBB16s', *values.values()))


class Clock:
    def __init__(self):
        self.tick = 1_000_000

    def __call__(self):
        return self.tick

    def advance(self, ticks):
        self.tick += ticks


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.e = enrollment()

    def core(self, e=None):
        return s.NativeSessionPolicy(e or self.e, clock=self.clock, frequency=FREQUENCY)

    def ledger(self):
        return s.RetirementLedger(self.e, clock=self.clock, frequency=FREQUENCY)

    def active(self, e=None):
        e = e or self.e
        core = self.core(e)
        core.begin_request(ident(1))
        messages, key, sid = transcript(e)
        core.verify_handshake(*messages)
        core.observe_server_finish_write(s.IOObservation.COMPLETED)
        return core, key, sid

    def closed(self, *, failed=False, e=None):
        core, _, _ = self.active(e)
        if not failed:
            self.clock.advance(30 * FREQUENCY)
        else:
            self.clock.advance(FREQUENCY)
        core.observe_child_io(s.IOObservation.COMPLETED)
        original = core.record_child_close(reason=1 if failed else 0,
                                           outcome=3 if failed else 0)
        return core, original

    def settle(self, ledger, closed, *, outcome=0):
        ledger.receive_closed(closed)
        ledger.observe_app_io(s.IOObservation.COMPLETED)
        ledger.record_server_close()
        return ledger.complete_retirement(ident(50), outcome=outcome)

    def rejected(self, call, *args, **kwargs):
        with self.assertRaises(s.SessionPolicyError) as caught:
            call(*args, **kwargs)
        self.assertIn(str(caught.exception), ('NATIVE_SESSION_REJECTED', 'UNAVAILABLE', 'BUSY'))
        return caught.exception

    def test_frozen_epoch0_crypto_and_status_vector(self):
        # Exact adopted vector outputs, not a comparison to production signing.
        messages, key, sid = transcript(self.e)
        self.assertEqual(messages[1][156:].hex(),
                         '47f40b77c747b17906a560b5fdc74aa10a6a8c1d43a0a27ecd4274c00eb1e1e1')
        self.assertEqual(messages[2][12:].hex(),
                         'd5a58724ebc339f5ef12f9090f60cbe52395f096abc33d9ef4c6ba1eb3009ef0')
        self.assertEqual(messages[3][12:].hex(),
                         'bb7224631e40e121fd9e0884367fa003682999cfb4fc6ddd5f64744f9bcca8f4')
        self.assertEqual(key.hex(), '0427d6ab56a96122e53f6bd246798fb00019f34acbedc04ab92d815e83c69f51')
        self.assertEqual(sid.hex(), 'd24a0dd3599f78461de968162388a155')
        raw = data_frame(key, sid)
        self.assertEqual(raw[-32:].hex(), '4d06c5114be5cc7f2c3088f6f474ba2079440a25c0f9425f697b1752fc2ba13f')
        core, _, _ = self.active()
        permit = core.accept_status(raw)
        self.assertEqual(permit.session_id, sid)
        self.assertEqual(permit.identity, self.e.identity)
        self.assertEqual(permit.message_id, '123e4567-e89b-42d3-a456-426614174000')
        self.rejected(core.accept_status, raw)  # No second dispatch in one press.

    def test_renewal_key_changes_and_old_proof_rejects(self):
        core, key, sid = self.active(enrollment(1))
        self.assertNotEqual(sid, transcript(self.e)[2])
        self.assertIsInstance(core.accept_status(data_frame(key, sid)), s.StatusPermit)
        other = self.core(enrollment(1))
        other.begin_request(ident(1))
        self.rejected(other.verify_handshake, *transcript(self.e)[0])
        self.assertTrue(other.quarantined)

    def test_each_tampered_handshake_message_rejects(self):
        for index in range(4):
            with self.subTest(message=index):
                core = self.core()
                core.begin_request(ident(1))
                messages = list(transcript(self.e)[0])
                raw = bytearray(messages[index])
                raw[-1] ^= 1
                messages[index] = bytes(raw)
                self.rejected(core.verify_handshake, *messages)
                self.assertTrue(core.quarantined)

    def test_wrong_pinned_process_and_generation_reject(self):
        for offset in (0, 16, 28, 32, 40, 44, 76, 108):
            with self.subTest(context_offset=offset):
                core = self.core()
                core.begin_request(ident(1))
                messages = list(transcript(self.e)[0])
                ch = bytearray(messages[0]); ch[12 + offset] ^= 1
                messages[0] = bytes(ch)
                self.rejected(core.verify_handshake, *messages)
                self.assertTrue(core.quarantined)

    def test_zero_and_reflected_nonce_reject(self):
        for nonce in (bytes(32), bytes(range(0x40, 0x60))):
            core = self.core(); core.begin_request(ident(1))
            messages = list(transcript(self.e)[0])
            messages[0] = messages[0][:124] + nonce
            self.rejected(core.verify_handshake, *messages)

    def test_no_status_before_proofs_and_observed_finish_write(self):
        for observation in (s.IOObservation.PENDING, s.IOObservation.CANCEL_REQUESTED):
            core = self.core(); core.begin_request(ident(1))
            messages, key, sid = transcript(self.e)
            self.rejected(core.accept_status, data_frame(key, sid))
            core.verify_handshake(*messages)
            core.observe_server_finish_write(observation)
            self.assertEqual(core.phase, s.Phase.PROOFS_VERIFIED)
            self.rejected(core.accept_status, data_frame(key, sid))

    def test_repeated_handshake_cannot_adopt_second_offer(self):
        core, _, _ = self.active()
        self.rejected(core.verify_handshake, *transcript(self.e)[0])
        self.assertTrue(core.quarantined)
        with self.assertRaises(AttributeError):
            core.identity = enrollment(1).identity

    def test_frame_mac_and_session_direction_binding(self):
        for variant in ('tamper', 'wrong_key', 'wrong_session', 'wrong_direction', 'no_mac'):
            with self.subTest(variant=variant):
                core, key, sid = self.active()
                raw = data_frame(key, sid)
                if variant == 'tamper':
                    raw = raw[:-1] + bytes((raw[-1] ^ 1,))
                elif variant == 'wrong_key':
                    raw = data_frame(bytes(32), sid)
                elif variant == 'wrong_session':
                    raw = data_frame(key, ident(999))
                elif variant == 'wrong_direction':
                    raw = data_frame(key, sid, direction=2)
                else:
                    raw = raw[:-32]
                with patch.object(wire, 'decode_message', side_effect=AssertionError('parse before MAC')):
                    self.rejected(core.accept_status, raw)
                self.assertTrue(core.quarantined)

    def test_sequence_replay_and_gap_reject_before_json(self):
        for sequence in (0, 2, 10):
            core, key, sid = self.active()
            with patch.object(wire, 'decode_message', side_effect=AssertionError('parse before sequence')):
                self.rejected(core.accept_status, data_frame(key, sid, sequence))
            self.assertTrue(core.quarantined)
        core, key, sid = self.active()
        core.accept_status(data_frame(key, sid))
        core.begin_request(ident(2))
        self.rejected(core.accept_status, data_frame(key, sid))
        self.assertTrue(core.quarantined)

    def test_next_sequence_on_new_request_succeeds(self):
        core, key, sid = self.active()
        core.accept_status(data_frame(key, sid))
        core.begin_request(ident(2))
        self.assertIsInstance(core.accept_status(data_frame(key, sid, 2)), s.StatusPermit)

    def test_no_sequence_wrap(self):
        core, key, sid = self.active()
        core._sequence = U64  # Reach a finite boundary without 2**64 operations.
        core.accept_status(data_frame(key, sid, U64))
        self.assertEqual(core.phase, s.Phase.RETIRING)
        core.begin_request(ident(2))
        self.rejected(core.accept_status, data_frame(key, sid, 1))

    def test_capture_paste_lookup_persistence_and_unknown_profiles_denied(self):
        profiles = {
            'clipboard.capture_begin': {'press_id': '123e4567-e89b-42d3-a456-426614174001',
                'action': 'clipboard.capture_selection', 'target_token': '123e4567-e89b-42d3-a456-426614174002'},
            'clipboard.capture_submit': {'operation_id': '123e4567-e89b-42d3-a456-426614174001',
                'producer_generation': '123e4567-e89b-42d3-a456-426614174002', 'mode': 'selection',
                'observed_at': '2026-10-16T12:00:00.000Z', 'format': 'text/plain', 'text': 'SYNTHETIC'},
            'clipboard.paste_prepare': {'press_id': '123e4567-e89b-42d3-a456-426614174001',
                'action': 'clipboard.paste_latest', 'target_token': '123e4567-e89b-42d3-a456-426614174002'},
            'clipboard.paste_consume': {'prepared_id': '123e4567-e89b-42d3-a456-426614174001',
                'head_token': '123e4567-e89b-42d3-a456-426614174002', 'item_id': '1', 'revision': '1',
                'target_token': '123e4567-e89b-42d3-a456-426614174003'},
            'clipboard.lookup': {'query_id': '123e4567-e89b-42d3-a456-426614174001',
                'operation_id': '123e4567-e89b-42d3-a456-426614174002',
                'producer_generation': '123e4567-e89b-42d3-a456-426614174003'},
        }
        for contract, payload in profiles.items():
            with self.subTest(contract=contract):
                # First establish a valid H01-A command, so denial tests policy.
                message = wire.NativeMessage(contract, '123e4567-e89b-42d3-a456-426614174000',
                                             '2026-10-16T12:00:00.000Z', 'ahk.clipboard', payload)
                core, key, sid = self.active()
                self.rejected(core.accept_status, data_frame(key, sid, raw=wire.encode_message(message)))
                self.assertTrue(core.quarantined)
        for contract in ('clipboard.persist', 'clipboard.monitor', 'run_command'):
            core, key, sid = self.active()
            self.rejected(core.accept_status, data_frame(key, sid, raw=document(contract)))

    def test_authenticated_malformed_json_role_and_shape_rejected(self):
        for raw in (b'{', b'{}', document(payload={'supported_version': '1.0', 'text': 'SYNTHETIC'}),
                    document().replace(b'ahk.clipboard', b'f7hub.clipboard')):
            core, key, sid = self.active()
            self.rejected(core.accept_status, data_frame(key, sid, raw=raw))
            self.assertTrue(core.quarantined)

    def test_deadline_equality_expiry_and_no_initial_budget_reset(self):
        for elapsed in (499_999, 500_000, 500_001):
            core, key, sid = self.active()
            self.clock.advance(elapsed)
            if elapsed < 500_000:
                core.accept_status(data_frame(key, sid))
            else:
                self.rejected(core.accept_status, data_frame(key, sid))
            self.clock.advance(FREQUENCY)

    def test_deadline_checked_after_document_validation(self):
        core, key, sid = self.active()
        original_decode = wire.decode_message
        def slow_decode(*args, **kwargs):
            result = original_decode(*args, **kwargs)
            self.clock.advance(500_000)
            return result
        with patch.object(wire, 'decode_message', side_effect=slow_decode):
            self.rejected(core.accept_status, data_frame(key, sid))

    def test_handshake_and_finish_cannot_establish_at_cutoff(self):
        core = self.core(); core.begin_request(ident(1)); self.clock.advance(500_000)
        self.rejected(core.verify_handshake, *transcript(self.e)[0])
        core = self.core(); core.begin_request(ident(2)); core.verify_handshake(*transcript(self.e)[0])
        self.clock.advance(500_000)
        self.rejected(core.observe_server_finish_write, s.IOObservation.COMPLETED)
        self.assertNotEqual(core.phase, s.Phase.ACTIVE)

    def test_clock_regression_invalid_frequency_and_overflow_fail_closed(self):
        core = self.core(); core.begin_request(ident(1)); self.clock.advance(-1)
        self.rejected(core.begin_request, ident(2)); self.assertTrue(core.quarantined)
        for frequency in (True, 0, 1, -1, float('nan')):
            self.rejected(s.NativeSessionPolicy, self.e, clock=Clock(), frequency=frequency)
        self.clock.tick = U64
        core = self.core()
        self.rejected(core.begin_request, ident(1)); self.assertTrue(core.quarantined)

    def test_concurrent_and_duplicate_request_no_budget_reset(self):
        core = self.core(); core.begin_request(ident(1))
        self.rejected(core.begin_request, ident(2))
        self.clock.advance(500_000)
        self.rejected(core.begin_request, ident(1))
        core.begin_request(ident(2))

    def test_idle_cutoff_requires_retirement_not_a_new_request(self):
        core, key, sid = self.active()
        self.clock.advance(30 * FREQUENCY)
        core.begin_request(ident(2))
        self.rejected(core.accept_status, data_frame(key, sid))
        self.assertEqual(core.phase, s.Phase.RETIRING)

    def test_b1_direct_and_lost_ack_query_recover_stable_receipt(self):
        for lost in (False, True):
            core, closed = self.closed(); ledger = self.ledger()
            original_ack = self.settle(ledger, closed)
            if lost:
                core.begin_request(ident(2))
                query = core.make_state_query(ident(10))
                state_reply = ledger.reply_to_query(query)
                self.assertEqual(core.receive_state_reply(state_reply), 'RECEIPT_KNOWN')
            else:
                self.assertTrue(core.receive_retire_ack(original_ack))
            self.assertEqual(core.phase, s.Phase.RECEIPT_KNOWN)
            self.assertEqual(core.receipt, ledger.receipt)
            self.assertFalse(core.receive_retire_ack(original_ack))
            self.assertFalse(core.resend_used)

    def test_failed_post_start_outcome3_late_ack_bookkeeping_only(self):
        core, closed = self.closed(failed=True); ledger = self.ledger()
        raw = self.settle(ledger, closed, outcome=3)
        core.receive_retire_ack(raw)
        self.assertEqual(core.receipt.outcome, 3)
        self.rejected(core.accept_status, bytes(45))
        self.rejected(core.claim_closed_retransmission)

    def test_wrong_outcome_or_conflicting_receipt_quarantines(self):
        for outcome in (1, 2, 3, 4, 255):
            core, _ = self.closed()
            self.rejected(core.receive_retire_ack, ack(self.e, outcome=outcome))
            self.assertTrue(core.quarantined)
        core, _ = self.closed()
        core.receive_retire_ack(ack(self.e))
        self.rejected(core.receive_retire_ack, ack(self.e, receipt=ident(51)))
        self.assertTrue(core.quarantined)
        self.assertEqual(core.receipt.receipt_id, ident(50))

    def test_wrong_retirement_identity_never_advances(self):
        changes = ({'epoch': 1}, {'offer': ident(12)}, {'owner': 1},
                   {'pid': 99}, {'creation': 1}, {'generation': ident(66)})
        for change in changes:
            core, _ = self.closed()
            self.rejected(core.receive_retire_ack, ack(self.e, **change))
            self.assertIsNone(core.receipt)

    def test_tampered_unauthenticated_and_malformed_control_rejects(self):
        for variant in ('tamper', 'no_mac', 'trailing', 'wrong_type', 'wrong_key'):
            core, _ = self.closed(); raw = ack(self.e)
            if variant == 'tamper': raw = raw[:-1] + bytes((raw[-1] ^ 1,))
            elif variant == 'no_mac': raw = raw[:-32]
            elif variant == 'trailing': raw += b'X'
            elif variant == 'wrong_type': raw = raw[:9] + b'\x0b' + raw[10:]
            else: raw = control(9, raw[12:-32], key=bytes(32))
            self.rejected(core.receive_retire_ack, raw)
            self.assertTrue(core.quarantined)
            self.assertIsNone(core.receipt)

    def test_cancel_or_incomplete_child_io_cannot_establish_closed_state(self):
        for observation in (s.IOObservation.PENDING, s.IOObservation.CANCEL_REQUESTED):
            core = self.core(); core.observe_child_io(observation)
            self.rejected(core.record_child_close, reason=1, outcome=3)
            self.rejected(core.receive_retire_ack, ack(self.e, outcome=3))
            self.assertIsNone(core.receipt)

    def test_no_repeat_child_or_app_close(self):
        core, closed = self.closed()
        self.rejected(core.record_child_close, reason=0, outcome=0)
        ledger = self.ledger(); raw_ack = self.settle(ledger, closed)
        self.rejected(ledger.record_server_close)
        self.assertFalse(ledger.receive_closed(closed))
        self.assertIsNone(ledger.complete_retirement(ident(50), outcome=0))
        self.assertEqual(raw_ack, ack(self.e))

    def test_b2_lost_closed_recovers_without_second_close(self):
        core, original = self.closed(); ledger = self.ledger()
        core.begin_request(ident(2)); query = core.make_state_query(ident(10))
        state_reply = ledger.reply_to_query(query)
        self.assertEqual(core.receive_state_reply(state_reply), 'PENDING')
        self.assertIsNone(core.receipt)
        resend = core.claim_closed_retransmission()
        self.assertEqual(resend, original)
        self.assertTrue(core.resend_used)
        self.rejected(core.claim_closed_retransmission)
        raw_ack = self.settle(ledger, resend)
        core.receive_retire_ack(raw_ack)
        self.assertEqual(core.receipt, ledger.receipt)
        self.rejected(core.record_child_close, reason=0, outcome=0)

    def test_b2_failed_post_start_lost_closed_and_lost_ack(self):
        core, original = self.closed(failed=True); ledger = self.ledger()
        core.begin_request(ident(2)); q = core.make_state_query(ident(10))
        core.receive_state_reply(ledger.reply_to_query(q))
        resend = core.claim_closed_retransmission()
        self.settle(ledger, resend, outcome=3)  # Drop ACK as well.
        self.clock.advance(500_000)
        core.begin_request(ident(3)); q = core.make_state_query(ident(11))
        core.receive_state_reply(ledger.reply_to_query(q))
        self.assertEqual(core.receipt.outcome, 3)
        self.assertEqual(resend, original)

    def test_allowance_consumed_even_with_no_observed_delivery_and_new_request(self):
        core, _ = self.closed(); ledger = self.ledger()
        core.begin_request(ident(2)); q = core.make_state_query(ident(10))
        core.receive_state_reply(ledger.reply_to_query(q))
        core.claim_closed_retransmission()  # Deliberately drop it; no success callback.
        self.clock.advance(500_000)
        core.begin_request(ident(3)); q = core.make_state_query(ident(11))
        core.receive_state_reply(ledger.reply_to_query(q))
        self.rejected(core.claim_closed_retransmission)
        self.assertTrue(core.resend_used)
        self.assertIsNone(core.receipt)
        self.assertIsNone(ledger.receipt)

    def test_no_unsolicited_resend_or_second_query(self):
        core, _ = self.closed()
        self.rejected(core.claim_closed_retransmission)
        core.begin_request(ident(2))
        self.rejected(core.claim_closed_retransmission)
        core.make_state_query(ident(10))
        self.rejected(core.make_state_query, ident(11))
        self.rejected(core.claim_closed_retransmission)

    def test_pending_previous_receipt_is_not_current_retirement(self):
        e = enrollment(1)
        core, _ = self.closed(e=e)
        core.begin_request(ident(2)); core.make_state_query(ident(10))
        self.assertEqual(core.receive_state_reply(reply(e, state=1,
                                                       outcome=e.previous_outcome,
                                                       receipt=e.previous_receipt_id)), 'PENDING')
        self.assertIsNone(core.receipt)
        core.claim_closed_retransmission()

    def test_active_quarantined_wrong_identity_query_context_denies_resend(self):
        for changes in ({'state': 2}, {'state': 3}, {'epoch': 1},
                        {'highwater': 1}, {'query': ident(999)}):
            core, _ = self.closed(); core.begin_request(ident(2)); core.make_state_query(ident(10))
            raw = reply(self.e, state=1, outcome=255, receipt=ZERO, **changes) \
                if 'state' not in changes else reply(self.e, outcome=255, receipt=ZERO, **changes)
            try:
                core.receive_state_reply(raw)
            except s.SessionPolicyError:
                pass
            self.rejected(core.claim_closed_retransmission)
            self.assertIsNone(core.receipt)

    def test_expired_query_reply_cannot_be_adopted_by_next_request(self):
        core, _ = self.closed(); core.begin_request(ident(2)); core.make_state_query(ident(10))
        raw = reply(self.e)
        self.clock.advance(500_000)
        self.rejected(core.receive_state_reply, raw)
        self.assertIsNone(core.receipt)
        core.begin_request(ident(3)); core.make_state_query(ident(11))
        self.rejected(core.receive_state_reply, raw)
        self.assertIsNone(core.receipt)

    def test_resend_and_recovery_confirmation_cutoff_equality(self):
        core, closed = self.closed(); ledger = self.ledger()
        core.begin_request(ident(2)); q = core.make_state_query(ident(10))
        core.receive_state_reply(ledger.reply_to_query(q))
        self.settle(ledger, closed)
        self.clock.advance(500_000)
        self.rejected(core.claim_closed_retransmission)
        self.rejected(ledger.claim_recovery_confirmation)
        self.assertFalse(core.resend_used)

    def test_delayed_original_resend_race_single_receipt_and_confirmation(self):
        core, original = self.closed(); ledger = self.ledger()
        core.begin_request(ident(2)); q = core.make_state_query(ident(10))
        core.receive_state_reply(ledger.reply_to_query(q))
        resend = core.claim_closed_retransmission()
        first_ack = self.settle(ledger, original)
        self.assertFalse(ledger.receive_closed(resend))
        second_ack = ledger.claim_recovery_confirmation()
        self.assertEqual(first_ack, second_ack)
        self.rejected(ledger.claim_recovery_confirmation)
        core.receive_retire_ack(second_ack)
        self.assertFalse(core.receive_retire_ack(first_ack))
        self.assertIsNone(ledger.reply_to_query(q))

    def test_child_evidence_never_substitutes_for_app_completion_and_close(self):
        for observation in (s.IOObservation.PENDING, s.IOObservation.CANCEL_REQUESTED):
            _, closed = self.closed(); ledger = self.ledger()
            ledger.receive_closed(closed); ledger.observe_app_io(observation)
            self.rejected(ledger.record_server_close)
            self.rejected(ledger.complete_retirement, ident(50), outcome=0)
            self.assertIsNone(ledger.receipt)
        _, closed = self.closed(); ledger = self.ledger()
        ledger.receive_closed(closed); ledger.observe_app_io(s.IOObservation.COMPLETED)
        self.rejected(ledger.complete_retirement, ident(50), outcome=0)

    def test_conflicting_closed_or_receipt_never_replaces_app_record(self):
        _, closed = self.closed(); ledger = self.ledger()
        self.settle(ledger, closed)
        self.rejected(ledger.complete_retirement, ident(51), outcome=0)
        self.assertEqual(ledger.receipt.receipt_id, ident(50))
        _, closed = self.closed(); ledger = self.ledger(); ledger.receive_closed(closed)
        changed = control(3, struct.pack('<16sQ16sI', GEN, 0, GEN, 1))
        self.rejected(ledger.receive_closed, changed)
        self.assertTrue(ledger.quarantined)

    def test_query_does_not_fully_retire_app_or_permit_second_offer(self):
        core, _ = self.closed(); ledger = self.ledger()
        core.begin_request(ident(2)); raw_query = core.make_state_query(ident(10))
        ledger.reply_to_query(raw_query)
        self.assertIsNone(ledger.receipt)
        self.rejected(ledger.complete_retirement, ident(50), outcome=0)
        self.assertFalse(hasattr(core, 'allocate_offer'))
        self.assertFalse(hasattr(ledger, 'allocate_offer'))

    def test_renewal_recovery_preserves_previous_receipt_without_adopting_it(self):
        e = enrollment(1)
        core, _, _ = self.active(e)
        ledger = s.RetirementLedger(e, clock=self.clock, frequency=FREQUENCY)
        self.clock.advance(30 * FREQUENCY)
        core.observe_child_io(s.IOObservation.COMPLETED)
        closed = core.record_child_close(reason=0, outcome=0)
        core.begin_request(ident(2))
        query = core.make_state_query(ident(10))
        self.assertEqual(query[76:92], ident(50))  # Existing observed_receipt field.
        pending = ledger.reply_to_query(query)
        self.assertEqual(pending[-48:-32], ident(50))  # App's previous receipt.
        self.assertEqual(core.receive_state_reply(pending), 'PENDING')
        self.assertIsNone(core.receipt)
        self.assertEqual(core.claim_closed_retransmission(), closed)
        ledger.receive_closed(closed)
        ledger.observe_app_io(s.IOObservation.COMPLETED)
        ledger.record_server_close()
        core.receive_retire_ack(ledger.complete_retirement(ident(51), outcome=0))
        self.assertEqual(core.receipt.receipt_id, ident(51))

    def test_missing_predecessor_context_for_renewed_offer_rejected(self):
        self.rejected(s.EnrollmentContext, enrollment(1).identity, KEY, CONTEXT)
        self.rejected(s.EnrollmentContext, self.e.identity, KEY, CONTEXT, ident(50), 0)

    def test_immediately_reused_query_id_cannot_bind_an_old_reply(self):
        core, _ = self.closed()
        core.begin_request(ident(2)); core.make_state_query(ident(10))
        self.clock.advance(500_000)
        core.begin_request(ident(3))
        self.rejected(core.make_state_query, ident(10))
        self.rejected(core.receive_state_reply, reply(self.e, query=ident(10)))
        self.assertIsNone(core.receipt)

    def test_confirmation_build_time_does_not_extend_request(self):
        core, closed = self.closed(); ledger = self.ledger()
        core.begin_request(ident(2)); ledger.reply_to_query(core.make_state_query(ident(10)))
        self.settle(ledger, closed)
        original = ledger._ack
        def slow_ack():
            result = original()
            self.clock.advance(500_000)
            return result
        with patch.object(ledger, '_ack', side_effect=slow_ack):
            self.rejected(ledger.claim_recovery_confirmation)
        self.rejected(ledger.claim_recovery_confirmation)

    def test_f1_query_build_obeys_original_deadline_and_consumes_query_slot(self):
        for elapsed in (499_999, 500_000, 500_001):
            with self.subTest(elapsed=elapsed):
                core, _ = self.closed()
                core.begin_request(ident(2))
                deadline = self.clock.tick + 500_000
                original_sign = core._sign
                built = []
                def timed_sign(*args):
                    result = original_sign(*args)
                    built.append(result)
                    self.clock.advance(elapsed)
                    return result
                returned = None
                with patch.object(core, '_sign', side_effect=timed_sign) as signer:
                    if elapsed < 500_000:
                        returned = core.make_state_query(ident(10))
                        self.assertEqual(returned, built[0])
                        self.assertEqual(struct.unpack_from('<Q', returned, 92)[0], deadline)
                    else:
                        self.rejected(core.make_state_query, ident(10))
                        self.assertIsNone(returned)
                    self.rejected(core.make_state_query, ident(11))
                    self.assertEqual(signer.call_count, 1)
                self.assertEqual(core._deadline, deadline)
                self.assertEqual(core._query_id, ident(10))
                self.assertFalse(core.resend_used)

    def test_f2_ack_identity_conflict_terminally_fences_later_valid_ack(self):
        for change in ({'pid': 99}, {'creation': 1}, {'owner': 1},
                       {'offer': ident(12)}, {'epoch': 1}):
            with self.subTest(change=change):
                core, _ = self.closed()
                self.rejected(core.receive_retire_ack, ack(self.e, **change))
                self.assertTrue(core.quarantined)
                self.assertEqual(core.phase, s.Phase.QUARANTINED)
                self.rejected(core.receive_retire_ack, ack(self.e))
                self.rejected(core.begin_request, ident(2))
                self.assertIsNone(core.receipt)

    def test_f2_reply_identity_conflict_terminally_fences_later_valid_reply(self):
        for change in ({'pid': 99}, {'creation': 1}, {'owner': 1},
                       {'offer': ident(12)}, {'epoch': 1}, {'highwater': 1}):
            with self.subTest(change=change):
                core, _ = self.closed()
                core.begin_request(ident(2)); core.make_state_query(ident(10))
                self.rejected(core.receive_state_reply, reply(self.e, **change))
                self.assertTrue(core.quarantined)
                self.rejected(core.receive_state_reply, reply(self.e))
                self.rejected(core.receive_retire_ack, ack(self.e))
                self.rejected(core.claim_closed_retransmission)
                self.assertIsNone(core.receipt)

    def test_f2_old_epoch_and_irrelevant_query_do_not_fence_current_offer(self):
        e = enrollment(1)
        core, _ = self.closed(e=e)
        core.begin_request(ident(2)); core.make_state_query(ident(10))
        self.rejected(core.receive_retire_ack, ack(self.e))
        self.rejected(core.receive_state_reply, reply(self.e))
        self.rejected(core.receive_state_reply, reply(e, query=ident(999)))
        self.assertFalse(core.quarantined)
        self.assertIsNone(core.receipt)
        self.assertEqual(core.receive_state_reply(reply(e, receipt=ident(51))), 'RECEIPT_KNOWN')
        self.assertEqual(core.receipt.receipt_id, ident(51))

    def test_f3_original_request_cannot_recover_but_later_request_can_once(self):
        core = self.core(); core.begin_request(ident(1))
        core.observe_child_io(s.IOObservation.COMPLETED)
        original = core.record_child_close(reason=1, outcome=3)
        self.rejected(core.make_state_query, ident(10))
        self.rejected(core.claim_closed_retransmission)
        self.assertFalse(core.resend_used)
        self.assertIsNone(core._query_id)
        self.rejected(core.begin_request, ident(1))
        self.clock.advance(500_000)
        core.begin_request(ident(2))
        ledger = self.ledger()
        query = core.make_state_query(ident(10))
        self.assertEqual(core.receive_state_reply(ledger.reply_to_query(query)), 'PENDING')
        self.assertEqual(core.claim_closed_retransmission(), original)
        self.assertTrue(core.resend_used)
        self.rejected(core.claim_closed_retransmission)
        self.rejected(core.record_child_close, reason=1, outcome=3)
        self.clock.advance(500_000); core.begin_request(ident(3))
        self.clock.advance(500_000); core.begin_request(ident(4))
        self.clock.advance(500_000)
        self.rejected(core.begin_request, ident(1))  # Original remains ineligible after rotation.
        self.assertTrue(core.resend_used)
        core.receive_retire_ack(self.settle(ledger, original, outcome=3))
        self.assertEqual(core.receipt, ledger.receipt)

    def test_f3_later_request_resend_rejects_deadline_equality_and_expiry(self):
        for elapsed in (500_000, 500_001):
            with self.subTest(elapsed=elapsed):
                core, original = self.closed()
                core.begin_request(ident(2))
                core.receive_state_reply(self.ledger().reply_to_query(core.make_state_query(ident(10))))
                self.clock.advance(elapsed)
                self.rejected(core.claim_closed_retransmission)
                self.assertFalse(core.resend_used)
                self.rejected(core.record_child_close, reason=0, outcome=0)
                self.assertEqual(core._closed, original)

    def test_f4_matching_predecessor_for_pending_and_active_reply(self):
        for epoch in (0, 1):
            for state in (1, 2):
                with self.subTest(epoch=epoch, state=state):
                    e = enrollment(epoch)
                    core, original = self.closed(e=e)
                    core.begin_request(ident(2)); core.make_state_query(ident(10))
                    result = core.receive_state_reply(reply(e, state=state,
                        outcome=e.previous_outcome, receipt=e.previous_receipt_id))
                    self.assertEqual(result, 'PENDING' if state == 1 else 'UNAVAILABLE')
                    self.assertFalse(core.quarantined)
                    self.assertIsNone(core.receipt)
                    if state == 1:
                        self.assertEqual(core.claim_closed_retransmission(), original)
                    else:
                        self.rejected(core.claim_closed_retransmission)

    def test_f4_conflicting_predecessor_terminally_fences_recovery(self):
        for epoch in (0, 1):
            e = enrollment(epoch)
            conflicts = ((ident(999), 0),) if epoch == 0 else (
                (ident(999), e.previous_outcome), (e.previous_receipt_id, 3), (ZERO, 255))
            for state in (1, 2):
                for receipt_id, outcome in conflicts:
                    with self.subTest(epoch=epoch, state=state, receipt=receipt_id, outcome=outcome):
                        core, _ = self.closed(e=e)
                        core.begin_request(ident(2)); core.make_state_query(ident(10))
                        self.rejected(core.receive_state_reply,
                                      reply(e, state=state, outcome=outcome, receipt=receipt_id))
                        self.assertTrue(core.quarantined)
                        self.rejected(core.receive_state_reply, reply(e, state=1,
                            outcome=e.previous_outcome, receipt=e.previous_receipt_id))
                        self.rejected(core.receive_state_reply, reply(e, receipt=ident(51)))
                        self.rejected(core.receive_retire_ack, ack(e, receipt=ident(51)))
                        self.rejected(core.claim_closed_retransmission)
                        self.assertIsNone(core.receipt)
                        self.assertFalse(core.resend_used)

    def test_f3_replayed_earlier_id_cannot_create_recovery_but_fresh_id_can(self):
        core = self.core()
        core.begin_request(ident(1))
        self.clock.advance(500_000)
        core.begin_request(ident(2))
        core.observe_child_io(s.IOObservation.COMPLETED)
        original = core.record_child_close(reason=1, outcome=3)
        self.clock.advance(500_000)
        core.begin_request(ident(3))
        self.clock.advance(500_000)
        deadline = core._deadline
        self.rejected(core.begin_request, ident(1))
        self.assertEqual(core._request_id, ident(3))
        self.assertEqual(core._deadline, deadline)
        self.assertIsNone(core._query_id)
        self.assertFalse(core._resend_eligible)
        self.rejected(core.make_state_query, ident(10))
        self.rejected(core.claim_closed_retransmission)
        self.assertFalse(core.resend_used)
        self.assertFalse(core.quarantined)
        core.begin_request(ident(4))
        ledger = self.ledger()
        query = core.make_state_query(ident(10))
        self.assertEqual(core.receive_state_reply(ledger.reply_to_query(query)), 'PENDING')
        self.assertEqual(core.claim_closed_retransmission(), original)
        self.assertTrue(core.resend_used)
        self.rejected(core.claim_closed_retransmission)
        self.rejected(core.record_child_close, reason=1, outcome=3)
        core.receive_retire_ack(self.settle(ledger, original, outcome=3))
        self.assertEqual(core.receipt, ledger.receipt)

    def test_f3_all_accepted_ids_remain_replays_across_multiple_rotations(self):
        core = self.core()
        accepted = (200, 7, 99, 3, 800, 2, 16)  # Opaque IDs need not increase numerically.
        for number in accepted:
            core.begin_request(ident(number))
            if number == 7:
                core.observe_child_io(s.IOObservation.COMPLETED)
                core.record_child_close(reason=1, outcome=3)
            self.clock.advance(500_000)
        deadline = core._deadline
        for number in accepted:
            self.rejected(core.begin_request, ident(number))
            self.assertEqual(core._request_id, ident(16))
            self.assertEqual(core._deadline, deadline)
            self.assertIsNone(core._query_id)
            self.assertFalse(core.resend_used)
        self.assertFalse(core.quarantined)
        core.begin_request(ident(1))  # Never accepted before; smaller bytes are still fresh.
        self.assertEqual(core._request_id, ident(1))

    def test_f3_request_history_capacity_quarantines_without_eviction(self):
        core = self.core()
        for number in range(1, s._MAX_REQUEST_IDS + 1):
            core.begin_request(ident(number))
            self.clock.advance(500_000)
        self.rejected(core.begin_request, ident(1))
        self.assertFalse(core.quarantined)
        self.assertEqual(len(core._accepted_request_ids), s._MAX_REQUEST_IDS)
        self.rejected(core.begin_request, ident(s._MAX_REQUEST_IDS + 1))
        self.assertTrue(core.quarantined)
        self.assertEqual(len(core._accepted_request_ids), s._MAX_REQUEST_IDS)
        self.assertIn(ident(1), core._accepted_request_ids)
        self.assertIn(ident(s._MAX_REQUEST_IDS), core._accepted_request_ids)
        self.rejected(core.begin_request, ident(s._MAX_REQUEST_IDS + 2))
        self.rejected(core.begin_request, ident(1))
        self.rejected(core.claim_closed_retransmission)
        self.assertFalse(core.resend_used)
        self.assertIsNone(core.receipt)

    def test_query_deadline_frequency_and_child_identity_validation(self):
        r = self.e.identity
        for deadline, frequency, child_state, observed in (
                (self.clock.tick, FREQUENCY, 3, ZERO),
                (self.clock.tick + 500_001, FREQUENCY, 3, ZERO),
                (self.clock.tick + 500_000, FREQUENCY + 1, 3, ZERO),
                (self.clock.tick + 500_000, FREQUENCY, 2, ZERO),
                (self.clock.tick + 500_000, FREQUENCY, 3, ident(50))):
            ledger = self.ledger()
            raw = control(10, struct.pack('<16s16sQ16sQ16sQQB', GEN, ident(10), r.epoch,
                                          r.offer_id, r.owner_gen, observed, deadline,
                                          frequency, child_state))
            self.rejected(ledger.reply_to_query, raw)
            self.assertIsNone(ledger.receipt)

    def test_normal_idle_or_requested_close_needs_terminal_context(self):
        core, _, _ = self.active(); core.observe_child_io(s.IOObservation.COMPLETED)
        self.rejected(core.record_child_close, reason=0, outcome=0)  # Idle not elapsed.
        self.rejected(core.record_child_close, reason=2, outcome=0)  # No authenticated request.
        raw = control(7, struct.pack('<16sQ16s', GEN, 0, GEN))
        core.receive_close_request(raw)
        core.record_child_close(reason=2, outcome=0)
        self.assertEqual(core.phase, s.Phase.LOCAL_CLOSED)

    def test_identity_validation_and_no_secret_repr_or_reflection(self):
        for changes in ({'owner_gen': True}, {'epoch': -1}, {'generation': ZERO},
                        {'child_pid': True}, {'offer_id': ident(2)}):
            self.rejected(replace, self.e.identity, **changes)
        self.assertNotIn(KEY.hex(), repr(self.e))
        self.assertNotIn(repr(KEY), repr(self.e))
        core = self.core()
        error = self.rejected(core.receive_retire_ack, b'SYNTHETIC_SECRET')
        self.assertNotIn('SYNTHETIC_SECRET', str(error))


if __name__ == '__main__':
    unittest.main()
