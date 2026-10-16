"""Inert H01 native Clipboard 1.0 wire contracts.

This module validates documents and models a frame's byte layout. It does not
authenticate frames, manage a session, access the Clipboard, or dispatch work.
Transport code must authenticate the frame before calling ``decode_message``.
"""

from dataclasses import dataclass, field
from datetime import datetime
import json
import re
import struct
from types import MappingProxyType
from typing import Mapping


VERSION = '1.0'
MAX_ORDINARY_BYTES = 16_384
MAX_CONTENT_BYTES = 131_072
MAX_TEXT_BYTES = 65_536
MAX_FRAME_BYTES = MAX_CONTENT_BYTES + 44
MAX_DEPTH = 6
MAX_MEMBERS = 16
MAX_NODES = 128
SAFE_ERROR_MESSAGE = 'The native Clipboard request failed.'
ERROR_CODES = frozenset(('CONTRACT_VALIDATION_FAILED', 'UNSUPPORTED_VERSION',
                         'UNKNOWN_CONTRACT', 'AUTHORIZATION_DENIED',
                         'EXECUTION_BOUNDARY_FAILED', 'TIMEOUT',
                         'PAYLOAD_LIMIT_EXCEEDED', 'PROVIDER_UNAVAILABLE',
                         'INTERNAL_ERROR'))
_UUID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z')
_TIME = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z\Z')
_DECIMAL = re.compile(r'[1-9][0-9]{0,18}\Z')
_ENVELOPE = frozenset(('contract', 'schema_version', 'message_class', 'message_id',
                       'created_at', 'producer', 'payload'))
_OBSERVED = frozenset(('NOT_ATTEMPTED', 'SUCCESS', 'DENIED', 'FAILED', 'UNCERTAIN'))
_STATUS = frozenset(('READY', 'SUCCESS', 'DENIED', 'UNAVAILABLE', 'BUSY', 'FAILED',
                     'TIMED_OUT', 'UNCERTAIN', 'NOT_FOUND', 'REPLAYED'))


class NativeProtocolError(ValueError):
    """Safe rejection with no reflected source bytes or parser exception."""


def _fail():
    raise NativeProtocolError('NATIVE_PROTOCOL_REJECTED')


def _check_string(value):
    if type(value) is not str or any((ord(c) < 32 and c not in '\t\r\n')
                                      or 127 <= ord(c) <= 159
                                      or 0xD800 <= ord(c) <= 0xDFFF for c in value):
        _fail()


def _check(value, kind):
    if kind == 'uuid':
        if type(value) is not str or _UUID.fullmatch(value) is None:
            _fail()
    elif kind == 'timestamp':
        if type(value) is not str or _TIME.fullmatch(value) is None:
            _fail()
        try:
            datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            _fail()
    elif kind == 'decimal':
        if type(value) is not str or _DECIMAL.fullmatch(value) is None or int(value) > 2**63 - 1:
            _fail()
    elif kind == 'text':
        _check_string(value)
        if not value or len(value.encode('utf-8')) > MAX_TEXT_BYTES:
            _fail()
    elif kind == 'bool':
        if type(value) is not bool:
            _fail()
    elif kind == 'status':
        if type(value) is not str or value not in _STATUS:
            _fail()
    elif kind == 'observation':
        if type(value) is not str or value not in _OBSERVED:
            _fail()
    elif kind == 'action':
        if type(value) is not str or value not in ('clipboard.capture_selection', 'clipboard.paste_latest'):
            _fail()
    elif kind == 'mode':
        if value != 'selection':
            _fail()
    elif kind == 'format':
        if value != 'text/plain':
            _fail()
    elif kind == 'version':
        if value != VERSION:
            _fail()
    elif kind == 'error_code':
        if type(value) is not str or value not in ERROR_CODES:
            _fail()
    elif kind == 'error_message':
        if value != SAFE_ERROR_MESSAGE:
            _fail()
    else:
        _fail()


