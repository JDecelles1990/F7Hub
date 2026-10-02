"""Shared Qt transport primitives; no business or presentation dependencies."""

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path

from PySide6.QtCore import QObject, QStandardPaths, QTimer, Signal

from f7hub.domain.mochi_protocol import (Framer, ProtocolError, encode, decode,
    MAX_MESSAGE, MAX_QUEUE, READ_BUFFER, INCOMPLETE_MS)


@dataclass(frozen=True)
class CheckoutIdentity:
    checkout_id: str
    endpoint: str
    lock_path: str

    @classmethod
    def from_root(cls, root):
        canonical = os.path.normcase(str(Path(root).resolve()))
        checkout_id = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
        cache = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.GenericCacheLocation))
        directory = cache / 'F7Hub' / 'Mochi'
        user = hashlib.sha256(str(cache.resolve()).casefold().encode('utf-8')).hexdigest()[:16]
        name = f'f7hub-mochi-{user}-{checkout_id}'
        return cls(checkout_id, name, str(directory / (checkout_id + '.lock')))


class Channel(QObject):
    message = Signal(object)
    failed = Signal()

    def __init__(self, socket, parent=None):
        super().__init__(parent)
        self.socket = socket
        self.framer = Framer()
        self.closed = False
        socket.setReadBufferSize(READ_BUFFER)
        self.deadline = QTimer(self)
        self.deadline.setSingleShot(True)
        self.deadline.setInterval(INCOMPLETE_MS)
        self.deadline.timeout.connect(self.reject)
        socket.readyRead.connect(self.read)

    def read(self):
        if self.closed:
            return
        try:
            # Capacity applies to one coalesced batch; server separately bounds its queue.
            frames = self.framer.feed(bytes(self.socket.read(READ_BUFFER)))
            values = [decode(frame) for frame in frames]
        except ProtocolError:
            self.reject()
            return
        if self.framer.buffer:
            if frames or not self.deadline.isActive():
                self.deadline.start()
        else:
            self.deadline.stop()
        for value in values:
            if self.closed:
                break
            self.message.emit(value)

    def send(self, value):
        if self.closed:
            return False
        try:
            raw = encode(value)
        except (ProtocolError, ValueError, TypeError):
            self.reject()
            return False
        # A non-reading peer cannot grow the asynchronous write buffer indefinitely.
        if self.socket.bytesToWrite() + len(raw) > MAX_MESSAGE * MAX_QUEUE:
            self.reject()
            return False
        if self.socket.write(raw) != len(raw):
            self.reject()
            return False
        return True

    def reject(self):
        if not self.closed:
            self.closed = True
            self.deadline.stop()
            self.socket.abort()
            self.failed.emit()
