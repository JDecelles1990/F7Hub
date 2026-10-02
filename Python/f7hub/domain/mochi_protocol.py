"""Mochi protocol v1: bounded UTF-8 JSON lines; no Qt or application data."""

import json
import re

VERSION = 1
MAX_MESSAGE = 4096  # includes the LF delimiter
READ_BUFFER = 8192
MAX_CONNECTIONS = 8
MAX_QUEUE = 8
INCOMPLETE_MS = 2000
COMMAND_MS = 2000
STARTUP_MS = 5000
MUTATIONS = frozenset(('show', 'hide', 'idle', 'wave', 'pause', 'resume', 'exit'))
COMMANDS = MUTATIONS | {'attach', 'status'}
OUTCOMES = frozenset(('ATTACHED', 'STATUS', 'STATE', 'CHANGED', 'UNCHANGED', 'INVALID_TRANSITION', 'NO_CONTROLLER', 'EXITING'))
FIELDS = {'version', 'request_id', 'controller_id', 'session_id', 'checkout_id', 'command', 'payload'}
SNAPSHOT_FIELDS = {'checkout_id', 'behavior', 'selected_animation', 'frame', 'visibility', 'paused'}
_ID = re.compile(r'[A-Za-z0-9_-]{1,64}\Z')


class ProtocolError(ValueError):
    """Invalid input; never expose the source bytes or exception text."""


def identifier(value):
    return type(value) is str and _ID.fullmatch(value) is not None


def encode(value):
    raw = json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(',', ':')).encode('utf-8') + b'\n'
    if len(raw) > MAX_MESSAGE:
        raise ProtocolError('MESSAGE_LIMIT')
    return raw


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ProtocolError('DUPLICATE_FIELD')
        result[key] = value
    return result


def decode(raw):
    if len(raw) + 1 > MAX_MESSAGE:
        raise ProtocolError('MESSAGE_LIMIT')
    try:
        value = json.loads(raw.decode('utf-8', errors='strict'), object_pairs_hook=_unique,
                           parse_constant=lambda _: (_ for _ in ()).throw(ProtocolError('INVALID_JSON')))
    except (UnicodeError, ValueError, RecursionError) as error:
        raise ProtocolError('INVALID_JSON') from error
    if type(value) is not dict:
        raise ProtocolError('INVALID_OBJECT')
    return value


def validate_request(value, checkout_id):
    if set(value) != FIELDS or type(value['version']) is not int or value['version'] != VERSION:
        raise ProtocolError('SCHEMA')
    if not all(identifier(value[k]) for k in ('request_id', 'controller_id', 'session_id', 'checkout_id')):
        raise ProtocolError('IDENTIFIER')
    if value['checkout_id'] != checkout_id:
        raise ProtocolError('CHECKOUT')
    command, payload = value['command'], value['payload']
    if type(command) is not str or command not in COMMANDS or type(payload) is not dict:
        raise ProtocolError('COMMAND')
    if command == 'attach':
        if (set(payload) != {'greeting_requested', 'connection_generation'} or
                type(payload['greeting_requested']) is not bool or
                type(payload['connection_generation']) is not int or
                not 1 <= payload['connection_generation'] <= 2**53):
            raise ProtocolError('PAYLOAD')
    elif payload:
        raise ProtocolError('PAYLOAD')
    return value


def validate_response(value, checkout_id):
    if set(value) != {'version', 'request_id', 'runtime_id', 'connection_generation', 'ok', 'outcome', 'snapshot'}:
        raise ProtocolError('RESPONSE_SCHEMA')
    if (type(value['version']) is not int or value['version'] != VERSION or
            not identifier(value['request_id']) or not identifier(value['runtime_id']) or
            type(value['connection_generation']) is not int or not 1 <= value['connection_generation'] <= 2**53 or
            type(value['ok']) is not bool or type(value['outcome']) is not str or value['outcome'] not in OUTCOMES):
        raise ProtocolError('RESPONSE_SCHEMA')
    s = value['snapshot']
    if (type(s) is not dict or set(s) != SNAPSHOT_FIELDS or s['checkout_id'] != checkout_id or
            s['behavior'] not in ('STARTING', 'IDLE', 'WAVE', 'PAUSED', 'EXITING') or
            s['selected_animation'] not in ('IDLE', 'WAVE') or s['visibility'] not in ('VISIBLE', 'HIDDEN') or
            type(s['frame']) is not int or not 0 <= s['frame'] < 128 or type(s['paused']) is not bool):
        raise ProtocolError('SNAPSHOT')
    return value


class Framer:
    """Reject oversized unterminated input and bound complete frames per read."""
    def __init__(self):
        self.buffer = bytearray()

    def feed(self, data, capacity=MAX_QUEUE):
        self.buffer.extend(data)
        frames = []
        while b'\n' in self.buffer:
            end = self.buffer.index(10)
            if end + 1 > MAX_MESSAGE or len(frames) >= capacity:
                raise ProtocolError('INPUT_LIMIT')
            frames.append(bytes(self.buffer[:end]))
            del self.buffer[:end + 1]
        if len(self.buffer) >= MAX_MESSAGE:
            raise ProtocolError('INPUT_LIMIT')
        return frames
