"""Run one service call at a time and deliver completion on the GUI thread."""

from collections.abc import Callable

from PySide6.QtCore import QObject, QThread, Signal, Slot


class _ServiceTask(QThread):
    def __init__(self, work: Callable, parent: QObject) -> None:
        super().__init__(parent)
        self.work = work
        self.result = None
        self.error = None

    def run(self) -> None:
        try:
            self.result = self.work()
        except Exception as error:
            self.error = error


class ServiceTaskRunner(QObject):
    """Retain workers until finished; never update widgets from run()."""

    busy_changed = Signal(bool)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._task = None

    @property
    def busy(self) -> bool:
        return self._task is not None

    def submit(self, work: Callable, on_success: Callable, on_error: Callable) -> bool:
        if self.busy:
            return False
        self._success = on_success
        self._error = on_error
        self._task = _ServiceTask(work, self)
        self._task.finished.connect(self._finished)
        self.busy_changed.emit(True)
        self._task.start()
        return True

    @Slot()
    def _finished(self) -> None:
        task = self._task
        success, error = self._success, self._error
        self._task = None
        self._success = self._error = None
        task.deleteLater()
        self.busy_changed.emit(False)
        if task.error is None:
            success(task.result)
        else:
            error(task.error)
