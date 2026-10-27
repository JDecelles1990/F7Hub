"""Pure HBR-01 post-START authentication/status and retirement policy.

No transport, OS calls, Clipboard, persistence, workers or application wiring.
Construction requires an exact offer and a root/context supplied by a FUTURE
trusted enrollment adapter. This module cannot verify OS process pinning, key
delivery, physical press acceptance or native completion. Local observations
are that adapter's obligations, never peer-supplied authentication flags.

Actual transcript/control/frame MACs are checked here. Proof verification and
an observed complete ServerFinish write gate status admission; this is not an
end-to-end native handshake implementation. Each instance binds ONE offer,
has no successor-allocation API, and must not become a parallel offer owner.
PRESTART/ABANDON, initial readiness clocks and generation-wide allocation are
later adapter/ledger work. Returned bytes/permits describe decisions only.
"""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import hmac
import struct
from time import monotonic_ns

from . import clipboard_native_protocol as protocol


_U64 = 2**64 - 1
_MAX_REQUEST_IDS = 4096  # Fixed-offer lifetime cap; exhaustion quarantines, never evicts.
_ZERO = bytes(16)
_ACK = struct.Struct('<16sIQQ16sQB16s')
_QUERY = struct.Struct('<16s16sQ16sQ16sQQB')
_REPLY = struct.Struct('<16s16sIQQQ16sQBB16s')
_CLOSED = struct.Struct('<16sQ16sI')
_LENGTHS = {3: 88, 7: 84, 9: 121, 10: 141, 11: 146}


class SessionPolicyError(ValueError):
    """Fixed content-free denial; no source bytes or secret diagnostics."""


def _deny(code='NATIVE_SESSION_REJECTED'):
    raise SessionPolicyError(code)


def _uint(value, maximum=_U64):
    return type(value) is int and 0 <= value <= maximum


def _id(value):
    return type(value) is bytes and len(value) == 16 and value != _ZERO


def _mac(key, label, data):
    return hmac.digest(key, label + b'\0' + data, 'sha256')


class IOObservation(Enum):
    PENDING = 'pending'
    CANCEL_REQUESTED = 'cancel_requested'
    COMPLETED = 'completed'


class Phase(Enum):
    POST_START = 'post_start'
    PROOFS_VERIFIED = 'proofs_verified'
    ACTIVE = 'active'
    RETIRING = 'retiring'
    LOCAL_CLOSED = 'local_closed'
    RECEIPT_KNOWN = 'receipt_known'
    QUARANTINED = 'quarantined'


@dataclass(frozen=True, slots=True)
class RetirementIdentity:
    generation: bytes
    child_pid: int
    child_creation: int
    epoch: int
    offer_id: bytes
    owner_gen: int

    def __post_init__(self):
        if not _id(self.generation) or not _id(self.offer_id) \
                or not _uint(self.child_pid, 2**32 - 1) or not self.child_pid \
                or not _uint(self.child_creation) or not self.child_creation \
                or not _uint(self.epoch) or type(self.owner_gen) is not int \
                or self.owner_gen != self.epoch:
            _deny()
        if self.epoch == 0 and self.offer_id != self.generation:
            _deny()


@dataclass(frozen=True, slots=True)
class EnrollmentContext:
    """Trusted adapter inputs, not an assertion that OS enrollment occurred."""

    identity: RetirementIdentity
    root_key: bytes = field(repr=False)
    pinned_context: bytes = field(repr=False)
    previous_receipt_id: bytes = _ZERO
    previous_outcome: int = 255

    def __post_init__(self):
        if type(self.identity) is not RetirementIdentity \
                or type(self.root_key) is not bytes or len(self.root_key) != 32 \
                or type(self.pinned_context) is not bytes or len(self.pinned_context) != 112:
            _deny()
        r = self.identity
        if type(self.previous_outcome) is not int or self.previous_outcome not in (0, 1, 2, 3, 4, 255) \
                or type(self.previous_receipt_id) is not bytes or len(self.previous_receipt_id) != 16 \
                or (self.previous_receipt_id == _ZERO) != (self.previous_outcome == 255) \
                or (r.epoch == 0) != (self.previous_receipt_id == _ZERO):
            _deny()
        if self.pinned_context[:16] != r.generation \
                or struct.unpack_from('<IQ', self.pinned_context, 28) != (r.child_pid, r.child_creation) \
                or struct.unpack_from('<I', self.pinned_context, 108)[0] != 0x2000:
            _deny()


