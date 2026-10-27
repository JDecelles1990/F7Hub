"""One retained window, one tray route, and one guarded explicit shutdown."""

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QPainter, QPixmap, QColor
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon
from shiboken6 import isValid

from f7hub.infrastructure.windows_window_visibility import is_native_window_visible


class ApplicationLifecycle(QObject):
    """Application-owned Qt presentation lifecycle; no Clipboard acquisition."""

    def __init__(self, window):
        if window.lifecycle is not None:
            raise ValueError("The main window already has a lifecycle owner.")
        super().__init__(window)
        self.window = window
        self.application = QApplication.instance()
        self.exiting = False
        self.accepted = False
        self.started = False
        self._hidden = False
        self._focus = None
        self._was_maximized = False
        self.menu = QMenu(window)
        self.open_action = QAction("Open F7Hub", self)
        self.exit_action = QAction("Exit F7Hub", self)
        self.menu.addAction(self.open_action)
        self.menu.addAction(self.exit_action)
        self.tray = QSystemTrayIcon(self)
        # A bundled-independent icon: no theme/plugin/file availability assumption.
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor("#2457a7"))
        painter = QPainter(pixmap)
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "F7")
        painter.end()
        self.tray.setIcon(QIcon(pixmap))
        self.tray.setToolTip("F7Hub")
        self.tray.setContextMenu(self.menu)
        self.open_action.triggered.connect(self.restore)
        self.exit_action.triggered.connect(self.request_exit)
        self.tray.activated.connect(self._activated)
        self.recovery_timer = QTimer(self)
        self.recovery_timer.setInterval(1000)
        self.recovery_timer.timeout.connect(self.check_recovery)
        window.lifecycle = self
        self.application.aboutToQuit.connect(self._about_to_quit)

    def start(self):
        if self.started:
            return
        self.started = True
        self.application.setQuitOnLastWindowClosed(False)
        self.tray.show()
        self.recovery_timer.start()

    def recovery_available(self):
        # Availability is only a capability check. Require an installed, nonempty
        # icon geometry and retained enabled menu route before surrendering taskbar.
        return (self.started and QSystemTrayIcon.isSystemTrayAvailable()
                and self.tray.isVisible() and not self.tray.icon().isNull()
                and not self.tray.geometry().isEmpty()
                and self.tray.contextMenu() is self.menu
                and self.open_action in self.menu.actions()
                and self.menu.isEnabled() and self.open_action.isEnabled())

    def hide(self):
        if self.exiting or self.accepted:
            return
        if not self.recovery_available():
            self.restore()
            self.window.statusBar().showMessage(
                "Tray recovery is unavailable. F7Hub remains open; use Exit to quit.")
            return
        self._focus = self.window.focusWidget()
        self._was_maximized = self.window.isMaximized()
        self._hidden = True
        self.window.hide()
        self.recovery_timer.setInterval(100)
        self.check_recovery()

    def restore(self, *, activate=True, normalize=False):
        if self.accepted:
            return False
        self.recovery_timer.setInterval(1000)
        was_hidden = self._hidden
        maximized = not normalize and (
            self._was_maximized if was_hidden else self.window.isMaximized())
        # Clear minimized state even when activation is refused by Windows.
        # A visible taskbar/window remains the recovery path in that case.
        without_activation = Qt.WidgetAttribute.WA_ShowWithoutActivating
        previous_attribute = self.window.testAttribute(without_activation)
        try:
            if not activate:
                self.window.setAttribute(without_activation, True)
            if maximized:
                self.window.showMaximized()
            else:
                self.window.showNormal()
        finally:
            self.window.setAttribute(without_activation, previous_attribute)
        if activate:
            self.window.raise_()
            self.window.activateWindow()
        if activate and was_hidden and self._focus is not None:
            try:
                if self._focus.isVisible() and self._focus.isEnabled():
                    self._focus.setFocus(Qt.FocusReason.OtherFocusReason)
            except RuntimeError:
                self._focus = None  # A deleted editor cannot retain focus.
        visible = self.window.isVisible() and not self.window.isMinimized()
        self._hidden = not visible
        return visible

    def _activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger,
                      QSystemTrayIcon.ActivationReason.DoubleClick):
            self.restore()

    def check_recovery(self):
        if self.accepted or self.exiting or not isValid(self.window) or not self._hidden:
            return
        # Native show/activation need not deliver a usable Qt Expose event.
        # Reconcile authoritative HWND state from our existing GUI-thread timer.
        # Only a known retained window is queried; this sends no native message.
        if is_native_window_visible(int(self.window.effectiveWinId())):
            self.restore(activate=False, normalize=True)
        elif not self.recovery_available():
            self.restore()
            self.window.statusBar().showMessage(
                "Tray recovery was lost. F7Hub has been restored.")

    def request_exit(self):
        if self.exiting or self.accepted:
            return False
        self.exiting = True
        try:
            # Negotiate with a visible owner, including Exit requested from tray.
            self.restore()
            if not self.window.confirm_exit():
                return False
            self.window.cleanup_shutdown()
            self.accepted = True
            self.recovery_timer.stop()
            self.tray.hide()
            self.window.close()
            self.application.quit()
            return True
        finally:
            self.exiting = False

    def _about_to_quit(self):
        self.recovery_timer.stop()
        self.tray.hide()
        self.window.cleanup_shutdown()
