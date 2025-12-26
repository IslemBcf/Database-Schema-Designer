from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QLabel,
    QFrame,
)


class NewTableDialog(QDialog):
    """Enhanced dialog to enter a new table name."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add New Table")
        self.setModal(True)
        self.resize(400, 180)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #0a1629;
            }
            QLabel {
                color: #e2e8f0;
                font-size: 13px;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #1e3a5f;
                border-radius: 8px;
                font-size: 14px;
                background-color: #0d1b2a;
                color: #e2e8f0;
            }
            QLineEdit:focus {
                border: 2px solid #2563eb;
                background-color: #1a2332;
                color: #ffffff;
            }
            QPushButton {
                padding: 12px 28px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("Create New Table")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 700;
                color: #e2e8f0;
                padding-bottom: 5px;
                letter-spacing: 0.5px;
            }
        """)
        main_layout.addWidget(title)
        
        # Description
        desc = QLabel("Enter a unique name for your table:")
        desc.setStyleSheet("color: #94a3b8; font-size: 13px;")
        main_layout.addWidget(desc)

        # Input field
        self._name_edit = QLineEdit(self)
        self._name_edit.setPlaceholderText("e.g., users, products, orders")
        main_layout.addWidget(self._name_edit)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self
        )
        buttons.button(QDialogButtonBox.Ok).setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: 1px solid #3b82f6;
            }
            QPushButton:hover {
                background-color: #3b82f6;
                border: 1px solid #60a5fa;
            }
        """)
        buttons.button(QDialogButtonBox.Cancel).setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #e2e8f0;
                border: 1px solid #475569;
            }
            QPushButton:hover {
                background-color: #475569;
                border: 1px solid #64748b;
                color: #ffffff;
            }
        """)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
        
        # Auto-focus on input
        self._name_edit.setFocus()

    def get_table_name(self) -> str:
        return self._name_edit.text().strip()