@dataclass(frozen=True, slots=True)
class RetirementReceipt:
    identity: RetirementIdentity
    outcome: int
    receipt_id: bytes


@dataclass(frozen=True, slots=True)
class StatusPermit:
    """Content-free policy result; authorizes no capture/service/native effect."""

    identity: RetirementIdentity
    session_id: bytes
    message_id: str


class _BoundPolicy:
    def __init__(self, enrollment, *, clock=monotonic_ns, frequency=1_000_000_000):
        if type(enrollment) is not EnrollmentContext or not callable(clock) \
                or not _uint(frequency) or frequency < 2:
            _deny()
        self._enrollment = enrollment
        self._clock = clock
        self._frequency = frequency
        self._last_tick = 0
        self._quarantined = False
        self._now()

    @property
    def quarantined(self):
        return self._quarantined

    @property
    def identity(self):
        return self._enrollment.identity

    def _reject(self):
        self._quarantined = True
        _deny()

    def _healthy(self):
        if self._quarantined:
            _deny()

    def _now(self):
        try:
            tick = self._clock()
        except Exception:
            self._reject()
        if not _uint(tick) or tick < self._last_tick:
            self._reject()
        self._last_tick = tick
        return tick

    def _sign(self, kind, body):
        header = b'F7H01CTL' + bytes((1, kind)) + struct.pack('<H', len(body) + 44)
        return header + body + _mac(self._enrollment.root_key, b'F7H01CTL/mac', header + body)

    def _verify(self, raw, kind):
        self._healthy()
        if type(raw) is not bytes or len(raw) != _LENGTHS[kind] \
                or raw[:10] != b'F7H01CTL' + bytes((1, kind)) \
                or struct.unpack_from('<H', raw, 10)[0] != len(raw) \
                or not hmac.compare_digest(raw[-32:], _mac(self._enrollment.root_key,
                                                          b'F7H01CTL/mac', raw[:-32])):
            self._reject()
        if raw[12:28] != self.identity.generation:
            self._reject()
        return raw[12:-32]


