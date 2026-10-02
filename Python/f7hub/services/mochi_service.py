"""Application-session Mochi intent/state; Settings owns no connection."""

import threading
import uuid


class MochiService:
    def __init__(self, gateway):
        self.gateway = gateway
        self.session_id = uuid.uuid4().hex
        self.greeting_consumed = False
        self.automatic_attempt_started = False
        self.manual_exit = False
        self._gate = threading.Lock()
        self._subscribers = []
        self.snapshot = None
        self.availability = 'NOT_STARTED'
        self.busy = False
        self.last_command = None
        self.last_outcome = None
        gateway.changed.connect(self._snapshot)
        gateway.availability.connect(self._availability)
        gateway.busy_changed.connect(self._busy)
        gateway.completed.connect(self._completed)

    def consume_greeting(self):
        with self._gate:
            if self.greeting_consumed:
                return False
            self.greeting_consumed = True
            return True

    def automatic_start(self, schedule=None):
        with self._gate:
            if self.automatic_attempt_started or self.manual_exit:
                return False
            self.automatic_attempt_started = True
        if schedule is not None:
            schedule(lambda: self.gateway.start(self.session_id, self.consume_greeting))
            return True
        return self.gateway.start(self.session_id, self.consume_greeting)

    def start_show(self):
        return self.gateway.start(self.session_id, self.consume_greeting, show=True)

    def command(self, command):
        if command not in ('show', 'hide', 'idle', 'wave', 'pause', 'resume', 'exit', 'status'):
            return False
        if command == 'exit':
            self.manual_exit = True
        return self.gateway.send(command)

    def subscribe(self, callback):
        self._subscribers.append(callback)
        callback(self)

    def unsubscribe(self, callback):
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def _notify(self):
        for callback in tuple(self._subscribers):
            callback(self)

    def _snapshot(self, snapshot):
        self.snapshot = snapshot
        if snapshot['behavior'] == 'EXITING':
            self.manual_exit = True
        self._notify()

    def _availability(self, value):
        self.availability = value
        self._notify()

    def _busy(self, value):
        self.busy = value
        self._notify()

    def _completed(self, command, outcome):
        if command == 'status' and self.last_outcome == 'UNCERTAIN':
            self._notify()
            return
        self.last_command, self.last_outcome = command, outcome
        self._notify()

    def close(self):
        self._subscribers.clear()
        self.gateway.close()