# Fixed closed profiles; payload names are part of the H01-A contract.
# The final tuple marks fields permitted only for a READY/SUCCESS result.
_PROFILES = {
    'clipboard.native_status': ('QUERY', 'ahk.clipboard',
        {'supported_version': 'version'}, {}, None),
    'clipboard.native_status_result': ('RESULT', 'f7hub.clipboard',
        {'supported_version': 'version', 'ready': 'bool', 'revision': 'decimal', 'status': 'status'}, {}, None),
    'clipboard.capture_begin': ('COMMAND', 'ahk.clipboard',
        {'press_id': 'uuid', 'action': 'action', 'target_token': 'uuid'}, {}, None),
    'clipboard.capture_begin_result': ('RESULT', 'f7hub.clipboard',
        {'press_id': 'uuid', 'status': 'status'},
        {'operation_id': 'uuid', 'producer_generation': 'uuid'}, 'READY'),
    'clipboard.capture_submit': ('COMMAND', 'ahk.clipboard',
        {'operation_id': 'uuid', 'producer_generation': 'uuid', 'mode': 'mode',
         'observed_at': 'timestamp', 'format': 'format', 'text': 'text'}, {}, None),
    'clipboard.capture_submit_result': ('RESULT', 'f7hub.clipboard',
        {'operation_id': 'uuid', 'status': 'status', 'replayed': 'bool'},
        {'item_id': 'decimal', 'event_id': 'decimal', 'receipt_id': 'decimal'}, 'SUCCESS'),
    'clipboard.lookup': ('QUERY', 'ahk.clipboard',
        {'query_id': 'uuid', 'operation_id': 'uuid', 'producer_generation': 'uuid'}, {}, None),
    'clipboard.lookup_result': ('RESULT', 'f7hub.clipboard',
        {'query_id': 'uuid', 'operation_id': 'uuid', 'status': 'status'},
        {'item_id': 'decimal', 'event_id': 'decimal', 'receipt_id': 'decimal'}, 'SUCCESS'),
    'clipboard.paste_prepare': ('COMMAND', 'ahk.clipboard',
        {'press_id': 'uuid', 'action': 'action', 'target_token': 'uuid'}, {}, None),
    'clipboard.paste_prepare_result': ('RESULT', 'f7hub.clipboard',
        {'press_id': 'uuid', 'status': 'status'},
        {'prepared_id': 'uuid', 'head_token': 'uuid', 'item_id': 'decimal', 'revision': 'decimal'}, 'READY'),
    'clipboard.paste_consume': ('COMMAND', 'ahk.clipboard',
        {'prepared_id': 'uuid', 'head_token': 'uuid', 'item_id': 'decimal',
         'revision': 'decimal', 'target_token': 'uuid'}, {}, None),
    'clipboard.paste_consume_result': ('RESULT', 'f7hub.clipboard',
        {'prepared_id': 'uuid', 'status': 'status'},
        {'text': 'text', 'format': 'format', 'effect_lease_expires_at': 'timestamp'}, 'READY'),
    'clipboard.native_observation': ('EVENT', 'ahk.clipboard',
        {'operation_id': 'uuid', 'read_state': 'observation', 'write_state': 'observation',
         'input_state': 'observation', 'cleanup_state': 'observation'}, {}, None),
    'contract.error': ('ERROR', 'f7hub.clipboard',
        {'code': 'error_code', 'message': 'error_message'}, {'retryable': 'bool'}, None),
}
_REQUESTS = frozenset(k for k, v in _PROFILES.items() if v[0] in ('COMMAND', 'QUERY'))
_REPLIES = frozenset(k for k, v in _PROFILES.items() if v[0] in ('RESULT', 'ERROR'))
_TEXT_PROFILES = frozenset(('clipboard.capture_submit', 'clipboard.paste_consume_result'))
_PAIR = {k: k + '_result' for k in _REQUESTS}
_RESULT_STATUSES = {
    'clipboard.native_status_result': frozenset(('READY', 'UNAVAILABLE', 'FAILED')),
    'clipboard.capture_begin_result': frozenset(('READY', 'DENIED', 'UNAVAILABLE', 'BUSY', 'FAILED')),
    'clipboard.capture_submit_result': frozenset(('SUCCESS', 'DENIED', 'FAILED', 'TIMED_OUT', 'UNCERTAIN', 'REPLAYED')),
    'clipboard.lookup_result': frozenset(('SUCCESS', 'NOT_FOUND', 'UNCERTAIN')),
    'clipboard.paste_prepare_result': frozenset(('READY', 'DENIED', 'UNAVAILABLE', 'BUSY', 'FAILED')),
    'clipboard.paste_consume_result': frozenset(('READY', 'DENIED', 'FAILED', 'UNCERTAIN', 'REPLAYED')),
}


def _closed(value, required, optional=frozenset()):
    if type(value) is not dict or not required <= value.keys() or not value.keys() <= required | optional:
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


def _reject_number(_):
    _fail()


def _parse(raw):
    if type(raw) is not bytes or len(raw) > MAX_CONTENT_BYTES:
        _fail()
    try:
        source = raw.decode('utf-8', errors='strict')
    except UnicodeError:
        source = None
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
    try:
        value = json.loads(source, object_pairs_hook=_unique, parse_int=_reject_number,
                           parse_float=_reject_number, parse_constant=_reject_number)
    except (ValueError, RecursionError):
        value = None
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
            _fail()
        elif type(item) is str:
            _check_string(item)
    return value


