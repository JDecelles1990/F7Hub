"""Modeless runtime controls; closing only removes this UI subscription."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QGridLayout


class MochiSettingsDialog(QDialog):
    def __init__(self, service, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Mochi')
        self.setObjectName('mochiSettingsDialog')
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setModal(False)
        self.service = service
        self._active = True
        self.status = QLabel(self)
        self.status.setWordWrap(True)
        self.status.setTextFormat(Qt.TextFormat.PlainText)
        self.status.setObjectName('mochiStatus')
        layout = QVBoxLayout(self)
        layout.addWidget(self.status)
        grid = QGridLayout()
        layout.addLayout(grid)
        self.buttons = {}
        for index, (command, text) in enumerate((('start', 'Start/Show'), ('hide', 'Hide'),
                                               ('idle', 'Idle'), ('wave', 'Wave'),
                                               ('pause', 'Pause'), ('exit', 'Exit'))):
            button = QPushButton(text, self)
            button.setObjectName('mochi_' + command)
            button.clicked.connect(lambda _checked=False, c=command: self.invoke(c))
            self.buttons[command] = button
            grid.addWidget(button, index // 2, index % 2)
        close = QPushButton('Close', self)
        close.setObjectName('mochi_close')
        close.clicked.connect(self.close)
        layout.addWidget(close)
        self.resize(340, 250)
        service.subscribe(self.render)

    def invoke(self, command):
        if command == 'start':
            self.service.start_show()
        else:
            if command == 'pause' and self.service.snapshot and self.service.snapshot['paused']:
                command = 'resume'
            self.service.command(command)

    def render(self, service):
        if not self._active:
            return
        snapshot = service.snapshot
        text = {'NOT_STARTED': 'Mochi has not started.', 'CONNECTING': 'Connecting to Mochi…',
                'AVAILABLE': 'Mochi connected.', 'UNAVAILABLE': 'Mochi unavailable. Use Start/Show to retry.',
                'TIMEOUT': 'Mochi did not respond. Use Start/Show to retry.',
                'LAUNCH_FAILED': 'Mochi could not start. Use Start/Show to retry.',
                'DISCONNECTED': 'Mochi disconnected.'}.get(service.availability, 'Mochi unavailable.')
        if snapshot and service.availability == 'AVAILABLE':
            text += f"\n{snapshot['visibility'].title()} · {snapshot['behavior'].title()}"
        if service.last_outcome == 'UNCERTAIN':
            text += '\nThe last command could not be confirmed. Current state is being checked.'
        self.status.setText(text)
        usable = service.availability == 'AVAILABLE' and snapshot and snapshot['behavior'] != 'EXITING'
        for command, button in self.buttons.items():
            button.setEnabled(not service.busy and (command == 'start' or bool(usable)))
        paused = bool(snapshot and snapshot['paused'])
        self.buttons['pause'].setText('Resume' if paused else 'Pause')
        for command in ('idle', 'wave'):
            self.buttons[command].setEnabled(not service.busy and bool(usable) and not paused)

    def closeEvent(self, event):
        self._active = False
        self.service.unsubscribe(self.render)
        super().closeEvent(event)
