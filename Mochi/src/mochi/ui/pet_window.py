from PySide6.QtCore import QPoint, QTimer, Qt, Signal, QRect
from PySide6.QtGui import QAction, QPainter, QPixmap
from PySide6.QtWidgets import QMenu, QWidget

from ..core.config import Settings
from ..pet.animation_loader import LoadedAnimation
from ..pet.pet_state import PetState
from ..services.pet_runtime import PetRuntime


class PetWindow(QWidget):
    state_changed = Signal()

    def __init__(self, settings: Settings, loaded: LoadedAnimation, runtime: PetRuntime, wave=None):
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
        self._animations = {'IDLE': self._frames}
        if wave is not None:
            self._animations['WAVE'] = tuple(QPixmap.fromImage(image) for image in wave.images)
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
        self.runtime.start()
        self.sync_timer()
        self._sync_actions()
        self.update()

    def pause(self):
        self.apply('pause')

    def resume(self):
        self.apply('resume')

    def sync_timer(self):
        if self.runtime.playing:
            if not self.timer.isActive():
                self.timer.start()
        else:
            self.timer.stop()
        self._sync_actions()

    def recover_position(self, rectangles=None, primary=None):
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        rectangles = rectangles if rectangles is not None else [s.availableGeometry() for s in app.screens()]
        primary = primary if primary is not None else app.primaryScreen().availableGeometry()
        current = QRect(self.pos(), self.size())
        if any(rect.contains(current) for rect in rectangles):
            return
        target = max(rectangles, key=lambda r: r.intersected(current).width() * r.intersected(current).height(),
                     default=primary)
        if target.intersected(current).isEmpty():
            target = primary
        x = max(target.left(), min(current.left(), target.right() - self.width() + 1))
        y = max(target.top(), min(current.top(), target.bottom() - self.height() + 1))
        self.move(x, y)

    def apply(self, command, controller_count=0):
        outcome = self.runtime.command(command, controller_count)
        if outcome in ('CHANGED', 'UNCHANGED'):
            if command == 'show':
                self.recover_position()
                self.show()
            elif command == 'hide':
                self.hide()
            elif command == 'exit':
                self.sync_timer()
                self.state_changed.emit()
                QTimer.singleShot(0, self.close)
                return outcome
        self.sync_timer()
        self.update()
        self.state_changed.emit()
        return outcome

    def greet(self, session_id):
        self.runtime.greet(session_id)
        self.sync_timer()
        self.update()
        self.state_changed.emit()

    def shutdown(self):
        self.timer.stop()
        self.runtime.exit()
        self._drag_offset = None
        self._sync_actions()

    def _sync_actions(self):
        self.pause_action.setEnabled(self.runtime.state in (PetState.IDLE, PetState.WAVE))
        self.resume_action.setEnabled(self.runtime.state is PetState.PAUSED)
        self.exit_action.setEnabled(self.runtime.state is not PetState.EXITING)

    def _advance(self):
        if not self.runtime.playing:
            self.sync_timer()
            return
        previous = self.runtime.state
        self.runtime.advance()
        self.sync_timer()
        self.update()
        if self.runtime.state is not previous:
            self.state_changed.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._animations[self.runtime.selected_animation][self.runtime.frame_index])

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
