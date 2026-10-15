"""Inert Clipboard snapshot 1.0 boundary DTOs; no transport or privacy authority.

Byte limits cover the complete JSON document, including surrounding whitespace.
Transport framing is deliberately absent. Binding checks compare caller-supplied
identities only; they do not authenticate a process, authorize viewing, track
replays, or enforce the future 60-second application lifetime.
"""

from dataclasses import dataclass, field
from datetime import datetime
import json
import re


VERSION = '1.0'
REQUEST_CONTRACT = 'clipboard.snapshot_read'
RESULT_CONTRACT = 'clipboard.snapshot_read_result'
ERROR_CONTRACT = 'contract.error'
REQUEST_COMPONENT = 'f7hub.clipboard'
REPLY_COMPONENT = 'ahk.clipboard'
MAX_ORDINARY_BYTES = 16 * 1024
MAX_RESULT_BYTES = 128 * 1024
MAX_TEXT_BYTES = 65_536
FUTURE_SNAPSHOT_LIFETIME_SECONDS = 60
MAX_DEPTH = 4
MAX_MEMBERS = 16
MAX_NODES = 128
STATUSES = frozenset(('SUCCESS', 'EMPTY', 'DENIED', 'UNAVAILABLE', 'TIMED_OUT',
                      'FAILED', 'UNSUPPORTED', 'TOO_LARGE', 'LOCKED', 'UNSTABLE'))
ERROR_CODES = frozenset(('CONTRACT_VALIDATION_FAILED', 'UNSUPPORTED_VERSION',
                        'UNKNOWN_CONTRACT', 'AUTHORIZATION_DENIED',
                        'EXECUTION_BOUNDARY_FAILED', 'TIMEOUT',
                        'PAYLOAD_LIMIT_EXCEEDED', 'PROVIDER_UNAVAILABLE',
                        'INTERNAL_ERROR'))
SAFE_ERROR_MESSAGE = 'The snapshot request failed.'
_UUID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z')
_TIME = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z\Z')
_ENVELOPE = frozenset(('contract', 'schema_version', 'message_class', 'message_id',
                       'created_at', 'producer', 'payload'))
_BINDING = frozenset(('operation_id', 'admission_generation', 'producer_binding'))


class ProtocolError(ValueError):
    """Content-free rejection. Only module-owned classification is exposed."""


def _fail():
    raise ProtocolError('SNAPSHOT_PROTOCOL_REJECTED')


def _uuid(value):
    if type(value) is not str or _UUID.fullmatch(value) is None:
        _fail()


def _timestamp(value):
    if type(value) is not str or _TIME.fullmatch(value) is None:
        _fail()
    valid = False
    try:
        datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
        valid = True
    except ValueError:
        pass
    if not valid:
        _fail()


def _string(value):
    if type(value) is not str:
        _fail()
    # Preserve TAB/LF/CR; reject other C0, DEL/C1 and all surrogate code points.
    if any((ord(c) < 32 and c not in '\t\n\r') or 127 <= ord(c) <= 159
           or 0xD800 <= ord(c) <= 0xDFFF for c in value):
        _fail()


def _closed(value, required, optional=frozenset()):
    if type(value) is not dict or not required <= value.keys() or not value.keys() <= required | optional:
        _fail()


@dataclass(frozen=True, slots=True)
class SnapshotBinding:
    """Opaque UUIDs supplied by a future caller, never proof of enrollment."""

    admission_generation: str
    producer_binding: str

    def __post_init__(self):
        _uuid(self.admission_generation)
        _uuid(self.producer_binding)


@dataclass(frozen=True, slots=True)
class SnapshotHeader:
    contract: str
    message_class: str
    message_id: str
    created_at: str
    producer_component: str
    correlation_id: str | None = None

    def __post_init__(self):
        _uuid(self.message_id)
        _timestamp(self.created_at)
        expected = {
            REQUEST_CONTRACT: ('COMMAND', REQUEST_COMPONENT),
            RESULT_CONTRACT: ('RESULT', REPLY_COMPONENT),
            ERROR_CONTRACT: ('ERROR', REPLY_COMPONENT),
        }
        if type(self.contract) is not str or self.contract not in expected:
            _fail()
        if (type(self.message_class) is not str or type(self.producer_component) is not str
                or (self.message_class, self.producer_component) != expected[self.contract]):
            _fail()
        if self.contract == REQUEST_CONTRACT:
            if self.correlation_id is not None:
                _fail()
        else:
            _uuid(self.correlation_id)
            if self.message_id == self.correlation_id:
                _fail()