class NativeSessionPolicy(_BoundPolicy):
    """One child offer's proof/status gate and post-START B1/B2 policy.

    No public API accepts decoded/unverified peer messages or a boolean
    'authenticated' claim. All received evidence is exact MACed bytes.
    A caller that controls trusted enrollment or local observations is outside
    this pure boundary; production must supply them from its owning adapter.
    """

    def __init__(self, enrollment, **kwargs):
        super().__init__(enrollment, **kwargs)
        self._phase = Phase.POST_START
        self._attempted = False
        self._request_id = None
        self._previous_request = None
        self._accepted_request_ids = set()
        self._deadline = 0
        self._request_done = True
        self._query_id = None
        self._last_query_id = None
        self._resend_eligible = False
        self._resend_used = False
        self._child_io_complete = False
        self._closed = None
        self._closed_request_id = None
        self._outcome = None
        self._close_requested = False
        self._receipt = None
        self._c2s_key = None
        self._session_id = None
        self._sequence = 1
        self._last_activity = 0

    @property
    def phase(self):
        return Phase.QUARANTINED if self.quarantined else self._phase

    @property
    def receipt(self):
        return self._receipt

    @property
    def resend_used(self):
        return self._resend_used

    def begin_request(self, request_id):
        self._healthy()
        now = self._now()
        if not _id(request_id) or request_id in self._accepted_request_ids:
            _deny()
        if not self._request_done and now < self._deadline:
            _deny('BUSY')
        if now > _U64 - self._frequency // 2:
            self._reject()
        if len(self._accepted_request_ids) >= _MAX_REQUEST_IDS:
            self._reject()
        self._accepted_request_ids.add(request_id)
        self._previous_request = self._request_id
        self._request_id = request_id
        self._deadline = now + self._frequency // 2
        self._request_done = False
        self._query_id = None
        self._resend_eligible = False

    def _live(self):
        self._healthy()
        if self._request_done or self._now() >= self._deadline:
            _deny('UNAVAILABLE')

    def verify_handshake(self, client_hello, server_hello, client_finish, server_finish):
        """Verify one complete fixed transcript; native delivery is not inferred."""
        self._live()
        if self._phase is not Phase.POST_START or self._attempted:
            self._reject()
        self._attempted = True
        messages = (client_hello, server_hello, client_finish, server_finish)
        for kind, (raw, size) in enumerate(zip(messages, (156, 188, 44, 44)), 1):
            if type(raw) is not bytes or len(raw) != size \
                    or raw[:12] != b'F7H01C01' + bytes((1, kind)) + struct.pack('<H', size):
                self._reject()
        ch, sh, cf, sf = messages
        if ch[12:124] != self._enrollment.pinned_context or sh[12:124] != ch[12:124] \
                or ch[124:] == bytes(32) or sh[124:156] == bytes(32) \
                or ch[124:] == sh[124:156]:
            self._reject()
        r = self.identity
        key = self._enrollment.root_key
        if r.epoch:
            key = _mac(key, b'F7H01C01/epoch-key', struct.pack('<Q', r.epoch) + r.offer_id)
        sh0 = sh[:156]
        if not hmac.compare_digest(sh[156:], _mac(key, b'F7H01C01/server-proof', ch + sh0)) \
                or not hmac.compare_digest(cf[12:], _mac(key, b'F7H01C01/client-proof', ch + sh0 + sh[156:])) \
                or not hmac.compare_digest(sf[12:], _mac(key, b'F7H01C01/server-finish', ch + sh0 + sh[156:] + cf)):
            self._reject()
        salt = hashlib.sha256(b'F7H01C01/salt\0' + ch + sh0).digest()
        prk = hmac.digest(salt, key, 'sha256')
        base = b'F7H01C01/session\0' + hashlib.sha256(ch + sh + cf + sf).digest()
        self._c2s_key = hmac.digest(prk, base + b'/client-to-server\0\x01', 'sha256')
        self._session_id = hmac.digest(prk, base + b'/session-id\0\x01', 'sha256')[:16]
        self._live()
        self._phase = Phase.PROOFS_VERIFIED

    def observe_server_finish_write(self, observation):
        self._live()
        if self._phase is not Phase.PROOFS_VERIFIED or type(observation) is not IOObservation:
            self._reject()
        if observation is IOObservation.COMPLETED:
            self._live()
            self._phase = Phase.ACTIVE
            self._last_activity = self._last_tick

    def accept_status(self, raw):
        self._live()
        if self._phase is not Phase.ACTIVE:
            _deny('UNAVAILABLE')
        if self._now() - self._last_activity >= 30 * self._frequency:
            self._phase = Phase.RETIRING
            self._c2s_key = None
            _deny('UNAVAILABLE')
        try:
            frame = protocol.unpack_frame(raw)
        except protocol.NativeProtocolError:
            self._reject()
        expected = _mac(self._c2s_key, b'F7H01C01/frame', self._session_id + b'\x01\x01' + raw[:-32])
        if not hmac.compare_digest(frame.mac, expected) or frame.sequence != self._sequence:
            self._reject()
        try:
            message = protocol.decode_message(frame.document, expected_producer='ahk.clipboard')
        except protocol.NativeProtocolError:
            self._reject()
        if message.contract != 'clipboard.native_status' or message.message_class != 'QUERY':
            self._reject()
        permit = StatusPermit(self.identity, self._session_id, message.message_id)
        self._live()
        self._sequence += 1
        if self._sequence > _U64:
            self._phase = Phase.RETIRING
            self._c2s_key = None
        self._last_activity = self._last_tick
        self._request_done = True
        return permit

    def observe_child_io(self, observation):
        self._healthy()
        if type(observation) is not IOObservation:
            self._reject()
        if observation is IOObservation.COMPLETED:
            self._child_io_complete = True

    def receive_close_request(self, raw):
        _, epoch, offer = struct.unpack('<16sQ16s', self._verify(raw, 7))
        if (epoch, offer) != (self.identity.epoch, self.identity.offer_id):
            self._reject()
        self._close_requested = True  # Advisory only; proves no completion.

    def record_child_close(self, *, reason, outcome):
        """Record actual adapter-observed close ONCE; return original CLOSED.

        Must be called only after the real child close is observed. This method
        never calls CloseHandle or requests cancellation. No success is inferred
        from a peer message or a cancellation return value.
        """
        self._healthy()
        if self._closed is not None or not self._child_io_complete \
                or self._phase not in (Phase.POST_START, Phase.PROOFS_VERIFIED, Phase.ACTIVE, Phase.RETIRING) \
                or type(reason) is not int or type(outcome) is not int \
                or (reason, outcome) not in ((0, 0), (1, 3), (2, 0), (2, 3)):
            _deny()
        if (reason == 0 and (self._phase not in (Phase.ACTIVE, Phase.RETIRING)
                            or self._now() - self._last_activity < 30 * self._frequency)) \
                or (reason == 2 and not self._close_requested) \
                or (outcome == 0 and self._phase not in (Phase.ACTIVE, Phase.RETIRING)):
            _deny()
        r = self.identity
        self._closed = self._sign(3, _CLOSED.pack(r.generation, r.epoch, r.offer_id, reason))
        self._closed_request_id = self._request_id  # Recovery requires acceptance after this close.
        self._outcome = outcome
        self._c2s_key = None
        self._phase = Phase.LOCAL_CLOSED
        return self._closed

    def _adopt(self, pid, creation, epoch, offer, owner, outcome, receipt_id):
        r = self.identity
        if epoch < r.epoch:  # An older offer cannot advance this fixed-offer policy.
            _deny()
        if (pid, creation, epoch, offer, owner) != (r.child_pid, r.child_creation, r.epoch, r.offer_id, r.owner_gen):
            self._reject()
        if outcome not in (0, 3) or type(outcome) is not int or not _id(receipt_id) \
                or outcome != self._outcome:
            self._reject()
        receipt = RetirementReceipt(r, outcome, receipt_id)
        if self._receipt is not None:
            if self._receipt != receipt:
                self._reject()
            return False
        if self._phase is not Phase.LOCAL_CLOSED or not self._child_io_complete or self._closed is None:
            _deny()
        self._receipt = receipt
        self._phase = Phase.RECEIPT_KNOWN
        self._resend_eligible = False
        return True

    def receive_retire_ack(self, raw):
        """Direct ACK can bookkeep after expiry; it never revives a request."""
        _, *fields = _ACK.unpack(self._verify(raw, 9))
        return self._adopt(*fields)

    def make_state_query(self, query_id):
        self._live()
        if self._phase is not Phase.LOCAL_CLOSED or not _id(query_id) \
                or self._request_id == self._closed_request_id \
                or self._query_id is not None or query_id == self._last_query_id:
            _deny()
        self._query_id = query_id
        self._last_query_id = query_id
        r = self.identity
        query = self._sign(10, _QUERY.pack(r.generation, query_id, r.epoch, r.offer_id,
                                         r.owner_gen, self._enrollment.previous_receipt_id,
                                         self._deadline, self._frequency, 3))
        self._live()
        return query

    def receive_state_reply(self, raw):
        self._live()  # Expired replies cannot be retained for the next request.
        values = _REPLY.unpack(self._verify(raw, 11))
        _, query, pid, creation, highwater, epoch, offer, owner, state, outcome, receipt_id = values
        if self._query_id is None or query != self._query_id:
            _deny()
        r = self.identity
        if epoch < r.epoch:
            _deny()
        if (pid, creation, epoch, offer, owner, highwater) != (r.child_pid, r.child_creation, r.epoch,
                                                            r.offer_id, r.owner_gen, r.epoch):
            self._reject()
        if state not in (0, 1, 2, 3) or outcome not in (0, 1, 2, 3, 4, 255) \
                or (receipt_id == _ZERO) != (outcome == 255):
            self._reject()
        if state in (1, 2) and (receipt_id, outcome) != (self._enrollment.previous_receipt_id,
                                                       self._enrollment.previous_outcome):
            self._reject()
        self._live()
        if state == 0:
            self._adopt(pid, creation, epoch, offer, owner, outcome, receipt_id)
            return 'RECEIPT_KNOWN'
        self._resend_eligible = state == 1 and self._phase is Phase.LOCAL_CLOSED
        return 'PENDING' if state == 1 else 'UNAVAILABLE'

    def claim_closed_retransmission(self):
        """Consume before returning bytes, even if adapter delivery later fails."""
        self._live()
        if self._phase is not Phase.LOCAL_CLOSED or self._closed is None \
                or not self._child_io_complete or self._receipt is not None \
                or self._request_id == self._closed_request_id \
                or self._query_id is None or not self._resend_eligible or self._resend_used:
            _deny('UNAVAILABLE')
        self._resend_used = True
        self._resend_eligible = False
        return self._closed


