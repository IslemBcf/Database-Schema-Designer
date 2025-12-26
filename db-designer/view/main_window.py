from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QLabel,
    QPlainTextEdit,
    QTableView,
    QDialog,
    QDialogButtonBox,
    QScrollArea,
    QHeaderView,
    QMessageBox,
)


from .widgets.sql_viewer import SQLViewer
from .widgets.canvas_widget import CanvasWidget


class SQLGeneratorDialog(QDialog):
    """Dialog to show generated SQL with copy functionality."""
    
    def __init__(self, sql_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generated SQL")
        self.resize(850, 650)
        
        # Apply dark blue night theme
        self.setStyleSheet("""
            QDialog {
                background-color: #0a1629;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header with title and info
        header_layout = QHBoxLayout()
        
        title = QLabel("📋 Generated SQL Schema")
        title.setStyleSheet("""
            QLabel {
                font-weight: 700;
                font-size: 24px;
                color: #e2e8f0;
                letter-spacing: 0.5px;
            }
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Info label
        info_label = QLabel("Copy this SQL to create your database schema")
        info_label.setStyleSheet("""
            QLabel {
                color: #cbd5e1;
                font-size: 13px;
                background-color: #1e3a5f;
                padding: 10px 18px;
                border-radius: 10px;
                border: 1px solid #3b82f6;
            }
        """)
        header_layout.addWidget(info_label)
        
        layout.addLayout(header_layout)
        
        # SQL viewer
        self.sql_view = SQLViewer()
        self.sql_view.setPlainText(sql_text)
        self.sql_view.setStyleSheet("""
            QTextEdit {
                background-color: #0d1b2a;
                border: 2px solid #2563eb;
                border-radius: 12px;
                padding: 24px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 14px;
                color: #e2e8f0;
                selection-background-color: #3b82f6;
                selection-color: white;
                line-height: 1.8;
            }
        """)
        layout.addWidget(self.sql_view)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Copy button
        copy_btn = QPushButton("📋 Copy to Clipboard")
        copy_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #1e40af);
                color: white;
                border: 1px solid #3b82f6;
                padding: 14px 36px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                min-width: 160px;
                max-height: 46px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #2563eb);
                border: 1px solid #60a5fa;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        copy_btn.setFixedHeight(44)
        copy_btn.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(copy_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #e2e8f0;
                border: 1px solid #475569;
                padding: 14px 36px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                min-width: 110px;
                max-height: 46px;
            }
            QPushButton:hover {
                background-color: #475569;
                border: 1px solid #64748b;
                color: #ffffff;
            }
        """)
        close_btn.setFixedHeight(44)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _copy_to_clipboard(self):
        """Copy SQL to clipboard."""
        from PySide6.QtGui import QClipboard
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.sql_view.toPlainText())
        
        # Show brief confirmation
        QMessageBox.information(self, "Copied", "SQL copied to clipboard!", QMessageBox.Ok)


class SQLConsoleDialog(QDialog):
    """Enhanced SQL Console with better UX."""
    
    execute_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SQL Console")
        self.setMinimumSize(800, 600)
        self.resize(950, 750)
        
        # Make the dialog resizable
        self.setSizeGripEnabled(True)
        
        # Apply dark blue night theme
        self.setStyleSheet("""
            QDialog {
                background-color: #0a1629;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("⚡ SQL Console")
        title.setStyleSheet("""
            QLabel {
                font-weight: 700;
                font-size: 24px;
                color: #e2e8f0;
                letter-spacing: 0.5px;
            }
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # SQL input section
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(12)
        
        input_header = QHBoxLayout()
        input_label = QLabel("📝 SQL Query Editor")
        input_label.setStyleSheet("font-weight: 600; color: #cbd5e1; font-size: 14px;")
        input_header.addWidget(input_label)
        input_header.addStretch()
        
        input_layout.addLayout(input_header)
        
        self.sql_console = QPlainTextEdit()
        self.sql_console.setPlaceholderText(
            "-- Write your SQL queries here\n"
            "-- Example:\n"
            "INSERT INTO \"student\" (\"id\", \"name\") VALUES (1, 'Alice Johnson');\n"
            "INSERT INTO \"student\" (\"id\", \"name\") VALUES (2, 'Bob Smith');\n"
            "SELECT * FROM \"student\";"
        )
        self.sql_console.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0d1b2a;
                border: 2px solid #2563eb;
                border-radius: 12px;
                padding: 20px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 14px;
                color: #e2e8f0;
                selection-background-color: #3b82f6;
                selection-color: white;
                line-height: 1.7;
            }
            QPlainTextEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)
        self.sql_console.setMinimumHeight(200)
        input_layout.addWidget(self.sql_console)
        
        layout.addWidget(input_container)
        
        # Execute button
        execute_layout = QHBoxLayout()
        
        self.btn_execute = QPushButton("▶️ Execute Query")
        self.btn_execute.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0891b2, stop:1 #06b6d4);
                color: white;
                border: 1px solid #22d3ee;
                padding: 16px 40px;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
                min-width: 190px;
                max-height: 50px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #06b6d4, stop:1 #22d3ee);
                border: 1px solid #67e8f9;
            }
            QPushButton:pressed {
                background-color: #0e7490;
            }
        """)
        self.btn_execute.setFixedHeight(48)
        self.btn_execute.clicked.connect(self._on_execute)
        execute_layout.addStretch()
        execute_layout.addWidget(self.btn_execute)
        execute_layout.addStretch()
        
        layout.addLayout(execute_layout)
        
        # Results section
        results_container = QWidget()
        results_layout = QVBoxLayout(results_container)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(12)
        
        results_header = QHBoxLayout()
        results_label = QLabel("📊 Query Results")
        results_label.setStyleSheet("font-weight: 600; color: #cbd5e1; font-size: 14px;")
        results_header.addWidget(results_label)
        
        self.result_status = QLabel("")
        self.result_status.setStyleSheet("color: #94a3b8; font-size: 12px;")
        results_header.addWidget(self.result_status)
        results_header.addStretch()
        
        results_layout.addLayout(results_header)
        
        self.results_view = QTableView()
        self.results_view.setStyleSheet("""
            QTableView {
                background-color: #0d1b2a;
                border: 2px solid #1e3a5f;
                border-radius: 12px;
                gridline-color: #1e3a5f;
                selection-background-color: #2563eb;
                selection-color: white;
                font-size: 13px;
                color: #e2e8f0;
            }
            QTableView::item {
                padding: 12px;
                color: #e2e8f0;
                background-color: #0d1b2a;
            }
            QTableView::item:alternate {
                background-color: #1a2332;
                color: #e2e8f0;
            }
            QTableView::item:selected {
                background-color: #2563eb;
                color: white;
            }
            QHeaderView::section {
                background-color: #1e293b;
                color: #e2e8f0;
                padding: 14px;
                border: none;
                border-bottom: 2px solid #334155;
                font-weight: 600;
                font-size: 13px;
            }
        """)
        self.results_view.setAlternatingRowColors(True)
        self.results_view.horizontalHeader().setStretchLastSection(True)
        self.results_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.results_view.setMinimumHeight(200)
        
        # Wrap results view in scroll area for better scrolling
        results_scroll = QScrollArea()
        results_scroll.setWidget(self.results_view)
        results_scroll.setWidgetResizable(True)
        results_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1e293b;
                width: 14px;
                border-radius: 7px;
                border: 1px solid #334155;
            }
            QScrollBar::handle:vertical {
                background-color: #475569;
                border-radius: 7px;
                min-height: 40px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #64748b;
            }
            QScrollBar:horizontal {
                background-color: #1e293b;
                height: 14px;
                border-radius: 7px;
                border: 1px solid #334155;
            }
            QScrollBar::handle:horizontal {
                background-color: #475569;
                border-radius: 7px;
                min-width: 40px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #64748b;
            }
        """)
        results_layout.addWidget(results_scroll, 1)
        
        layout.addWidget(results_container, 1)
        
        # Bottom button layout
        bottom_layout = QHBoxLayout()
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear Editor")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: 1px solid #ef4444;
                padding: 12px 28px;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                min-width: 130px;
                max-height: 42px;
            }
            QPushButton:hover {
                background-color: #ef4444;
                border: 1px solid #f87171;
            }
        """)
        clear_btn.setFixedHeight(40)
        clear_btn.clicked.connect(self.sql_console.clear)
        bottom_layout.addWidget(clear_btn)
        
        bottom_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #e2e8f0;
                border: 1px solid #475569;
                padding: 12px 36px;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                min-width: 110px;
                max-height: 42px;
            }
            QPushButton:hover {
                background-color: #475569;
                border: 1px solid #64748b;
                color: #ffffff;
            }
        """)
        close_btn.setFixedHeight(40)
        close_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(close_btn)
        
        layout.addLayout(bottom_layout)
    
    def _on_execute(self):
        # Get the SQL text from the console
        raw_sql = self.sql_console.toPlainText()
        
        # Strip whitespace and check if there's content
        sql = raw_sql.strip() if raw_sql else ""
        
        if not sql:
            self.result_status.setText("⚠️ No SQL to execute - Please enter a SQL query")
            return
        
        # Execute the SQL - let the SQL engine handle validation
        self.result_status.setText("⏳ Executing...")
        self.execute_requested.emit(sql)
    
    def set_query_results_model(self, model):
        self.results_view.setModel(model)
        # Update status based on results
        if model.rowCount() > 0:
            self.result_status.setText(f"{model.rowCount()} row(s) returned")
        else:
            self.result_status.setText("Query executed successfully")
        
        # Auto-resize columns to content
        self.results_view.resizeColumnsToContents()


class MainWindow(QMainWindow):
    """
    Main application window with modern left sidebar design.
    """

    add_table_requested = Signal()
    add_attribute_requested = Signal()
    add_relationship_requested = Signal()
    generate_sql_requested = Signal()
    execute_sql_requested = Signal(str)
    open_sql_console_requested = Signal()
    delete_table_requested = Signal(str)
    delete_attribute_requested = Signal(str, str)
    delete_relationship_requested = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Database Schema Designer")
        self.resize(1600, 1000)
        
        # Store dialogs
        self.sql_generator_dialog = None
        self.sql_console_dialog = None
        
        # Apply dark blue night theme styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a1629;
            }
            QFrame#sidebar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f1b2e, stop:1 #1a2332);
                border-right: 1px solid #1e3a5f;
            }
            QFrame#canvas {
                background-color: #0d1b2a;
                border: 1px solid #1e3a5f;
                border-radius: 12px;
            }
        """)

        # Main container with horizontal layout (sidebar + content)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo/Branding Section
        logo_container = QFrame()
        logo_container.setFixedHeight(160)
        logo_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e40af, stop:1 #1e3a8a);
                border-bottom: 1px solid #3b82f6;
            }
        """)
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(20, 20, 20, 20)
        logo_layout.setSpacing(8)
        
        # Logo icon/text
        logo_label = QLabel("🗄️")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                background: transparent;
                border: none;
            }
        """)
        logo_layout.addWidget(logo_label)
        
        # App name
        app_name = QLabel("Schema Designer")
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: 700;
                color: #ffffff;
                background: transparent;
            }
        """)
        logo_layout.addWidget(app_name)
        
        # Tagline
        tagline = QLabel("Database Modeling Tool")
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #e0f2fe;
                background: transparent;
                font-weight: 500;
            }
        """)
        logo_layout.addWidget(tagline)
        
        sidebar_layout.addWidget(logo_container)

        # Navigation Buttons Section
        nav_container = QWidget()
        nav_container.setStyleSheet("background-color: transparent;")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(18, 25, 18, 25)
        nav_layout.setSpacing(10)

        # Sidebar button style - dark blue night theme
        sidebar_button_style = """
            QPushButton {
                background-color: #1e293b;
                color: #cbd5e1;
                border: 1px solid #334155;
                padding: 16px 22px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
                text-align: left;
                min-height: 52px;
            }
            QPushButton:hover {
                background-color: #2563eb;
                color: #ffffff;
                border: 1px solid #3b82f6;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #1e40af;
                border: 1px solid #2563eb;
            }
        """

        # Create navigation buttons
        self.btn_add_table = QPushButton("📊 Add Table")
        self.btn_add_table.setStyleSheet(sidebar_button_style)
        self.btn_add_table.setToolTip("Create a new table")
        
        self.btn_add_attribute = QPushButton("📝 Add Attribute")
        self.btn_add_attribute.setStyleSheet(sidebar_button_style)
        self.btn_add_attribute.setToolTip("Add a column to existing table")
        
        self.btn_add_relationship = QPushButton("🔗 Add Relationship")
        self.btn_add_relationship.setStyleSheet(sidebar_button_style)
        self.btn_add_relationship.setToolTip("Link tables with relationships")
        
        # Generate SQL button style (purple accent)
        sql_button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c3aed, stop:1 #6366f1);
                color: #ffffff;
                border: 1px solid #8b5cf6;
                padding: 16px 22px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
                text-align: left;
                min-height: 52px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8b5cf6, stop:1 #818cf8);
                border: 1px solid #a78bfa;
            }
            QPushButton:pressed {
                background-color: #6d28d9;
            }
        """
        
        self.btn_generate_sql = QPushButton("⚡ Generate SQL")
        self.btn_generate_sql.setStyleSheet(sql_button_style)
        self.btn_generate_sql.setToolTip("Generate CREATE TABLE statements")
        
        # SQL Console button style (teal accent)
        console_button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0891b2, stop:1 #06b6d4);
                color: #ffffff;
                border: 1px solid #22d3ee;
                padding: 16px 22px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
                text-align: left;
                min-height: 52px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #06b6d4, stop:1 #22d3ee);
                border: 1px solid #67e8f9;
            }
            QPushButton:pressed {
                background-color: #0e7490;
            }
        """
        
        self.btn_execute_sql = QPushButton("▶️ SQL Console")
        self.btn_execute_sql.setStyleSheet(console_button_style)
        self.btn_execute_sql.setToolTip("Open SQL console to run queries")

        # Add buttons to navigation layout
        nav_layout.addWidget(self.btn_add_table)
        nav_layout.addWidget(self.btn_add_attribute)
        nav_layout.addWidget(self.btn_add_relationship)
        nav_layout.addWidget(self.btn_generate_sql)
        nav_layout.addWidget(self.btn_execute_sql)
        nav_layout.addStretch()

        sidebar_layout.addWidget(nav_container)
        main_layout.addWidget(sidebar)

        # Main Content Area (Canvas)
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #0a1629;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Canvas header
        canvas_header = QHBoxLayout()
        canvas_title = QLabel("🎨 Schema Canvas")
        canvas_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: 700;
                color: #e2e8f0;
                letter-spacing: 0.5px;
            }
        """)
        canvas_header.addWidget(canvas_title)
        
        canvas_hint = QLabel("Drag tables to reposition • Right-click for options")
        canvas_hint.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #94a3b8;
                padding-left: 15px;
            }
        """)
        canvas_header.addWidget(canvas_hint)
        canvas_header.addStretch()
        
        content_layout.addLayout(canvas_header)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1e293b;
                width: 14px;
                border-radius: 7px;
                border: 1px solid #334155;
            }
            QScrollBar::handle:vertical {
                background-color: #475569;
                border-radius: 7px;
                min-height: 40px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #64748b;
            }
            QScrollBar:horizontal {
                background-color: #1e293b;
                height: 14px;
                border-radius: 7px;
                border: 1px solid #334155;
            }
            QScrollBar::handle:horizontal {
                background-color: #475569;
                border-radius: 7px;
                min-width: 40px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #64748b;
            }
        """)
        
        self.canvas = CanvasWidget()
        self.canvas.setObjectName("canvas")
        self.canvas.setFrameShape(QFrame.StyledPanel)
        self.canvas.setLayout(None)
        self.canvas.setMinimumSize(1250, 820)
        
        scroll_area.setWidget(self.canvas)
        content_layout.addWidget(scroll_area, 1)
        
        main_layout.addWidget(content_widget, 1)

        # Connect buttons to signal handlers
        self.btn_add_table.clicked.connect(self._on_add_table_clicked)
        self.btn_add_attribute.clicked.connect(self._on_add_attribute_clicked)
        self.btn_add_relationship.clicked.connect(self._on_add_relationship_clicked)
        self.btn_generate_sql.clicked.connect(self._on_generate_sql_clicked)
        self.btn_execute_sql.clicked.connect(self._on_execute_sql_clicked)

    # API for controller

    def set_generated_sql(self, sql: str) -> None:
        """Show generated SQL in a dialog."""
        self.sql_generator_dialog = SQLGeneratorDialog(sql, self)
        self.sql_generator_dialog.exec()

    def set_query_results_model(self, model) -> None:
        """Update query results in the console dialog."""
        if self.sql_console_dialog:
            self.sql_console_dialog.set_query_results_model(model)

    # Slots that only emit signals

    def _on_add_table_clicked(self) -> None:
        self.add_table_requested.emit()

    def _on_add_attribute_clicked(self) -> None:
        self.add_attribute_requested.emit()

    def _on_add_relationship_clicked(self) -> None:
        self.add_relationship_requested.emit()

    def _on_generate_sql_clicked(self) -> None:
        self.generate_sql_requested.emit()

    def _on_execute_sql_clicked(self) -> None:
        """Open SQL console dialog."""
        self.open_sql_console_requested.emit()
        self.sql_console_dialog = SQLConsoleDialog(self)
        self.sql_console_dialog.execute_requested.connect(
            lambda sql: self.execute_sql_requested.emit(sql)
        )
        self.sql_console_dialog.exec()
