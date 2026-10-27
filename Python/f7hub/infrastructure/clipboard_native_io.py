"""Dormant HBR-01N post-START, fixed-offer local I/O retirement gate.

No Windows calls, transport, timers, threads, dispatch or application wiring.
One trusted, serialized issuing-process adapter must retain this gate and its
supplied HBR-01 policy for the entire offer lifetime, including quarantine.
It must bind close_handle to the exact retained handle/process/offer identity.
Peer messages, cancellation returns and timeouts are NOT local completion.

The future adapter owns native completion verification and bounded supervision;
this gate cannot establish either. Resources supplied at issue time stay alive
until positive local completion, including during cancellation/quarantine.
PRESTART remote-close authority and control-channel I/O are outside this gate.
"""

from enum import Enum

from .clipboard_native_session import (
    IOObservation, NativeSessionPolicy, Phase, RetirementLedger, SessionPolicyError,
)


class NativeIOError(ValueError):
    """Fixed content-free local adapter rejection."""


class Direction(Enum):
    READ = 'read'
    WRITE = 'write'


class PostStartIOGate:
    """One READ and one WRITE slot, then one irreversible local close attempt.

    Construction and every observation are trusted local adapter operations,
    never wire ingress. Calls must be serialized by that owner. This object
    neither constructs nor replaces a policy and has no reopen/reset API.
    Child close reason/outcome and CLOSED emission remain separate policy work.
    """

    def __init__(self, policy, *, close_handle):
        if type(policy) not in (NativeSessionPolicy, RetirementLedger) \
                or not callable(close_handle) or policy.quarantined:
            raise NativeIOError('NATIVE_IO_REJECTED')
        if type(policy) is NativeSessionPolicy and policy.phase not in (
                Phase.POST_START, Phase.PROOFS_VERIFIED, Phase.ACTIVE, Phase.RETIRING):
            raise NativeIOError('NATIVE_IO_REJECTED')
        if type(policy) is RetirementLedger and policy.receipt is not None:
            raise NativeIOError('NATIVE_IO_REJECTED')
        self._policy = policy
        self._close_handle = close_handle
        self._pending = {}
        self._retiring = False
        self._close_attempted = False
        self._closed = False
        self._quarantined = False
        try:
            policy._retain_io_owner(self)
        except SessionPolicyError:
            raise NativeIOError('NATIVE_IO_REJECTED') from None

    @property
    def policy(self):
        """The original authoritative instance; replay/resend state stays here."""
        return self._policy

    @property
    def identity(self):
        return self._policy.identity

    @property
    def pending_count(self):
        return len(self._pending)

    @property
    def closed(self):
        """Exact True observed from the trusted local close callback."""
        return self._closed

    @property
    def quarantined(self):
        return self._quarantined or self._policy.quarantined

    def _reject(self):
        raise NativeIOError('NATIVE_IO_REJECTED')

    def _healthy(self):
        if self.quarantined:
            self._reject()

    def issue(self, direction, *, resources):
        """Reserve BEFORE native issue; retain buffer/operation resources.

        The caller must report completion even for synchronous completion or
        known issue failure with no pending OS use. An uncertain issue remains
        pending. This method does not issue any native I/O itself.
        """
        self._healthy()
        if self._retiring or type(direction) is not Direction \
                or direction in self._pending \
                or type(resources) is not tuple or not resources:
            self._reject()
        ticket = object()
        self._pending[direction] = (ticket, resources, IOObservation.PENDING)
        return ticket

    def _slot(self, ticket):
        for direction, entry in self._pending.items():
            if ticket is entry[0]:
                return direction, entry
        self._quarantined = True
        self._reject()

    def observe_cancel_requested(self, ticket):
        """Record advisory cancellation; retain the slot and its resources."""
        direction, (token, resources, _) = self._slot(ticket)
        self._pending[direction] = (token, resources, IOObservation.CANCEL_REQUESTED)

    def observe_completion(self, ticket):
        """Positive issuing-process completion, including failed/cancelled I/O.

        Draining remains possible in quarantine, without restoring admission
        or close authority. A duplicate/stale/foreign ticket quarantines.
        """
        direction, _ = self._slot(ticket)
        del self._pending[direction]

    def begin_retirement(self):
        """Permanently fence new I/O before draining outstanding operations."""
        self._healthy()
        self._retiring = True

    def close(self):
        """Attempt exact local close once, only after fenced I/O has drained.

        A callback must return exact True only after positive native closure.
        False, exception or uncertain completion quarantines; there is no retry
        by numeric handle. No cancellation or peer observation can reach this
        callback while a local operation remains pending.
        """
        self._healthy()
        if not self._retiring or self._pending or self._close_attempted:
            self._reject()
        self._close_attempted = True  # Consume before callback, including reentry.
        try:
            result = self._close_handle()
        except Exception:
            self._quarantined = True
            raise NativeIOError('NATIVE_IO_REJECTED') from None
        except BaseException:
            self._quarantined = True
            raise  # Preserve process interruption while fencing uncertain close.
        if result is not True:
            self._quarantined = True
            self._reject()
        self._closed = True
        self._healthy()  # Callback reentry cannot publish quarantined evidence.
        try:
            if type(self._policy) is NativeSessionPolicy:
                self._policy.observe_child_io(IOObservation.COMPLETED)
            else:
                self._policy.observe_app_io(IOObservation.COMPLETED)
                self._policy.record_server_close()
        except SessionPolicyError:
            self._quarantined = True
            raise NativeIOError('NATIVE_IO_REJECTED') from None