@dataclass(frozen=True, slots=True)
class NativeMessage:
    contract: str
    message_id: str
    created_at: str
    producer: str
    payload: Mapping[str, object] = field(repr=False)
    correlation_id: str | None = None

    def __post_init__(self):
        _check(self.message_id, 'uuid')
        _check(self.created_at, 'timestamp')
        if type(self.contract) is not str or self.contract not in _PROFILES:
            _fail()
        message_class, producer, required, optional, conditional = _PROFILES[self.contract]
        if self.producer != producer or type(self.payload) not in (dict, MappingProxyType):
            _fail()
        fields = dict(self.payload)
        if conditional is not None and fields.get('status') != conditional:
            allowed_optional = frozenset()
        else:
            allowed_optional = frozenset(optional)
        # Conditional fields are a complete set for successful result profiles.
        needed = frozenset(required) | (allowed_optional if conditional is not None else frozenset())
        _closed(fields, needed, allowed_optional if conditional is None else frozenset())
        for key, kind in (required | optional).items():
            if key in fields:
                _check(fields[key], kind)
        if self.contract in _RESULT_STATUSES and fields['status'] not in _RESULT_STATUSES[self.contract]:
            _fail()
        if self.contract == 'clipboard.capture_begin' and fields['action'] != 'clipboard.capture_selection':
            _fail()
        if self.contract == 'clipboard.paste_prepare' and fields['action'] != 'clipboard.paste_latest':
            _fail()
        if message_class in ('RESULT', 'ERROR'):
            _check(self.correlation_id, 'uuid')
            if self.message_id == self.correlation_id:
                _fail()
        elif self.correlation_id is not None:
            _fail()
        object.__setattr__(self, 'payload', MappingProxyType(fields))

    @property
    def message_class(self):
        return _PROFILES[self.contract][0]


def decode_message(raw: bytes, *, expected_producer: str | None = None,
                   request: NativeMessage | None = None) -> NativeMessage:
    """Decode a document only after the caller's transport authentication gate."""
    value = _parse(raw)
    contract = value.get('contract')
    if type(contract) is not str or contract not in _PROFILES:
        _fail()
    if len(raw) > (MAX_CONTENT_BYTES if contract in _TEXT_PROFILES else MAX_ORDINARY_BYTES):
        _fail()
    message_class, producer, _, _, _ = _PROFILES[contract]
    reply = message_class in ('RESULT', 'ERROR')
    _closed(value, _ENVELOPE | ({'correlation_id'} if reply else set()))
    _closed(value['producer'], {'component'})
    if value['schema_version'] != VERSION or value['message_class'] != message_class \
            or value['producer']['component'] != producer:
        _fail()
    if expected_producer is not None and producer != expected_producer:
        _fail()
    result = NativeMessage(contract, value['message_id'], value['created_at'], producer,
                           value['payload'], value.get('correlation_id'))
    if request is not None:
        if type(request) is not NativeMessage or request.contract not in _REQUESTS \
                or contract not in (_PAIR[request.contract], 'contract.error') \
                or result.correlation_id != request.message_id:
            _fail()
        for field_name in ('press_id', 'query_id', 'operation_id', 'prepared_id'):
            if field_name in request.payload and field_name in result.payload \
                    and request.payload[field_name] != result.payload[field_name]:
                _fail()
    elif reply:
        # A reply can be parsed for inspection, but cannot establish correlation alone.
        pass
    return result


def encode_message(message: NativeMessage) -> bytes:
    if type(message) is not NativeMessage:
        _fail()
    value = {'contract': message.contract, 'schema_version': VERSION,
             'message_class': message.message_class, 'message_id': message.message_id,
             'created_at': message.created_at, 'producer': {'component': message.producer},
             'payload': dict(message.payload)}
    if message.correlation_id is not None:
        value['correlation_id'] = message.correlation_id
    try:
        raw = json.dumps(value, ensure_ascii=False, allow_nan=False,
                         separators=(',', ':')).encode('utf-8')
    except (UnicodeError, ValueError, TypeError):
        _fail()
    if len(raw) > (MAX_CONTENT_BYTES if message.contract in _TEXT_PROFILES else MAX_ORDINARY_BYTES):
        _fail()
    return raw


@dataclass(frozen=True, slots=True)
class NativeFrame:
    """Unverified byte layout; MAC and sequence enforcement belong to H01-C."""

    sequence: int
    document: bytes = field(repr=False)
    mac: bytes = field(repr=False)

    def __post_init__(self):
        if type(self.sequence) is not int or not 1 <= self.sequence <= 2**64 - 1 \
                or type(self.document) is not bytes or not 1 <= len(self.document) <= MAX_CONTENT_BYTES \
                or type(self.mac) is not bytes or len(self.mac) != 32:
            _fail()


def pack_frame(frame: NativeFrame) -> bytes:
    if type(frame) is not NativeFrame:
        _fail()
    return struct.pack('<IQ', len(frame.document), frame.sequence) + frame.document + frame.mac


def unpack_frame(raw: bytes) -> NativeFrame:
    if type(raw) is not bytes or not 44 <= len(raw) <= MAX_FRAME_BYTES:
        _fail()
    length, sequence = struct.unpack_from('<IQ', raw)
    if not 1 <= length <= MAX_CONTENT_BYTES or len(raw) != length + 44:
        _fail()
    return NativeFrame(sequence, raw[12:-32], raw[-32:])