class RetirementLedger(_BoundPolicy):
    """App's separate fixed-offer post-START retirement evidence.

    Positive app-I/O and server-close observations must come from the app's
    own adapter. A child CLOSED/query can never stand in for either fact.
    The caller injects a fresh random receipt ID; the ledger never replaces it.
    """

    def __init__(self, enrollment, **kwargs):
        super().__init__(enrollment, **kwargs)
        self._app_io_complete = False
        self._server_closed = False
        self._closed = None
        self._reason = None
        self._receipt = None
        self._query = None
        self._confirmation_used = False

    @property
    def receipt(self):
        return self._receipt

    def observe_app_io(self, observation):
        self._healthy()
        if type(observation) is not IOObservation:
            self._reject()
        if observation is IOObservation.COMPLETED:
            self._app_io_complete = True

    def record_server_close(self):
        self._healthy()
        if not self._app_io_complete or self._server_closed:
            _deny()
        self._server_closed = True

    def receive_closed(self, raw):
        _, epoch, offer, reason = _CLOSED.unpack(self._verify(raw, 3))
        if (epoch, offer) != (self.identity.epoch, self.identity.offer_id) or reason not in (0, 1, 2):
            self._reject()
        if self._closed is not None:
            if self._closed != raw:
                self._reject()
            return False  # Delayed original and resend are one immutable fact.
        self._closed = raw
        self._reason = reason
        return True

    def complete_retirement(self, receipt_id, *, outcome):
        self._healthy()
        if not self._app_io_complete or not self._server_closed or self._closed is None:
            _deny('UNAVAILABLE')
        if not _id(receipt_id) or type(outcome) is not int \
                or (self._reason, outcome) not in ((0, 0), (1, 3), (2, 0), (2, 3)):
            self._reject()
        receipt = RetirementReceipt(self.identity, outcome, receipt_id)
        if self._receipt is not None:
            if self._receipt != receipt:
                self._reject()
            return None
        self._receipt = receipt
        return self._ack()  # Initial cleanup ACK; may follow request expiry.

    def _ack(self):
        r = self.identity
        return self._sign(9, _ACK.pack(r.generation, r.child_pid, r.child_creation, r.epoch,
                                      r.offer_id, r.owner_gen, self._receipt.outcome,
                                      self._receipt.receipt_id))

    def reply_to_query(self, raw):
        _, query_id, epoch, offer, owner, observed_receipt, deadline, frequency, child_state = \
            _QUERY.unpack(self._verify(raw, 10))
        r = self.identity
        if not _id(query_id) or (epoch, offer, owner) != (r.epoch, r.offer_id, r.owner_gen) \
                or child_state != 3 or observed_receipt != self._enrollment.previous_receipt_id \
                or frequency != self._frequency:
            self._reject()
        now = self._now()
        if not now < deadline or deadline - now > self._frequency // 2:
            _deny('UNAVAILABLE')
        if self._query is not None:
            old_id, old_deadline = self._query
            if old_id == query_id:
                return None
            if now < old_deadline:
                _deny('BUSY')
        self._query = (query_id, deadline)
        self._confirmation_used = False
        receipt = self._receipt
        outcome = receipt.outcome if receipt else self._enrollment.previous_outcome
        receipt_id = receipt.receipt_id if receipt else self._enrollment.previous_receipt_id
        reply = self._sign(11, _REPLY.pack(r.generation, query_id, r.child_pid, r.child_creation,
                                          r.epoch, r.epoch, r.offer_id, r.owner_gen,
                                          0 if receipt else 1, outcome, receipt_id))
        if self._now() >= deadline:
            _deny('UNAVAILABLE')
        return reply

    def claim_recovery_confirmation(self):
        self._healthy()
        if self._receipt is None or self._query is None or self._confirmation_used \
                or self._now() >= self._query[1]:
            _deny('UNAVAILABLE')
        self._confirmation_used = True
        result = self._ack()
        if self._now() >= self._query[1]:
            _deny('UNAVAILABLE')
        return result
