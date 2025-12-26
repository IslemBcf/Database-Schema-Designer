import sys

from PySide6.QtWidgets import QApplication

from model.schema import Schema
from view.main_window import MainWindow
from controller.schema_controller import SchemaController


def main() -> None:
    app = QApplication(sys.argv)

    schema = Schema()
    main_window = MainWindow()
    controller = SchemaController(schema, main_window)  # IMPORTANT: keep a reference

    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