@dataclass(frozen=True, slots=True)
class SnapshotRequest:
    header: SnapshotHeader
    operation_id: str
    binding: SnapshotBinding

    def __post_init__(self):
        if type(self.header) is not SnapshotHeader or self.header.contract != REQUEST_CONTRACT:
            _fail()
        _uuid(self.operation_id)
        if type(self.binding) is not SnapshotBinding:
            _fail()


@dataclass(frozen=True, slots=True)
class SnapshotResult:
    header: SnapshotHeader
    operation_id: str
    binding: SnapshotBinding
    status: str
    observed_at: str | None = None
    text: str | None = field(default=None, repr=False)

    def __post_init__(self):
        if type(self.header) is not SnapshotHeader or self.header.contract != RESULT_CONTRACT:
            _fail()
        _uuid(self.operation_id)
        if type(self.binding) is not SnapshotBinding or type(self.status) is not str or self.status not in STATUSES:
            _fail()
        if self.status == 'SUCCESS':
            _timestamp(self.observed_at)
            _string(self.text)
            if not self.text or len(self.text.encode('utf-8')) > MAX_TEXT_BYTES:
                _fail()
        elif self.observed_at is not None or self.text is not None:
            _fail()


@dataclass(frozen=True, slots=True)
class SnapshotError:
    """A narrow supported subset of Foundation contract.error 1.0."""

    header: SnapshotHeader
    code: str
    retryable: bool | None = None

    def __post_init__(self):
        if type(self.header) is not SnapshotHeader or self.header.contract != ERROR_CONTRACT:
            _fail()
        if type(self.code) is not str or self.code not in ERROR_CODES:
            _fail()
        if self.retryable is not None and type(self.retryable) is not bool:
            _fail()


def _unique(pairs):
    if len(pairs) > MAX_MEMBERS:
        _fail()
    value = {}
    for key, item in pairs:
        if key in value:
            _fail()
        value[key] = item
    return value


def _integer(value):
    # This profile has no numeric payload fields. Bound numeric parsing first.
    if len(value) > 16:
        _fail()
    result = int(value)
    if abs(result) > 2**53 - 1:
        _fail()
    return result


def _no_number(_):
    _fail()


def _parse(raw):
    if type(raw) is not bytes or len(raw) > MAX_RESULT_BYTES:
        _fail()
    source = None
    try:
        source = raw.decode('utf-8', errors='strict')
    except UnicodeError:
        pass
    # Raise outside the except block: do not retain a raw decode exception.
    if source is None or source.startswith('\ufeff'):
        _fail()
    depth = 0
    quoted = escaped = False
    for char in source:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '{[':
            depth += 1
            if depth > MAX_DEPTH:
                _fail()
        elif char in '}]':
            depth -= 1
            if depth < 0:
                _fail()
    value = None
    try:
        value = json.loads(source, object_pairs_hook=_unique, parse_int=_integer,
                           parse_float=_no_number, parse_constant=_no_number)
    except (ValueError, RecursionError):
        pass
    # json.JSONDecodeError holds its source document; do not chain/retain it.
    if type(value) is not dict:
        _fail()
    pending = [value]
    nodes = 0
    while pending:
        item = pending.pop()
        nodes += 1
        if nodes > MAX_NODES:
            _fail()
        if type(item) is dict:
            pending.extend(item.keys())
            pending.extend(item.values())
        elif type(item) is list:
            # No arrays are declared anywhere in this narrow profile.
            _fail()
        elif type(item) is str:
            _string(item)
    return value


