"""Minimal F7Hub application shell for current technician workflows."""

from __future__ import annotations

import sys
import logging

from PySide6.QtGui import QAction, QColor, QIcon, QKeySequence, QPainter, QPalette, QPen, QPixmap, QShortcut
from PySide6.QtCore import QEvent, QPoint, QPointF, QSize, Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QMainWindow, QWidget, QStackedWidget, QMessageBox,
    QFrame, QMenu, QScrollArea, QToolButton, QVBoxLayout,
)
from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.gui.knowledge_workspace import KnowledgeWorkspace
from f7hub.gui.ticket_workspace import TicketWorkspace
from f7hub.gui.script_workspace import ScriptWorkspace
from f7hub.gui.clipboard_workspace import ClipboardWorkspace
from f7hub.services.ticket_reference_service import TicketReferenceService
from f7hub.services.company_service import CompanyService
from f7hub.services.contact_service import ContactService
from f7hub.services.knowledge_service import KnowledgeService
from f7hub.services.ticket_knowledge_service import TicketKnowledgeService
from f7hub.services.database_backup_service import DatabaseBackupService
from f7hub.services.script_service import ScriptService
from f7hub.gui.mochi_settings_dialog import MochiSettingsDialog
from f7hub.services.altf7hub_service import AltF7HubService, AltF7HubOpenError
from f7hub.services.clipboard_service import ClipboardService
from f7hub.services.settings_service import SettingsService

from f7hub.gui.ticket_create_widget import (
    TicketCreateWidget,
    TicketCreationService,
)


