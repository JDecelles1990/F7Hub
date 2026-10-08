"""Read-only Clipboard Center shell while history capability is unavailable."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class ClipboardWorkspace(QWidget):
    """Present capability absence without accessing clipboard or domain data."""

    tickets_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("clipboardWorkspace")
        self.setAccessibleName("Clipboard Center")
        self.setProperty("moduleKey", "clipboard")

        self.heading = QLabel("Clipboard Center", self)
        self.heading.setObjectName("clipboardHeading")
        self.heading.setTextFormat(Qt.TextFormat.PlainText)
        self.heading.setAccessibleName("Clipboard Center")
        self.unavailable_message = QLabel("Clipboard history is not available yet.", self)
        self.unavailable_message.setObjectName("clipboardUnavailableMessage")
        self.unavailable_message.setTextFormat(Qt.TextFormat.PlainText)
        self.unavailable_message.setWordWrap(True)
        self.unavailable_message.setAccessibleName(self.unavailable_message.text())
        self.back_button = QPushButton("Back to Tickets", self)
        self.back_button.setObjectName("clipboardBackToTicketsButton")
        self.back_button.setAccessibleName("Back to Tickets")
        self.back_button.clicked.connect(self.tickets_requested.emit)

        layout = QVBoxLayout(self)
        layout.addWidget(self.heading)
        layout.addWidget(self.unavailable_message)
        layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
