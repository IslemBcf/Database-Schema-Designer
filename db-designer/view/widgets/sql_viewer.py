from PySide6.QtWidgets import QTextEdit


class SQLViewer(QTextEdit):
    """Read-only widget to display generated SQL."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setPlaceholderText("Generated SQL will appear here.")

