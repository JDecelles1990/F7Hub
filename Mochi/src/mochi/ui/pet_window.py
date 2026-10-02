from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtGui import QAction, QPainter, QPixmap
from PySide6.QtWidgets import QMenu, QWidget

from ..core.config import Settings
from ..pet.animation_loader import LoadedAnimation
from ..pet.pet_state import PetState
from ..services.pet_runtime import PetRuntime


class PetWindow(QWidget):
    def __init__(self, settings: Settings, loaded: LoadedAnimation, runtime: PetRuntime):
        # ShowWithoutActivating avoids startup focus theft. WindowDoesNotAcceptFocus
        # also eats native mouse activation on Windows, preventing the context menu.
        flags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
        if settings.always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        super().__init__(None, flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setWindowTitle(settings.name)
        self.setWindowOpacity(settings.opacity)
        self.runtime = runtime
        self._frames = tuple(QPixmap.fromImage(image) for image in loaded.images)
        self.setFixedSize(self._frames[0].size())
        self._drag_offset: QPoint | None = None
        self.timer = QTimer(self)
        self.timer.setInterval(loaded.animation.interval_ms)
        self.timer.timeout.connect(self._advance)
        self.menu = QMenu(self)
        self.pause_action = QAction("Pause", self)
        self.resume_action = QAction("Resume", self)
        self.exit_action = QAction("Exit", self)
        self.menu.addActions((self.pause_action, self.resume_action, self.exit_action))
        self.pause_action.triggered.connect(self.pause)
        self.resume_action.triggered.connect(self.resume)
        self.exit_action.triggered.connect(self.close)
        self._sync_actions()

    def start(self):
        if self.runtime.start():
            self.timer.start()
        self._sync_actions()
        self.update()

    def pause(self):
        if self.runtime.pause():
            self.timer.stop()
        self._sync_actions()

    def resume(self):
        if self.runtime.resume():
            self.timer.start()
        self._sync_actions()

    def shutdown(self):
        self.timer.stop()
        self.runtime.exit()
        self._drag_offset = None
        self._sync_actions()

    def _sync_actions(self):
        self.pause_action.setEnabled(self.runtime.state is PetState.IDLE)
        self.resume_action.setEnabled(self.runtime.state is PetState.PAUSED)
        self.exit_action.setEnabled(self.runtime.state is not PetState.EXITING)

    def _advance(self):
        self.runtime.advance()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._frames[self.runtime.frame_index])

    def contextMenuEvent(self, event):
        self._drag_offset = None
        self._sync_actions()
        self.menu.popup(event.globalPos())
        event.accept()

    def mousePressEvent(self, event):
        if event.button() is Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() is Qt.MouseButton.LeftButton:
            self._drag_offset = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def closeEvent(self, event):
        self.shutdown()
        self.menu.close()
        event.accept()
        # Tool windows are not counted by Qt's automatic last-window shutdown.
        from PySide6.QtWidgets import QApplication
        QApplication.instance().quit()
