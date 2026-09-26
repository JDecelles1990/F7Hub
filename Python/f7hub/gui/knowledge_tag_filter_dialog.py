"""Choose existing global tags for a read-only any-tag filter."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton,
    QVBoxLayout,
)


class KnowledgeTagFilterDialog(QDialog):
    def __init__(self, tags, selected_ids: tuple[int, ...] = (), parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter by Tags")
        self.resize(480, 340)
        instruction = QLabel("Match any selected tag. Select none for All tags.", self)
        instruction.setTextFormat(Qt.TextFormat.PlainText)
        instruction.setWordWrap(True)
        self.tag_list = QListWidget(self)
        self.tag_list.setAccessibleName("Tags to match; any selected tag")
        for tag in tags:
            item = QListWidgetItem(tag.name, self.tag_list)
            item.setData(Qt.ItemDataRole.UserRole, tag.tag_id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if tag.tag_id in selected_ids
                else Qt.CheckState.Unchecked
            )
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setDefault(True)
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button = QPushButton("Apply", self)
        self.apply_button.setAutoDefault(False)
        self.apply_button.clicked.connect(self.accept)
        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.apply_button)
        layout = QVBoxLayout(self)
        layout.addWidget(instruction)
        layout.addWidget(self.tag_list, 1)
        layout.addLayout(actions)

    def selected_ids(self) -> tuple[int, ...]:
        return tuple(sorted(
            self.tag_list.item(index).data(Qt.ItemDataRole.UserRole)
            for index in range(self.tag_list.count())
            if self.tag_list.item(index).checkState() == Qt.CheckState.Checked
        ))
