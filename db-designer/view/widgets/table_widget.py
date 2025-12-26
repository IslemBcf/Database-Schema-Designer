from __future__ import annotations

from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QContextMenuEvent, QCursor, QMouseEvent
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QMenu, QWidget


class TableWidget(QFrame):
    """
    Enhanced visual representation of a table on the canvas.
    Pure UI: shows table name + attributes, supports dragging and context menus.
    """

    delete_table_requested = Signal(str)
    delete_attribute_requested = Signal(str, str)

    def __init__(self, table_name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._table_name = table_name
        self._drag_start_pos: QPoint | None = None

        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #1a2332;
                border: 2px solid #2563eb;
                border-radius: 14px;
                min-width: 240px;
            }
            QFrame:hover {
                border-color: #3b82f6;
                box-shadow: 0 0 10px rgba(37, 99, 235, 0.3);
            }
            QLabel#title {
                color: #ffffff;
                font-weight: 700;
                font-size: 16px;
                padding: 16px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #1e40af);
                border-bottom: 1px solid #3b82f6;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
            QLabel[attrLabel="true"] {
                color: #e2e8f0;
                font-size: 13px;
                padding: 10px 16px;
                background-color: #1a2332;
                border-bottom: 1px solid #1e3a5f;
            }
            QLabel[attrLabel="true"]:hover {
                background-color: #1e3a5f;
                color: #60a5fa;
            }
            QLabel[noAttributes="true"] {
                color: #64748b;
                font-style: italic;
                font-size: 12px;
                padding: 14px 16px;
                background-color: #0d1b2a;
            }
            """
        )

        # Title
        self._title_label = QLabel(self._table_name)
        self._title_label.setObjectName("title")
        self._title_label.setAlignment(Qt.AlignCenter)

        # Attributes container
        self._attrs_layout = QVBoxLayout()
        self._attrs_layout.setContentsMargins(0, 0, 0, 0)
        self._attrs_layout.setSpacing(0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._title_label)
        layout.addLayout(self._attrs_layout)

        # Cursor to indicate draggable
        self.setCursor(QCursor(Qt.OpenHandCursor))

    @property
    def table_name(self) -> str:
        return self._table_name

    def update_attributes_text(self, lines: list[str]) -> None:
        """
        Update the list of displayed attributes.
        Lines are just attribute/column names (pure UI).
        """
        # Clear existing attribute labels
        while self._attrs_layout.count():
            item = self._attrs_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        if lines:
            for i, attr_name in enumerate(lines):
                attr_label = QLabel(f"  {attr_name}")
                # Use dynamic property instead of objectName for class-like styling
                attr_label.setProperty("attrLabel", "true")
                attr_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                attr_label.setContextMenuPolicy(Qt.CustomContextMenu)

                # Capture attr_name by default argument to avoid late-binding closure issue
                attr_label.customContextMenuRequested.connect(
                    lambda pos, name=attr_name, lbl=attr_label: self._show_attribute_context_menu(lbl, pos, name)
                )

                # Apply styling to all items, with special styling for last item
                if i == len(lines) - 1:
                    # Last item: rounded bottom corners
                    attr_label.setStyleSheet(
                        """
                        QLabel {
                            color: #e2e8f0;
                            font-size: 13px;
                            padding: 10px 16px;
                            background-color: #1a2332;
                            border-bottom-left-radius: 12px;
                            border-bottom-right-radius: 12px;
                        }
                        QLabel:hover {
                            background-color: #1e3a5f;
                            color: #60a5fa;
                        }
                        """
                    )
                else:
                    # Non-last items: explicit styling to ensure visibility
                    attr_label.setStyleSheet(
                        """
                        QLabel {
                            color: #e2e8f0;
                            font-size: 13px;
                            padding: 10px 16px;
                            background-color: #1a2332;
                            border-bottom: 1px solid #1e3a5f;
                        }
                        QLabel:hover {
                            background-color: #1e3a5f;
                            color: #60a5fa;
                        }
                        """
                    )

                self._attrs_layout.addWidget(attr_label)
                attr_label.show()  # Explicitly show the widget
        else:
            no_attrs_label = QLabel("(no columns)")
            no_attrs_label.setProperty("noAttributes", "true")
            no_attrs_label.setAlignment(Qt.AlignCenter)
            no_attrs_label.setStyleSheet(
                """
                QLabel {
                    color: #64748b;
                    font-style: italic;
                    font-size: 12px;
                    padding: 18px 16px;
                    background-color: #0d1b2a;
                    border-bottom-left-radius: 12px;
                    border-bottom-right-radius: 12px;
                }
                """
            )
            self._attrs_layout.addWidget(no_attrs_label)

        self.adjustSize()
        # Ensure minimum size
        min_width = 220
        min_height = 100
        if self.width() < min_width:
            self.resize(min_width, self.height())
        if self.height() < min_height:
            self.resize(self.width(), max(min_height, 60 + len(lines) * 28))

    # Table-level context menu
    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu(self)
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #1a2332;
                border: 1px solid #1e3a5f;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 10px 24px;
                border-radius: 6px;
                color: #e2e8f0;
            }
            QMenu::item:selected {
                background-color: #2563eb;
                color: white;
            }
            """
        )
        delete_action = menu.addAction("Delete Table")
        delete_action.triggered.connect(lambda: self.delete_table_requested.emit(self._table_name))
        menu.exec(event.globalPos())

    # Attribute-level context menu
    def _show_attribute_context_menu(self, label: QLabel, pos: QPoint, attr_name: str) -> None:
        menu = QMenu(self)
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #1a2332;
                border: 1px solid #1e3a5f;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 10px 24px;
                border-radius: 6px;
                color: #e2e8f0;
            }
            QMenu::item:selected {
                background-color: #dc2626;
                color: white;
            }
            """
        )
        delete_action = menu.addAction(f"Delete '{attr_name}'")
        delete_action.triggered.connect(
            lambda: self.delete_attribute_requested.emit(self._table_name, attr_name)
        )
        menu.exec(label.mapToGlobal(pos))

    # Dragging (UI only)
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.pos()
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_start_pos is not None and (event.buttons() & Qt.LeftButton):
            self.move(self.pos() + event.pos() - self._drag_start_pos)
            # Request canvas repaint for relationship lines
            parent = self.parent()
            if isinstance(parent, QWidget):
                parent.update()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = None
            self.setCursor(QCursor(Qt.OpenHandCursor))
            event.accept()
        else:
            super().mouseReleaseEvent(event)