class NewAttributeDialog(QDialog):
    """Enhanced dialog to define a new attribute."""

    def __init__(self, table_names: list[str], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Attribute")
        self.setModal(True)
        self.resize(480, 420)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #0a1629;
            }
            QLabel {
                color: #e2e8f0;
                font-size: 13px;
            }
            QLineEdit, QComboBox {
                padding: 12px;
                border: 2px solid #1e3a5f;
                border-radius: 8px;
                font-size: 13px;
                background-color: #0d1b2a;
                min-height: 20px;
                color: #e2e8f0;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #2563eb;
                background-color: #1a2332;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a2332;
                border: 1px solid #1e3a5f;
                color: #e2e8f0;
                selection-background-color: #2563eb;
                selection-color: white;
            }
            QCheckBox {
                spacing: 8px;
                color: #cbd5e1;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #475569;
                border-radius: 4px;
                background-color: #0d1b2a;
            }
            QCheckBox::indicator:checked {
                background-color: #2563eb;
                border-color: #3b82f6;
            }
            QPushButton {
                padding: 12px 28px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("Add Column/Attribute")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #1e293b;
            }
        """)
        main_layout.addWidget(title)
        
        # Description
        desc = QLabel("Define a new column for your table:")
        desc.setStyleSheet("color: #94a3b8; font-size: 13px; margin-bottom: 5px;")
        main_layout.addWidget(desc)

        # Form
        form = QFormLayout()
        form.setSpacing(15)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._table_combo = QComboBox(self)
        self._table_combo.addItems(table_names)
        form.addRow("Target Table:", self._table_combo)

        self._attr_name_edit = QLineEdit(self)
        self._attr_name_edit.setPlaceholderText("e.g., email, price, created_at")
        form.addRow("Column Name:", self._attr_name_edit)

        self._type_edit = QLineEdit(self)
        self._type_edit.setPlaceholderText("INTEGER, TEXT, REAL, BLOB")
        self._type_edit.setText("TEXT")
        form.addRow("Data Type:", self._type_edit)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #1e3a5f; max-height: 1px;")
        form.addRow(separator)
        
        # Constraints section
        constraints_label = QLabel("Constraints:")
        constraints_label.setStyleSheet("font-weight: 600; color: #cbd5e1; margin-top: 5px;")
        form.addRow(constraints_label)

        self._pk_check = QCheckBox("Primary Key", self)
        self._pk_check.setToolTip("Unique identifier for each row")
        form.addRow("", self._pk_check)

        self._nullable_check = QCheckBox("Nullable (Allow NULL)", self)
        self._nullable_check.setChecked(True)
        self._nullable_check.setToolTip("Can this column have empty values?")
        form.addRow("", self._nullable_check)

        self._unique_check = QCheckBox("Unique", self)
        self._unique_check.setToolTip("All values must be different")
        form.addRow("", self._unique_check)

        main_layout.addLayout(form)
        main_layout.addStretch()

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self
        )
        buttons.button(QDialogButtonBox.Ok).setText("Add Attribute")
        buttons.button(QDialogButtonBox.Ok).setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: 1px solid #3b82f6;
            }
            QPushButton:hover {
                background-color: #3b82f6;
                border: 1px solid #60a5fa;
            }
        """)
        buttons.button(QDialogButtonBox.Cancel).setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #e2e8f0;
                border: 1px solid #475569;
            }
            QPushButton:hover {
                background-color: #475569;
                border: 1px solid #64748b;
                color: #ffffff;
            }
        """)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
        
        # Auto-focus
        self._attr_name_edit.setFocus()

    def get_values(self) -> dict:
        return {
            "table_name": self._table_combo.currentText(),
            "attr_name": self._attr_name_edit.text().strip(),
            "data_type": self._type_edit.text().strip() or "TEXT",
            "is_pk": self._pk_check.isChecked(),
            "is_nullable": self._nullable_check.isChecked(),
            "is_unique": self._unique_check.isChecked(),
        }


class RelationshipDialog(QDialog):
    """Enhanced dialog to define a relationship between tables."""

    def __init__(self, table_names: list[str], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Relationship")
        self.setModal(True)
        self.resize(500, 380)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #0a1629;
            }
            QLabel {
                color: #e2e8f0;
                font-size: 13px;
            }
            QComboBox {
                padding: 12px;
                border: 2px solid #1e3a5f;
                border-radius: 8px;
                font-size: 13px;
                background-color: #0d1b2a;
                min-height: 20px;
                color: #e2e8f0;
            }
            QComboBox:focus {
                border: 2px solid #2563eb;
                background-color: #1a2332;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a2332;
                border: 1px solid #1e3a5f;
                color: #e2e8f0;
                selection-background-color: #2563eb;
                selection-color: white;
            }
            QPushButton {
                padding: 12px 28px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("Create Relationship")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 700;
                color: #e2e8f0;
                letter-spacing: 0.5px;
            }
        """)
        main_layout.addWidget(title)
        
        # Description
        desc = QLabel("Link two tables with a relationship:")
        desc.setStyleSheet("color: #94a3b8; font-size: 13px;")
        main_layout.addWidget(desc)

        # Form
        form = QFormLayout()
        form.setSpacing(15)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._table_a_combo = QComboBox(self)
        self._table_a_combo.addItems(table_names)
        form.addRow("Table A (Parent):", self._table_a_combo)

        self._table_b_combo = QComboBox(self)
        self._table_b_combo.addItems(table_names)
        form.addRow("Table B (Child):", self._table_b_combo)

        self._type_combo = QComboBox(self)
        self._type_combo.addItems(["1-N (One-to-Many)", "N-N (Many-to-Many)"])
        form.addRow("Relationship Type:", self._type_combo)

        main_layout.addLayout(form)
        main_layout.addStretch()

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self
        )
        buttons.button(QDialogButtonBox.Ok).setText("Create Relationship")
        buttons.button(QDialogButtonBox.Ok).setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: 1px solid #3b82f6;
            }
            QPushButton:hover {
                background-color: #3b82f6;
                border: 1px solid #60a5fa;
            }
        """)
        buttons.button(QDialogButtonBox.Cancel).setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #e2e8f0;
                border: 1px solid #475569;
            }
            QPushButton:hover {
                background-color: #475569;
                border: 1px solid #64748b;
                color: #ffffff;
            }
        """)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
    
    def get_values(self) -> dict:
        rel_type = "1-N" if self._type_combo.currentIndex() == 0 else "N-N"
        return {
            "table_a": self._table_a_combo.currentText(),
            "table_b": self._table_b_combo.currentText(),
            "rel_type": rel_type,
        }