class MainWindow(QMainWindow):
    """Host the current workflow behind a stable application shell."""

    def __init__(
        self,
        ticket_service: TicketCreationService,
        *,
        reference_service: TicketReferenceService | None = None,
        company_service: CompanyService | None = None,
        contact_service: ContactService | None = None,
        knowledge_service: KnowledgeService | None = None,
        knowledge_link_service: TicketKnowledgeService | None = None,
        backup_service: DatabaseBackupService | None = None,
        script_service: ScriptService | None = None,
        powershell_service=None,
        mochi_service=None,
        altf7hub_service: AltF7HubService | None = None,
        clipboard_service: ClipboardService | None = None,
        settings_service: SettingsService | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("mainWindow")
        self.setWindowTitle("F7Hub")
        available = self.screen().availableGeometry()
        self.resize(min(1180, available.width() - 40), min(850, available.height() - 60))

        self.runner = ServiceTaskRunner(self)
        self.backup_service = backup_service
        self.mochi_service = mochi_service
        self._mochi_dialog = None
        self._tickets_started = False
        self.altf7hub_service = altf7hub_service
        self.altf7hub_action = QAction("Guide", self)
        self.altf7hub_action.setObjectName("altF7HubGuideAction")
        self.altf7hub_action.setEnabled(self.altf7hub_service is not None)
        self.altf7hub_action.triggered.connect(self.show_altf7hub)
        self.clipboard_service = clipboard_service
        self.settings_service = settings_service
        self.pages = QStackedWidget(self)
        self.clipboard_workspace: ClipboardWorkspace | None = None
        self.ticket_create_widget = TicketCreateWidget(
            ticket_service, reference_service=reference_service, company_service=company_service,
            contact_service=contact_service,
            task_runner=self.runner, parent=self,
        )
        self.workspace = TicketWorkspace(
            ticket_service, self.runner, self, knowledge_link_service=knowledge_link_service,
            create_widget=self.ticket_create_widget,
        )
        self.workspace.knowledge_article_requested.connect(self.open_knowledge_article)
        self.knowledge_workspace = None
        if knowledge_service is not None:
            try:
                self.knowledge_workspace = KnowledgeWorkspace(
                    knowledge_service, self.runner,
                    guide_action=self.altf7hub_action)
            except Exception as error:
                logging.getLogger(__name__).warning(
                    "Knowledge Base workspace unavailable: %s", type(error).__name__)
        self.script_workspace = (
            ScriptWorkspace(script_service, self.runner, self, powershell_service=powershell_service)
            if script_service is not None
            else None
        )
        self.pages.addWidget(self.workspace)
        if self.knowledge_workspace is not None:
            self.pages.addWidget(self.knowledge_workspace)
        if self.script_workspace is not None:
            self.pages.addWidget(self.script_workspace)
        self.setCentralWidget(self.pages)
        self.ticket_create_widget.ticket_created.connect(self._ticket_created)

        self.mochi_action = QAction('Mochi…', self)
        self.mochi_action.setObjectName('mochiSettingsAction')
        self.mochi_action.setEnabled(mochi_service is not None)
        self.mochi_action.triggered.connect(self.show_mochi_settings)
        self.tickets_action = QAction("Tickets", self)
        self.tickets_action.triggered.connect(self.show_tickets)
        self.knowledge_action = QAction("Knowledge Base", self)
        self.knowledge_action.setEnabled(self.knowledge_workspace is not None)
        if self.knowledge_workspace is None:
            self.knowledge_action.setToolTip(
                "Knowledge Base is unavailable. Use Settings gear → Knowledge Base tools → Guide "
                "for the reference guide.")
        self.knowledge_action.triggered.connect(self.show_knowledge)
        self.scripts_action = QAction("Scripts", self)
        self.scripts_action.setEnabled(self.script_workspace is not None)
        self.scripts_action.triggered.connect(self.show_scripts)
        self.clipboard_action = QAction("&Clipboard Center", self)
        self.clipboard_action.setObjectName("clipboardCenterAction")
        self.clipboard_action.setData("clipboard.center")
        self.clipboard_action.triggered.connect(self.show_clipboard)
        self.backup_action = QAction("Back up database", self)
        self.backup_action.setObjectName("backupDatabaseAction")
        self.backup_action.setEnabled(self.backup_service is not None)
        self.backup_action.triggered.connect(self.back_up_database)
        exit_action = QAction("E&xit", self)
        exit_action.setObjectName("exitAction")
        quit_shortcut = QKeySequence(QKeySequence.StandardKey.Quit)
        if quit_shortcut.isEmpty() and sys.platform == "win32":
            quit_shortcut = QKeySequence("Ctrl+Q")
        exit_action.setShortcut(quit_shortcut)
        exit_action.triggered.connect(self.close)
        # Parentage retains the command; association registers its shortcut
        # independently of the utility menu's popup visibility.
        self.addAction(exit_action)
        self.exit_action = exit_action
        self.runner.busy_changed.connect(self._set_busy)
        self.runner.completion_finished.connect(self._queue_rail_focus)
        self.workspace.note_pending_changed.connect(lambda _pending: self._set_busy(self.runner.busy))
        self.workspace.creation_pending_changed.connect(lambda _pending: self._set_busy(self.runner.busy))
        self.workspace.status_pending_changed.connect(lambda _pending: self._set_busy(self.runner.busy))
        self.workspace.classification_pending_changed.connect(lambda _pending: self._set_busy(self.runner.busy))
        self.ticket_create_widget.pending_changed.connect(lambda _pending: self._set_busy(self.runner.busy))
        if self.script_workspace is not None:
            self.script_workspace.run_pending_changed.connect(lambda _pending: self._set_busy(self.runner.busy))

        self.statusBar().showMessage("Ready")
        self._build_navigation_rail()

    def _build_navigation_rail(self):
        """Present existing actions; the stack remains the routing authority."""
        shell = QWidget(self)
        shell.setObjectName("navigationShell")
        layout = QHBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.navigation_rail = QWidget(shell)
        self.navigation_rail.setObjectName("navigationRail")
        self.navigation_rail.setAccessibleName("Module navigation")
        self.navigation_rail.setAccessibleDescription("Alt+F focuses navigation without changing workspace.")
        self.navigation_rail.setFixedWidth(52)
        rail_layout = QVBoxLayout(self.navigation_rail)
        rail_layout.setContentsMargins(4, 8, 4, 8)
        rail_layout.setSpacing(6)
        self.navigation_buttons = {}
        self._workspace_focus = None
        self._rail_origin = None
        self._rail_generation = 0
        self._rail_keyboard_intent = None
        self._rail_keyboard_button = None
        self._rail_focus_displaced = False
        self._rail_displaced_focus = None
        self._rail_pending_focus = None
        self._rail_queued_generation = None
        self._navigation_return_focus = None
        for key, label, action in (
            ("tickets", "Tickets", self.tickets_action),
            ("knowledge", "Knowledge Base", self.knowledge_action),
            ("scripts", "Scripts", self.scripts_action),
            ("clipboard", "Clipboard Center", self.clipboard_action),
        ):
            button = QToolButton(self.navigation_rail)
            button.setObjectName(key + "NavigationButton")
            button.setDefaultAction(action)
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            button.setIcon(self._navigation_icon(key, QApplication.palette(), False))
            button.setIconSize(QSize(24, 24))
            button.setFixedSize(44, 44)
            button.setToolTip(action.toolTip() if key == "knowledge" and self.knowledge_workspace is None else label)
            button.setAccessibleName(label)
            # Mouse activation preserves the editor focus; Tab/Space remain native.
            button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
            button.installEventFilter(self)
            # Action changes also refresh QToolButton's icon/tooltip from QAction.
            action.changed.connect(
                lambda b=button, k=key, title=label: (
                    b.setIcon(self._navigation_icon(k, QApplication.palette(),
                                                   bool(b.property("active")), b.underMouse())),
                    b.setToolTip(self.knowledge_action.toolTip()
                                 if k == "knowledge" and self.knowledge_workspace is None else title)))
            button.pressed.connect(self._rail_action_started)
            button.triggered.connect(self._rail_action_finished)
            self.navigation_buttons[key] = button
            rail_layout.addWidget(button)
        rail_layout.addStretch()
        self.utility_menu = QMenu(self.navigation_rail)
        self.utility_menu.setObjectName("settingsUtilityMenu")
        for action in (self.mochi_action, self.backup_action, self.exit_action):
            self.utility_menu.addAction(action)
        self.knowledge_tools_menu = self.utility_menu.addMenu("Knowledge Base tools")
        self.knowledge_tools_menu.setObjectName("knowledgeBaseToolsMenu")
        self.knowledge_tools_menu.addAction(self.altf7hub_action)
        self.settings_button = QToolButton(self.navigation_rail)
        self.settings_button.setObjectName("settingsUtilityButton")
        self.settings_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.settings_button.setIconSize(QSize(24, 24))
        self.settings_button.setFixedSize(44, 44)
        self.settings_button.setToolTip("Settings and utilities")
        self.settings_button.setAccessibleName("Settings and utilities")
        self.settings_button.setAccessibleDescription("Alt+S opens Settings and utilities.")
        self.settings_button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.settings_button.installEventFilter(self)
        self.settings_button.clicked.connect(self._show_utility_menu)
        rail_layout.addWidget(self.settings_button)
        self._refresh_navigation_palette()
        layout.addWidget(self.navigation_rail)
        # Existing forms retain their measured minimum sizes. Overflow scrolls
        # inside the shell instead of widening compact windows or hiding controls.
        self.workspace_viewport = QScrollArea(shell)
        self.workspace_viewport.setObjectName("workspaceViewport")
        self.workspace_viewport.setFrameShape(QFrame.Shape.NoFrame)
        self.workspace_viewport.setWidgetResizable(True)
        self.workspace_viewport.setWidget(self.pages)
        layout.addWidget(self.workspace_viewport, 1)
        self.setCentralWidget(shell)
        # The scroll area participates in Tab traversal, while its viewport
        # proxies focus back to it. Put the rail between that entry and the
        # first Tickets control after the complete shell has been composed.
        QWidget.setTabOrder(self.workspace_viewport, self.navigation_buttons["tickets"])
        for first, second in zip(tuple(self.navigation_buttons.values()),
                                 tuple(self.navigation_buttons.values())[1:]):
            QWidget.setTabOrder(first, second)
        QWidget.setTabOrder(self.navigation_buttons["clipboard"], self.settings_button)
        QWidget.setTabOrder(self.settings_button, self.workspace.new_ticket_button)
        self.pages.currentChanged.connect(self._sync_navigation_rail)
        QApplication.instance().focusChanged.connect(self._remember_workspace_focus)
        QApplication.instance().installEventFilter(self)
        self._settings_shortcut = QShortcut(QKeySequence("Alt+S"), self)
        self._navigation_shortcut = QShortcut(QKeySequence("Alt+F"), self)
        for shortcut in (self._settings_shortcut, self._navigation_shortcut):
            shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            shortcut.setAutoRepeat(False)
        self._settings_shortcut.activated.connect(self._show_utility_menu)
        self._navigation_shortcut.activated.connect(self._focus_navigation)
        self.utility_menu.aboutToShow.connect(self._suspend_shell_shortcuts)
        self.utility_menu.aboutToHide.connect(self._resume_shell_shortcuts)
        self._sync_navigation_rail()

    def changeEvent(self, event):
        super().changeEvent(event)
        if (event.type() in (QEvent.Type.ApplicationPaletteChange,
                             QEvent.Type.PaletteChange, QEvent.Type.StyleChange)
                and hasattr(self, "navigation_rail") and not getattr(self, "_updating_navigation_palette", False)):
            self._refresh_navigation_palette()

    def eventFilter(self, watched, event):
        if (event.type() == QEvent.Type.ShortcutOverride
                and QApplication.activePopupWidget() is not None
                and event.modifiers() == Qt.KeyboardModifier.AltModifier
                and event.key() in (Qt.Key.Key_F, Qt.Key.Key_S)):
            # Popups keep their native keyboard handling; Qt's child shortcut
            # context otherwise includes them as an exception to window scope.
            event.accept()
            return True
        if (event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape
                and watched in (*getattr(self, "navigation_buttons", {}).values(),
                                getattr(self, "settings_button", None))
                and watched.hasFocus() and QApplication.activePopupWidget() is None
                and self._navigation_return_focus is not None):
            page, previous = self._navigation_return_focus
            self._navigation_return_focus = None
            try:
                if (self.pages.currentWidget() is page and previous.isVisible()
                        and previous.isEnabled() and previous.window() is self):
                    previous.setFocus(Qt.FocusReason.OtherFocusReason)
                    return True
            except RuntimeError:
                pass  # The invoking control was destroyed; no stale focus.
        if (watched is getattr(self, "settings_button", None)
                and event.type() == QEvent.Type.KeyPress and watched.hasFocus()
                and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)):
            watched.click()
            return True
        if watched is self and event.type() == QEvent.Type.WindowDeactivate:
            self._rail_pending_focus = None
        if self._rail_pending_focus is not None and event.type() in (
                QEvent.Type.MouseButtonPress, QEvent.Type.KeyPress):
            # An input event after activation is an intentional new choice.
            if isinstance(watched, QWidget) and (watched is self or self.isAncestorOf(watched)):
                self._rail_pending_focus = None
        elif (self._rail_pending_focus is not None
                and event.type() == QEvent.Type.FocusIn
                and event.reason() in (Qt.FocusReason.TabFocusReason, Qt.FocusReason.BacktabFocusReason)
                and isinstance(watched, QWidget) and self.isAncestorOf(watched)):
            # Qt also uses TabFocusReason when disabling a focused control.
            # Real Tab/click input cleared the request above; track subsequent
            # automatic displacement without treating it as newer user intent.
            generation, page, button, _displaced = self._rail_pending_focus
            self._rail_pending_focus = (generation, page, button, watched)
        if watched in getattr(self, "navigation_buttons", {}).values():
            if (event.type() == QEvent.Type.KeyPress and watched.hasFocus()
                    and event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter)):
                self._rail_keyboard_intent = watched
            elif event.type() == QEvent.Type.MouseButtonPress:
                self._rail_keyboard_intent = None
        if (isinstance(watched, QToolButton)
                and watched in getattr(self, "navigation_buttons", {}).values()
                and event.type() in (QEvent.Type.Enter, QEvent.Type.Leave)):
            # Styles may request Normal even on hover (non-auto-raised buttons).
            # Choose the foreground from the actual background, not icon mode.
            key = next(key for key, button in self.navigation_buttons.items() if button is watched)
            watched.setIcon(self._navigation_icon(
                key, QApplication.palette(), bool(watched.property("active")),
                event.type() == QEvent.Type.Enter))
        if (watched is getattr(self, "settings_button", None)
                and event.type() in (QEvent.Type.Enter, QEvent.Type.Leave)):
            watched.setIcon(self._navigation_icon(
                "settings", QApplication.palette(), False,
                event.type() == QEvent.Type.Enter))
        return super().eventFilter(watched, event)

    def _show_utility_menu(self):
        if QApplication.activePopupWidget() is not None or QApplication.activeModalWidget() is not None:
            return
        anchor = self.settings_button.mapToGlobal(QPoint(self.settings_button.width(), 0))
        available = self.settings_button.screen().availableGeometry()
        size = self.utility_menu.sizeHint()
        position = QPoint(
            max(available.left(), min(anchor.x(), available.right() - size.width() + 1)),
            max(available.top(), min(anchor.y(), available.bottom() - size.height() + 1)),
        )
        self.utility_menu.popup(position)

    def _suspend_shell_shortcuts(self):
        for shortcut in (self._settings_shortcut, self._navigation_shortcut):
            shortcut.setEnabled(False)

    def _resume_shell_shortcuts(self):
        # Native Alt can dismiss a popup before completing its key sequence.
        # Re-enable on the next event turn, never within that same dispatch.
        QTimer.singleShot(0, self, self._enable_shell_shortcuts)

    def _enable_shell_shortcuts(self):
        if not self.utility_menu.isVisible():
            for shortcut in (self._settings_shortcut, self._navigation_shortcut):
                shortcut.setEnabled(True)

    def _focus_navigation(self):
        """Move focus only; shared actions remain the routing authority."""
        if QApplication.activePopupWidget() is not None or QApplication.activeModalWidget() is not None:
            return
        self._rail_pending_focus = None
        self._rail_generation += 1
        buttons = tuple(self.navigation_buttons.values())
        eligible = lambda button: button.isVisible() and button.isEnabled()
        target = next((button for button in buttons
                       if button.property("active") and eligible(button)), None)
        if target is None:
            target = next((button for button in buttons if eligible(button)), None)
        if target is None and eligible(self.settings_button):
            target = self.settings_button
        if target is not None:
            previous = self.focusWidget()
            if previous is not None and self.pages.currentWidget().isAncestorOf(previous):
                self._navigation_return_focus = (self.pages.currentWidget(), previous)
            target.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _refresh_navigation_palette(self):
        """Use the effective Qt palette, including runtime system/app changes."""
        self._updating_navigation_palette = True
        try:
            palette = QApplication.palette()
            color = lambda group, role: palette.color(group, role).name()
            active = QPalette.ColorGroup.Active
            role = QPalette.ColorRole
            # Keep the adopted rail only for the verified stock Windows dark
            # palette. Any other system/application palette uses its own roles.
            stock_dark = self._navigation_uses_stock_dark(palette)
            background = "#202733" if stock_dark else color(active, role.Window)
            hover = "#343f50" if stock_dark else color(active, role.Button)
            selection = "#294d65" if stock_dark else color(active, role.Highlight)
            indicator = "#74dcff" if stock_dark else color(active, role.WindowText)
            hover_indicator = "#74dcff" if stock_dark else color(active, role.ButtonText)
            selected_indicator = "#74dcff" if stock_dark else color(active, role.HighlightedText)
            self.navigation_rail.setStyleSheet(f"""
                QWidget#navigationRail {{ background: {background}; }}
                QWidget#navigationRail QToolButton {{
                    background: transparent; border: 2px solid transparent;
                    border-radius: 5px;
                }}
                QWidget#navigationRail QToolButton:hover:enabled {{
                    background: {hover};
                }}
                QWidget#navigationRail QToolButton[active="true"],
                QWidget#navigationRail QToolButton[active="true"]:hover:enabled {{
                    background: {selection};
                    border-left-color: {selected_indicator};
                }}
                QWidget#navigationRail QToolButton:focus {{
                    border: 2px dashed {indicator};
                }}
                QWidget#navigationRail QToolButton:hover:focus:enabled {{
                    border: 2px dashed {hover_indicator};
                }}
                QWidget#navigationRail QToolButton[active="true"]:focus,
                QWidget#navigationRail QToolButton[active="true"]:hover:focus:enabled {{
                    border: 2px dashed {selected_indicator};
                    border-left: 2px solid {selected_indicator};
                }}
                QWidget#navigationRail QToolButton:disabled {{
                    background: transparent; border-color: transparent;
                }}
                QWidget#navigationRail QToolButton[active="true"]:disabled {{
                    background: {selection}; border-left: 2px solid {selected_indicator};
                }}
            """)
            for key, button in self.navigation_buttons.items():
                button.setIcon(self._navigation_icon(key, palette, bool(button.property("active")),
                                                     button.underMouse()))
            self.settings_button.setIcon(self._navigation_icon(
                "settings", palette, False, self.settings_button.underMouse()))
        finally:
            self._updating_navigation_palette = False

    @staticmethod
    def _navigation_uses_stock_dark(palette):
        return tuple(palette.color(QPalette.ColorGroup.Active, role).name() for role in (
            QPalette.ColorRole.Window, QPalette.ColorRole.WindowText,
            QPalette.ColorRole.Button, QPalette.ColorRole.Highlight,
        )) == ("#1e1e1e", "#ffffff", "#3c3c3c", "#0078d4")

    @staticmethod
    def _navigation_icon(key, palette, selected, hovered=False):
        """Original outline artwork, rasterized at multiple sizes for Qt DPI selection."""
        icon = QIcon()
        foreground = palette.color(
            QPalette.ColorGroup.Active,
            QPalette.ColorRole.HighlightedText if selected else
            QPalette.ColorRole.ButtonText if hovered else QPalette.ColorRole.WindowText)
        background = (QColor("#294d65" if selected else "#202733")
                      if MainWindow._navigation_uses_stock_dark(palette)
                      else palette.color(QPalette.ColorGroup.Active,
                                         QPalette.ColorRole.Highlight if selected else
                                         QPalette.ColorRole.Window))
        disabled = palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText)

        def luminance(color):
            return sum(weight * (value / 12.92 if value <= .04045 else
                                 ((value + .055) / 1.055) ** 2.4)
                       for value, weight in zip((color.redF(), color.greenF(), color.blueF()),
                                                (.2126, .7152, .0722)))

        def contrast(color):
            low, high = sorted((luminance(color), luminance(background)))
            return (high + .05) / (low + .05)

        # Some stock palettes make Disabled WindowText too faint for an icon.
        # Keep it when discernible; otherwise move toward its paired foreground,
        # retaining a muted color for as long as the rendered contrast allows.
        if contrast(disabled) < 3:
            target = palette.color(QPalette.ColorGroup.Active,
                                   QPalette.ColorRole.HighlightedText if selected else
                                   QPalette.ColorRole.WindowText)
            source = disabled
            for fraction in (.2, .4, .6, .8, 1):
                disabled = QColor.fromRgbF(*(
                    start + (end - start) * fraction for start, end in zip(
                        (source.redF(), source.greenF(), source.blueF()),
                        (target.redF(), target.greenF(), target.blueF()))))
                if contrast(disabled) >= 3:
                    break
        # Explicit modes prevent Qt from synthesizing a palette-incompatible tint.
        for mode, color in (
            (QIcon.Mode.Normal, foreground),
            (QIcon.Mode.Active, foreground),
            (QIcon.Mode.Selected, foreground),
            (QIcon.Mode.Disabled, disabled),
        ):
            for size in (24, 48, 72, 96):
                pixmap = QPixmap(size, size)
                pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.scale(size / 24, size / 24)
                painter.setPen(QPen(color, 1.8, Qt.PenStyle.SolidLine,
                                    Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
                if key == "tickets":
                    painter.drawRoundedRect(3, 5, 18, 14, 2, 2)
                    painter.drawLine(15, 6, 15, 9)
                    painter.drawLine(15, 12, 15, 13)
                    painter.drawLine(15, 16, 15, 18)
                    painter.drawLine(7, 10, 11, 10)
                    painter.drawLine(7, 14, 11, 14)
                elif key == "knowledge":
                    painter.drawRoundedRect(3, 4, 9, 16, 1, 1)
                    painter.drawRoundedRect(12, 4, 9, 16, 1, 1)
                    painter.drawLine(6, 8, 9, 8)
                    painter.drawLine(15, 8, 18, 8)
                    painter.drawLine(6, 12, 9, 12)
                    painter.drawLine(15, 12, 18, 12)
                elif key == "scripts":
                    for x1, y1, x2, y2 in ((7, 7, 2, 12), (2, 12, 7, 17),
                                          (17, 7, 22, 12), (22, 12, 17, 17),
                                          (14, 5, 10, 19)):
                        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
                elif key == "settings":
                    painter.drawEllipse(QPointF(12, 12), 7, 7)
                    painter.drawEllipse(QPointF(12, 12), 2.5, 2.5)
                    for x1, y1, x2, y2 in ((12, 2, 12, 5), (12, 19, 12, 22),
                                          (2, 12, 5, 12), (19, 12, 22, 12),
                                          (5, 5, 7, 7), (17, 17, 19, 19),
                                          (5, 19, 7, 17), (17, 7, 19, 5)):
                        painter.drawLine(x1, y1, x2, y2)
                else:
                    painter.drawRoundedRect(5, 5, 14, 16, 2, 2)
                    painter.drawRoundedRect(9, 3, 6, 4, 1, 1)
                    painter.drawLine(9, 11, 15, 11)
                    painter.drawLine(9, 15, 15, 15)
                painter.end()
                for state in (QIcon.State.Off, QIcon.State.On):
                    icon.addPixmap(pixmap, mode, state)
        return icon

    def _sync_navigation_rail(self, _index=None):
        current = self.pages.currentWidget()
        if _index is not None:
            # currentChanged fires only for a different page, never a refused
            # route or repeated activation. Reset synchronously, without a
            # queued callback that could override later deliberate scrolling.
            self.workspace_viewport.horizontalScrollBar().setValue(0)
            self.workspace_viewport.verticalScrollBar().setValue(0)
        for key, page in (("tickets", self.workspace),
                          ("knowledge", self.knowledge_workspace),
                          ("scripts", self.script_workspace),
                          ("clipboard", self.clipboard_workspace)):
            button = self.navigation_buttons[key]
            active = page is not None and current is page
            button.setProperty("active", active)
            button.setIcon(self._navigation_icon(key, QApplication.palette(), active, button.underMouse()))
            button.setAccessibleDescription("Current workspace" if active else "")
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    def _remember_workspace_focus(self, _old, new):
        if new not in (*self.navigation_buttons.values(), self.settings_button):
            self._navigation_return_focus = None
        if _old is self._rail_keyboard_button and new is not _old:
            self._rail_focus_displaced = True
            self._rail_displaced_focus = new
        page = self.pages.currentWidget()
        if new is not None and page is not None and page.isAncestorOf(new):
            self._workspace_focus = new

    def _rail_action_finished(self, _action):
        # QToolButton emits triggered after its default QAction route completes.
        # Restore only a refused route, synchronously, while focus is still on rail.
        focus = self.focusWidget()
        previous = self._workspace_focus
        page = self.pages.currentWidget()
        if (self._rail_keyboard_button is not None and self._rail_focus_displaced
                and (page is not self._rail_origin or self.runner.busy)):
            self._rail_pending_focus = (self._rail_generation, page,
                                        self._rail_keyboard_button, self._rail_displaced_focus)
        self._rail_keyboard_button = None
        if (page is self._rail_origin and focus in self.navigation_buttons.values() and previous is not None
                and page.isAncestorOf(previous) and previous.isVisible()
                and previous.isEnabled()):
            previous.setFocus(Qt.FocusReason.OtherFocusReason)

    def _rail_action_started(self):
        self._rail_generation += 1
        self._rail_pending_focus = None
        self._rail_origin = self.pages.currentWidget()
        self._rail_keyboard_button = (self.sender() if self.sender() is self._rail_keyboard_intent
                                      else None)
        self._rail_keyboard_intent = None
        self._rail_focus_displaced = False
        self._rail_displaced_focus = None

    def _reconcile_rail_focus(self, generation):
        self._rail_queued_generation = None
        pending = self._rail_pending_focus
        if pending is None or pending[0] != generation or generation != self._rail_generation:
            return
        _, page, button, displaced = pending
        if (not self.isVisible() or not self.isActiveWindow()
                or self.pages.currentWidget() is not page or self.runner.busy or self.runner.completing
                or not self.pages.isEnabled() or not button.isVisible() or not button.isEnabled()):
            return
        self._rail_pending_focus = None
        if self.focusWidget() in (None, displaced):
            button.setFocus(Qt.FocusReason.OtherFocusReason)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._tickets_started:
            self._tickets_started = True
            QTimer.singleShot(0, self, self._load_initial_tickets)
        if self.mochi_service is not None:
            self.mochi_service.automatic_start(lambda callback: QTimer.singleShot(0, self, callback))

    def show_mochi_settings(self):
        if self.mochi_service is None:
            return
        if self._mochi_dialog is None:
            self._mochi_dialog = MochiSettingsDialog(self.mochi_service, self)
            self._mochi_dialog.finished.connect(self._mochi_dialog_closed)
        self._mochi_dialog.show()
        self._mochi_dialog.raise_()
        self._mochi_dialog.activateWindow()

    def _load_initial_tickets(self):
        if (self.pages.currentWidget() is self.workspace and not self.runner.busy
                and not self.workspace.creating and self.workspace.details is None):
            self.workspace.refresh_list()

    def _mochi_dialog_closed(self, _result):
        self._mochi_dialog = None

    def _ticket_created(self, ticket: object) -> None:
        ticket_number = getattr(ticket, "ticket_number", "")
        self.statusBar().showMessage(f"Created ticket {ticket_number}.", 5_000)

    def _set_busy(self, busy):
        busy = busy or self.runner.busy or self._script_run_pending
        busy = busy or self.workspace.note_pending or self.workspace.creation_pending or self.workspace.status_pending or self.workspace.classification_pending
        if busy and self._rail_keyboard_button is not None and self.focusWidget() is self._rail_keyboard_button:
            self._rail_focus_displaced = True
        self.pages.setEnabled(not busy)
        self.tickets_action.setEnabled(not busy)
        self.knowledge_action.setEnabled(not busy and self.knowledge_workspace is not None)
        self.scripts_action.setEnabled(not busy and self.script_workspace is not None)
        self.clipboard_action.setEnabled(not busy)
        self.backup_action.setEnabled(not busy and self.backup_service is not None)
        self.altf7hub_action.setEnabled(not busy and self.altf7hub_service is not None)
        if busy and self._rail_focus_displaced:
            self._rail_displaced_focus = self.focusWidget()
        elif not busy:
            self._queue_rail_focus()
        self.statusBar().showMessage("Working…" if busy else "Ready")

    def _queue_rail_focus(self):
        # busy_changed(False) precedes callback execution. Wait for the outer
        # callback to finish, including any nested task/event dispatch.
        if not self.runner.busy and not self.runner.completing and self._rail_pending_focus is not None:
            generation = self._rail_pending_focus[0]
            if self._rail_queued_generation != generation:
                self._rail_queued_generation = generation
                QTimer.singleShot(0, self, lambda: self._reconcile_rail_focus(generation))

    @property
    def _script_run_pending(self):
        return self.script_workspace is not None and self.script_workspace.run_pending

    def show_new_ticket(self):
        if (self._script_run_pending or self.runner.busy or self.workspace.note_pending
                or self.workspace.creation_pending or self.workspace.status_pending
                or self.workspace.classification_pending):
            return
        if not self._leave_clipboard():
            return
        if (not self.runner.busy and not self.workspace.creation_pending and not self.workspace.status_pending and not self.workspace.classification_pending
                and not self.workspace.note_pending and self.workspace.creating):
            self.pages.setCurrentWidget(self.workspace)
            self.ticket_create_widget.subject_input.setFocus()
        elif self.workspace.begin_creation():
            self.pages.setCurrentWidget(self.workspace)

    def show_altf7hub(self):
        if self._script_run_pending:
            return
        if self.runner.busy or self.workspace.note_pending or self.workspace.creation_pending or self.workspace.status_pending or self.workspace.classification_pending or self.altf7hub_service is None:
            return

        def completed(outcome):
            self.statusBar().showMessage(
                "Guide editor focused." if outcome == "FOCUSED_EDITOR" else "Guide opened.",
                5_000,
            )

        def failed(error):
            message = (str(error) if isinstance(error, AltF7HubOpenError) else
                       "The guide open request was not confirmed. Retry or use Alt+F7.")
            self.statusBar().showMessage("Guide open request not confirmed.", 5_000)
            QMessageBox.warning(self, "Guide could not open", message)

        self.runner.submit(self.altf7hub_service.show_guide, completed, failed)

    def back_up_database(self):
        if self._script_run_pending:
            return
        if self.runner.busy or self.workspace.note_pending or self.workspace.creation_pending or self.workspace.status_pending or self.workspace.classification_pending or self.backup_service is None:
            return

        def completed(path):
            self.statusBar().showMessage("Database backup completed.", 5_000)
            QMessageBox.information(
                self, "Database backup completed",
                f"Backup saved to:\n{path}\n\n"
                "This contains local SQLite data only. Copy it to another location "
                "to protect against loss of this drive.",
            )

        def failed(_error):
            self.statusBar().showMessage("Database backup failed.", 5_000)
            QMessageBox.warning(
                self, "Database backup failed",
                "The database backup could not be completed. No completed backup was published.",
            )

        self.runner.submit(self.backup_service.create_backup, completed, failed)

    def show_tickets(self):
        if self._script_run_pending:
            return
        if not self.runner.busy and not self.workspace.note_pending and not self.workspace.creation_pending and not self.workspace.status_pending and not self.workspace.classification_pending:
            if not self._leave_clipboard():
                return
            self.pages.setCurrentWidget(self.workspace)
            self.workspace.refresh_list()

    def show_knowledge(self):
        if self._script_run_pending:
            return
        if not self.runner.busy and not self.workspace.note_pending and not self.workspace.creation_pending and not self.workspace.status_pending and not self.workspace.classification_pending and self.knowledge_workspace is not None:
            if not self.workspace.confirm_discard():
                return
            if not self._leave_clipboard():
                return
            self.workspace._clear_drafts()
            self.pages.setCurrentWidget(self.knowledge_workspace)
            self.knowledge_workspace.refresh_list()

    def show_scripts(self):
        if self._script_run_pending:
            return
        if not self.runner.busy and not self.workspace.note_pending and not self.workspace.creation_pending and not self.workspace.status_pending and not self.workspace.classification_pending and self.script_workspace is not None:
            if not self.workspace.confirm_discard():
                return
            if not self._leave_clipboard():
                return
            self.workspace._clear_drafts()
            self.pages.setCurrentWidget(self.script_workspace)
            self.script_workspace.refresh_list()

    def show_clipboard(self) -> bool:
        if (self._script_run_pending or self.runner.busy or self.workspace.note_pending
                or self.workspace.creation_pending or self.workspace.status_pending
                or self.workspace.classification_pending):
            return False
        if self.pages.currentWidget() is not self.clipboard_workspace:
            if not self.workspace.confirm_discard():
                return False
            self.workspace._clear_drafts()
        if self.clipboard_workspace is None:
            self.clipboard_workspace = ClipboardWorkspace(
                self, clipboard_service=self.clipboard_service, settings_service=self.settings_service,
                capture_scroll=self._capture_clipboard_scroll,
                restore_scroll=self._restore_clipboard_scroll)
            self.pages.addWidget(self.clipboard_workspace)
        same_page = self.pages.currentWidget() is self.clipboard_workspace
        self.pages.setCurrentWidget(self.clipboard_workspace)
        self.clipboard_workspace.activate()
        current_focus = self.focusWidget()
        rail_button = self.navigation_buttons["clipboard"]
        if same_page and current_focus is not None:
            try:
                if (current_focus is rail_button or self.clipboard_workspace.isAncestorOf(current_focus)):
                    if (current_focus.isVisible() and current_focus.isEnabled()
                            and current_focus.focusPolicy() != Qt.FocusPolicy.NoFocus):
                        return True
            except RuntimeError:
                pass  # A removed widget cannot retain focus.
        target = self.clipboard_workspace.activation_focus_target() or rail_button
        try:
            if (target.isVisible() and target.isEnabled()
                    and target.focusPolicy() != Qt.FocusPolicy.NoFocus):
                target.setFocus(Qt.FocusReason.OtherFocusReason)
        except RuntimeError:
            if target is not rail_button and rail_button.isVisible() and rail_button.isEnabled():
                rail_button.setFocus(Qt.FocusReason.OtherFocusReason)
        return True

    def _capture_clipboard_scroll(self):
        return (self.workspace_viewport.horizontalScrollBar().value(),
                self.workspace_viewport.verticalScrollBar().value())

    def _restore_clipboard_scroll(self, position):
        if self.pages.currentWidget() is not self.clipboard_workspace:
            return
        self.pages.layout().activate()
        for bar, value in zip((self.workspace_viewport.horizontalScrollBar(),
                               self.workspace_viewport.verticalScrollBar()), position):
            bar.setValue(max(bar.minimum(), min(bar.maximum(), value)))
        # Focus reachability takes precedence over retaining an off-screen
        # offset. Never scroll the hidden Clipboard source or another module.
        focus = self.focusWidget()
        if focus is not None and self.clipboard_workspace.isAncestorOf(focus):
            self.workspace_viewport.ensureWidgetVisible(focus, 0, 0)

    def _leave_clipboard(self) -> bool:
        if self.clipboard_workspace is None:
            return True
        if not self.clipboard_workspace.confirm_leave():
            self.statusBar().showMessage("Finish or discard the Clipboard preference edits before leaving.")
            return False
        self.clipboard_workspace.leave()
        return True

    def open_knowledge_article(self, article_id):
        if self._script_run_pending:
            return
        if self.runner.busy or self.workspace.note_pending or self.workspace.creation_pending or self.workspace.status_pending or self.workspace.classification_pending or self.knowledge_workspace is None:
            return
        if not self.workspace.confirm_discard():
            return
        if not self._leave_clipboard():
            return
        self.workspace._clear_drafts()
        self.pages.setCurrentWidget(self.knowledge_workspace)
        self.knowledge_workspace.open_article_by_id(article_id)

    def closeEvent(self, event):
        if (self._script_run_pending or self.runner.busy or self.workspace.note_pending or self.workspace.creation_pending or self.workspace.status_pending or self.workspace.classification_pending
                or (self.knowledge_workspace is not None and self.knowledge_workspace.filter_loading)
                or (self.clipboard_workspace is not None
                    and (self.clipboard_workspace.loading or self.clipboard_workspace.settings_pending))):
            self.statusBar().showMessage("An operation is finishing. Please close again when it completes.")
            event.ignore()
            return
        if not self.workspace.confirm_discard():
            event.ignore()
            return
        if self.ticket_create_widget.has_draft():
            answer = QMessageBox.question(
                self, "Unsaved new ticket", "Discard the unsaved new ticket?",
                QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if answer != QMessageBox.StandardButton.Discard:
                event.ignore()
                return
        if not self._leave_clipboard():
            event.ignore()
            return
        if self.mochi_service is not None:
            if self._mochi_dialog is not None:
                self._mochi_dialog.close()
            self.mochi_service.close()
        super().closeEvent(event)