def _header(value, contract, message_class):
    reply = contract != REQUEST_CONTRACT
    _closed(value, _ENVELOPE | ({'correlation_id'} if reply else set()))
    _closed(value['producer'], {'component'})
    if (type(value['contract']) is not str or value['contract'] != contract
            or type(value['schema_version']) is not str or value['schema_version'] != VERSION
            or type(value['message_class']) is not str or value['message_class'] != message_class):
        _fail()
    return SnapshotHeader(contract, message_class, value['message_id'], value['created_at'],
                          value['producer']['component'], value.get('correlation_id'))


def _binding(payload):
    return SnapshotBinding(payload['admission_generation'], payload['producer_binding'])


def _current(request, binding):
    if type(request) is not SnapshotRequest or type(binding) is not SnapshotBinding or request.binding != binding:
        _fail()


def decode_request(raw: bytes, *, binding: SnapshotBinding) -> SnapshotRequest:
    if type(raw) is not bytes or len(raw) > MAX_ORDINARY_BYTES:
        _fail()
    value = _parse(raw)
    header = _header(value, REQUEST_CONTRACT, 'COMMAND')
    payload = value['payload']
    _closed(payload, _BINDING)
    request = SnapshotRequest(header, payload['operation_id'], _binding(payload))
    _current(request, binding)
    return request


def decode_result(raw: bytes, *, request: SnapshotRequest, binding: SnapshotBinding) -> SnapshotResult:
    _current(request, binding)
    value = _parse(raw)
    header = _header(value, RESULT_CONTRACT, 'RESULT')
    payload = value['payload']
    _closed(payload, _BINDING | {'status'}, {'observed_at', 'format', 'text'})
    if type(payload['status']) is not str or payload['status'] not in STATUSES:
        _fail()
    if payload['status'] == 'SUCCESS':
        _closed(payload, _BINDING | {'status', 'observed_at', 'format', 'text'})
        if type(payload['format']) is not str or payload['format'] != 'text/plain':
            _fail()
    else:
        _closed(payload, _BINDING | {'status'})
    result = SnapshotResult(header, payload['operation_id'], _binding(payload), payload['status'],
                            payload.get('observed_at'), payload.get('text'))
    if (header.correlation_id != request.header.message_id or result.operation_id != request.operation_id
            or result.binding != binding):
        _fail()
    return result


def decode_error(raw: bytes, *, request: SnapshotRequest, binding: SnapshotBinding) -> SnapshotError:
    _current(request, binding)
    if type(raw) is not bytes or len(raw) > MAX_ORDINARY_BYTES:
        _fail()
    value = _parse(raw)
    header = _header(value, ERROR_CONTRACT, 'ERROR')
    payload = value['payload']
    _closed(payload, {'code', 'message'}, {'retryable'})
    if type(payload['message']) is not str or payload['message'] != SAFE_ERROR_MESSAGE:
        _fail()
    if 'retryable' in payload and type(payload['retryable']) is not bool:
        _fail()
    error = SnapshotError(header, payload['code'], payload.get('retryable'))
    if header.correlation_id != request.header.message_id:
        _fail()
    return error


def encode(message: SnapshotRequest | SnapshotResult | SnapshotError) -> bytes:
    """Validate outgoing DTO shape and size; return unframed UTF-8 JSON bytes."""
    if type(message) not in (SnapshotRequest, SnapshotResult, SnapshotError):
        _fail()
    h = message.header
    if type(message) is SnapshotError:
        payload = {'code': message.code, 'message': SAFE_ERROR_MESSAGE}
        if message.retryable is not None:
            payload['retryable'] = message.retryable
    else:
        payload = {'operation_id': message.operation_id,
                   'admission_generation': message.binding.admission_generation,
                   'producer_binding': message.binding.producer_binding}
        if type(message) is SnapshotResult:
            payload['status'] = message.status
            if message.status == 'SUCCESS':
                payload.update(observed_at=message.observed_at, format='text/plain', text=message.text)
    value = {'contract': h.contract, 'schema_version': VERSION, 'message_class': h.message_class,
             'message_id': h.message_id, 'created_at': h.created_at,
             'producer': {'component': h.producer_component}, 'payload': payload}
    if h.correlation_id is not None:
        value['correlation_id'] = h.correlation_id
    raw = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')
    limit = MAX_RESULT_BYTES if type(message) is SnapshotResult else MAX_ORDINARY_BYTES
    if len(raw) > limit:
        _fail()
    return raw
