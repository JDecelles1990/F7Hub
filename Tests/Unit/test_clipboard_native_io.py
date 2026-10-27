"""Synthetic local observations only; no Windows handle, AHK or Clipboard I/O."""

import gc
import struct
import unittest
import weakref

from f7hub.infrastructure import clipboard_native_io as io
from f7hub.infrastructure import clipboard_native_session as session


class Resource:
    pass


class Clock:
    tick = 1_000_000

    def __call__(self):
        return self.tick


def enrollment():
    generation = bytes(range(1, 17))
    context = struct.pack('<16sIQIQI32s32sI', generation, 100, 200, 300, 400,
                          1, bytes(32), bytes(32), 0x2000)
    identity = session.RetirementIdentity(generation, 300, 400, 0, generation, 0)
    return session.EnrollmentContext(identity, bytes(range(32)), context)


class NativeIOTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.context = enrollment()
        self.policy = session.NativeSessionPolicy(self.context, clock=self.clock,
                                                   frequency=1_000_000)
        self.ledger = session.RetirementLedger(self.context, clock=self.clock,
                                                frequency=1_000_000)
        self.closes = []

    def gate(self, policy=None, callback=None):
        def close():
            self.closes.append('close')
            return True
        return io.PostStartIOGate(policy or self.policy,
                                  close_handle=close if callback is None else callback)

    def rejected(self, call, *args, **kwargs):
        with self.assertRaises(io.NativeIOError) as caught:
            call(*args, **kwargs)
        self.assertEqual(str(caught.exception), 'NATIVE_IO_REJECTED')

    def ticket(self, gate, direction=io.Direction.READ):
        return gate.issue(direction, resources=(Resource(),))

    def test_retains_exact_policy_and_identity(self):
        gate = self.gate()
        self.assertIs(gate.policy, self.policy)
        self.assertIs(gate.identity, self.context.identity)
        self.assertFalse(gate.closed)
        self.assertFalse(gate.quarantined)

    def test_policy_retains_sole_owner_after_external_reference_is_dropped(self):
        gate = self.gate()
        ref = weakref.ref(gate)
        ticket = self.ticket(gate)
        del gate
        gc.collect()
        self.assertIsNotNone(ref())
        self.assertEqual(ref().pending_count, 1)
        self.rejected(self.gate)
        ref().observe_completion(ticket)
        ref().begin_retirement()
        ref().close()
        self.rejected(self.gate)  # Successful close cannot rebind either.

    def test_quarantined_owner_cannot_be_replaced(self):
        gate = self.gate(callback=lambda: False)
        gate.begin_retirement()
        self.rejected(gate.close)
        self.rejected(self.gate)
        self.assertIs(gate.policy, self.policy)

    def test_rejects_untrusted_policy_and_callback_types(self):
        for policy in (None, self.context, object()):
            self.rejected(io.PostStartIOGate, policy, close_handle=lambda: True)
        self.rejected(io.PostStartIOGate, self.policy, close_handle=True)

    def test_refuses_quarantined_policy(self):
        self.policy.begin_request(bytes(range(16)))
        with self.assertRaises(session.SessionPolicyError):
            self.policy.verify_handshake(b'', b'', b'', b'')
        self.rejected(io.PostStartIOGate, self.policy, close_handle=lambda: True)

    def test_two_bounded_direction_slots(self):
        gate = self.gate()
        read = self.ticket(gate)
        write = self.ticket(gate, io.Direction.WRITE)
        self.assertIsNot(read, write)
        self.assertEqual(gate.pending_count, 2)
        self.rejected(self.ticket, gate)
        self.assertEqual(gate.pending_count, 2)
        gate.observe_completion(read)
        replacement = self.ticket(gate)
        self.assertIsNot(replacement, read)

    def test_issue_requires_exact_direction_and_resource_tuple(self):
        gate = self.gate()
        for direction in ('read', True, 1, None):
            self.rejected(gate.issue, direction, resources=(Resource(),))
        for resources in ((), [], Resource(), None):
            self.rejected(gate.issue, io.Direction.READ, resources=resources)
        self.assertEqual(gate.pending_count, 0)

    def test_close_requires_retirement_fence(self):
        gate = self.gate()
        self.rejected(gate.close)
        self.assertEqual(self.closes, [])
        gate.begin_retirement()
        gate.close()
        self.assertEqual(self.closes, ['close'])

    def test_pending_each_direction_blocks_close(self):
        gate = self.gate()
        tickets = [self.ticket(gate, d) for d in io.Direction]
        gate.begin_retirement()
        for ticket in tickets:
            self.rejected(gate.close)
            self.assertEqual(self.closes, [])
            gate.observe_completion(ticket)
        gate.close()
        self.assertEqual(self.closes, ['close'])

    def test_cancellation_and_timeout_are_not_completion(self):
        gate = self.gate()
        ticket = self.ticket(gate)
        gate.begin_retirement()
        gate.observe_cancel_requested(ticket)
        gate.observe_cancel_requested(ticket)
        self.clock.tick += 100_000_000
        self.rejected(gate.close)
        self.assertEqual(gate.pending_count, 1)
        self.assertEqual(self.closes, [])
        gate.observe_completion(ticket)
        gate.close()
        self.assertTrue(gate.closed)

    def test_resources_retained_until_completion(self):
        gate = self.gate()
        resource = Resource()
        ref = weakref.ref(resource)
        ticket = gate.issue(io.Direction.READ, resources=(resource,))
        del resource
        gc.collect()
        self.assertIsNotNone(ref())
        gate.observe_cancel_requested(ticket)
        gc.collect()
        self.assertIsNotNone(ref())
        gate.observe_completion(ticket)
        gc.collect()
        self.assertIsNone(ref())

    def test_retirement_permanently_fences_new_work(self):
        gate = self.gate()
        gate.begin_retirement()
        gate.begin_retirement()
        self.rejected(self.ticket, gate)
        gate.close()
        self.rejected(self.ticket, gate)
        self.rejected(gate.close)
        self.assertEqual(self.closes, ['close'])

    def test_foreign_ticket_quarantines_without_dropping_pending(self):
        first, second = self.gate(), self.gate(self.ledger)
        ticket = self.ticket(first)
        self.rejected(second.observe_completion, ticket)
        self.assertTrue(second.quarantined)
        self.assertEqual(first.pending_count, 1)
        first.observe_completion(ticket)

    def test_stale_completion_quarantines(self):
        gate = self.gate()
        ticket = self.ticket(gate)
        gate.observe_completion(ticket)
        self.rejected(gate.observe_completion, ticket)
        self.assertTrue(gate.quarantined)
        self.rejected(gate.begin_retirement)

    def test_unknown_cancellation_quarantines(self):
        gate = self.gate()
        self.rejected(gate.observe_cancel_requested, object())
        self.assertTrue(gate.quarantined)

    def test_quarantine_retains_resources_and_allows_only_drain(self):
        gate = self.gate()
        resource = Resource()
        ref = weakref.ref(resource)
        ticket = gate.issue(io.Direction.WRITE, resources=(resource,))
        del resource
        self.rejected(gate.observe_completion, object())
        gc.collect()
        self.assertIsNotNone(ref())
        self.rejected(self.ticket, gate)
        gate.observe_completion(ticket)
        gc.collect()
        self.assertIsNone(ref())
        self.rejected(gate.close)
        self.assertEqual(self.closes, [])

    def test_non_true_close_results_quarantine_without_retry(self):
        for result in (False, None, 1, 'closed', session.IOObservation.COMPLETED):
            with self.subTest(result=result):
                calls = []
                def close():
                    calls.append(1)
                    return result
                policy = session.NativeSessionPolicy(self.context, clock=self.clock,
                                                       frequency=1_000_000)
                gate = self.gate(policy, callback=close)
                gate.begin_retirement()
                self.rejected(gate.close)
                self.assertTrue(gate.quarantined)
                self.assertFalse(gate.closed)
                self.rejected(gate.close)
                self.assertEqual(calls, [1])
                with self.assertRaises(session.SessionPolicyError):
                    policy.record_child_close(reason=1, outcome=3)

    def test_close_exception_is_safe_and_never_retried(self):
        calls = []
        def close():
            calls.append(1)
            raise OSError('synthetic untrusted detail')
        gate = self.gate(callback=close)
        gate.begin_retirement()
        self.rejected(gate.close)
        self.assertTrue(gate.quarantined)
        self.rejected(gate.close)
        self.assertEqual(calls, [1])

    def test_process_interruption_quarantines_and_preserves_interrupt(self):
        calls = []
        def close():
            calls.append(1)
            raise KeyboardInterrupt()
        gate = self.gate(callback=close)
        gate.begin_retirement()
        with self.assertRaises(KeyboardInterrupt):
            gate.close()
        self.assertTrue(gate.quarantined)
        self.rejected(gate.close)
        self.assertEqual(calls, [1])

    def test_close_attempt_consumed_before_reentrant_callback(self):
        calls = []
        def close():
            calls.append(1)
            self.rejected(gate.close)
            self.rejected(self.ticket, gate)
            return True
        gate = self.gate(callback=close)
        gate.begin_retirement()
        gate.close()
        self.assertEqual(calls, [1])
        self.assertTrue(gate.closed)

    def test_callback_cannot_publish_after_quarantine(self):
        def close():
            self.rejected(gate.observe_completion, object())
            return True
        gate = self.gate(callback=close)
        gate.begin_retirement()
        self.rejected(gate.close)
        self.assertTrue(gate.closed)
        self.assertTrue(gate.quarantined)
        with self.assertRaises(session.SessionPolicyError):
            self.policy.record_child_close(reason=1, outcome=3)

    def test_policy_quarantine_before_close_blocks_callback(self):
        gate = self.gate()
        gate.begin_retirement()
        self.policy.begin_request(bytes(range(16)))
        with self.assertRaises(session.SessionPolicyError):
            self.policy.verify_handshake(b'', b'', b'', b'')
        self.rejected(gate.close)
        self.assertEqual(self.closes, [])

    def test_child_close_and_app_close_still_require_mac_evidence(self):
        child, app = self.gate(), self.gate(self.ledger)
        child.begin_retirement()
        child.close()
        self.assertIs(self.policy.phase, session.Phase.POST_START)
        closed = self.policy.record_child_close(reason=1, outcome=3)
        self.assertIs(self.policy.phase, session.Phase.LOCAL_CLOSED)
        with self.assertRaises(session.SessionPolicyError):
            self.ledger.complete_retirement(bytes(range(16)), outcome=3)
        app.begin_retirement()
        app.close()
        with self.assertRaises(session.SessionPolicyError):
            self.ledger.complete_retirement(bytes(range(16)), outcome=3)
        self.ledger.receive_closed(closed)
        ack = self.ledger.complete_retirement(bytes(range(16)), outcome=3)
        self.assertTrue(self.policy.receive_retire_ack(ack))
        self.assertEqual(self.policy.receipt, self.ledger.receipt)
        self.assertEqual(len(self.closes), 2)
        self.rejected(child.close)
        self.rejected(app.close)
        self.rejected(io.PostStartIOGate, self.policy, close_handle=lambda: True)
        self.rejected(io.PostStartIOGate, self.ledger, close_handle=lambda: True)

    def test_authoritative_request_deadline_is_not_extended(self):
        gate = self.gate()
        self.policy.begin_request(bytes(range(16)))
        self.clock.tick += 500_000
        ticket = self.ticket(gate)
        gate.observe_completion(ticket)
        gate.begin_retirement()
        gate.close()  # Cleanup may outlive request; it cannot revive status.
        with self.assertRaises(session.SessionPolicyError) as caught:
            gate.policy.accept_status(b'')
        self.assertEqual(str(caught.exception), 'UNAVAILABLE')

    def test_gate_lifetime_preserves_consumed_closed_resend_allowance(self):
        gate = self.gate()
        first = (1).to_bytes(16, 'little')
        second = (2).to_bytes(16, 'little')
        query = (3).to_bytes(16, 'little')
        self.policy.begin_request(first)
        gate.begin_retirement()
        gate.close()
        closed = self.policy.record_child_close(reason=1, outcome=3)
        self.clock.tick += 500_000
        self.policy.begin_request(second)
        reply = self.ledger.reply_to_query(self.policy.make_state_query(query))
        self.assertEqual(self.policy.receive_state_reply(reply), 'PENDING')
        self.assertEqual(self.policy.claim_closed_retransmission(), closed)
        self.assertTrue(self.policy.resend_used)
        self.rejected(self.gate)
        self.rejected(gate.close)
        with self.assertRaises(session.SessionPolicyError):
            gate.policy.claim_closed_retransmission()
        self.assertTrue(gate.policy.resend_used)
        self.assertEqual(self.closes, ['close'])

    def test_replay_history_and_fail_closed_cap_remain_authoritative(self):
        gate = self.gate()
        for value in range(1, 4097):
            gate.policy.begin_request(value.to_bytes(16, 'little'))
            self.clock.tick += 500_000
        for value in (1, 2, 4096):
            with self.assertRaises(session.SessionPolicyError):
                gate.policy.begin_request(value.to_bytes(16, 'little'))
        self.assertFalse(gate.quarantined)
        with self.assertRaises(session.SessionPolicyError):
            gate.policy.begin_request((4097).to_bytes(16, 'little'))
        self.assertTrue(gate.quarantined)
        self.rejected(self.ticket, gate)
        self.assertIs(gate.policy, self.policy)


if __name__ == '__main__':
    unittest.main()
