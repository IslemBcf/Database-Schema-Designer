from __future__ import annotations

import sqlite3
from typing import Dict

from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QDialog, QMessageBox

from model.attribute import Attribute
from model.relationship import Relationship
from model.schema import Schema
from model.table import Table

from view.widgets.table_widget import TableWidget
from view.main_window import MainWindow

from .dialogs import NewTableDialog, NewAttributeDialog, RelationshipDialog
from . import sql_engine


class SchemaController:
    """
    Main controller that wires the view and the schema model.

    All application/business logic lives here.
    """

    def __init__(self, schema: Schema, main_window: MainWindow) -> None:
        self.schema = schema
        self.view = main_window

        self._table_widgets: Dict[str, TableWidget] = {}
        self._conn = sqlite3.connect("db_designer.db")
        self._create_tables_in_db()

        self.view.add_table_requested.connect(self.on_add_table)
        self.view.add_attribute_requested.connect(self.on_add_attribute)
        self.view.add_relationship_requested.connect(self.on_add_relationship)
        self.view.generate_sql_requested.connect(self.on_generate_sql)
        self.view.execute_sql_requested.connect(self.on_execute_sql)
        self.view.open_sql_console_requested.connect(self.on_open_sql_console)
        self.view.delete_table_requested.connect(self.on_delete_table)
        self.view.delete_attribute_requested.connect(self.on_delete_attribute)
        self.view.delete_relationship_requested.connect(self.on_delete_relationship)

        self._next_x = 20
        self._next_y = 20
        self._grid_step = 220  # Increased to accommodate larger widgets

    def on_open_sql_console(self) -> None:
        self._recreate_db()

    def _create_tables_in_db(self) -> None:
        """Create all tables from the current schema in the database."""
        create_sql = sql_engine.generate_create_table_statements(self.schema)
        if create_sql.strip():
            try:
                cursor = self._conn.cursor()
                # Use the proper SQL statement splitter that handles quoted strings
                statements = sql_engine._split_sql_statements(create_sql)
                for statement in statements:
                    if statement.strip():
                        cursor.execute(statement)
                self._conn.commit()
            except Exception as e:
                # For now, ignore errors in table creation
                pass

    def _recreate_db(self) -> None:
        """Recreate the database with the current schema."""
        # Drop all existing tables first
        try:
            cursor = self._conn.cursor()
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = cursor.fetchall()
            # Drop each table
            for (table_name,) in tables:
                cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
            self._conn.commit()
        except Exception as e:
            # If there's an error, just continue - might be first run
            pass
        
        # Now create tables with current schema
        self._create_tables_in_db()

    def on_add_table(self) -> None:
        dialog = NewTableDialog(self.view)
        dialog.raise_()
        dialog.activateWindow()
        result = dialog.exec()
        if result != QDialog.Accepted:
            return

        name = dialog.get_table_name()
        if not name:
            return
        if self.schema.find_table(name) is not None:
            return

        table = Table(name=name)
        self.schema.add_table(table)
        self._create_table_widget(table)
        self._recreate_db()

    def on_add_attribute(self) -> None:
        if not self.schema.tables:
            return

        table_names = [t.name for t in self.schema.tables]
        dialog = NewAttributeDialog(table_names, self.view)
        dialog.raise_()
        dialog.activateWindow()
        result = dialog.exec()
        if result != QDialog.Accepted:
            return

        values = dialog.get_values()
        table_name = values["table_name"]
        attr_name = values["attr_name"]
        data_type = values["data_type"]
        is_pk = values["is_pk"]
        is_nullable = values["is_nullable"]
        is_unique = values["is_unique"]

        if not attr_name:
            return

        table = self.schema.find_table(table_name)
        if table is None:
            return
        if any(a.name == attr_name for a in table.attributes):
            return

        attr = Attribute(
            name=attr_name,
            data_type=data_type,
            is_primary_key=is_pk,
            is_nullable=is_nullable,
            is_unique=is_unique,
        )
        table.add_attribute(attr)
        self._refresh_table_widget(table)
        self._recreate_db()

    def on_add_relationship(self) -> None:
        """Handle adding a new relationship."""
        if len(self.schema.tables) < 2:
            return

        table_names = [t.name for t in self.schema.tables]
        dialog = RelationshipDialog(table_names, self.view)
        dialog.raise_()
        dialog.activateWindow()
        result = dialog.exec()

        if result != QDialog.Accepted:
            return

        values = dialog.get_values()
        a_name = values["table_a"]
        b_name = values["table_b"]
        rel_type = values["rel_type"]

        # Validate table selection
        if not a_name or not b_name or a_name == b_name:
            return

        table_a = self.schema.find_table(a_name)
        table_b = self.schema.find_table(b_name)
        if not table_a or not table_b:
            return

        # Check if relationship already exists (bidirectional)
        for existing_rel in self.schema.relationships:
            if ((existing_rel.table_a.name == a_name and existing_rel.table_b.name == b_name) or
                (existing_rel.table_a.name == b_name and existing_rel.table_b.name == a_name)):
                QMessageBox.warning(
                    self.view, 
                    "Duplicate Relationship", 
                    f"A relationship between '{a_name}' and '{b_name}' already exists."
                )
                return

        # Validate primary keys based on relationship type
        if rel_type == "1-N":
            pk_attrs = table_a.get_primary_keys()
            if not pk_attrs:
                QMessageBox.warning(
                    self.view,
                    "Invalid Relationship",
                    f"Table '{a_name}' must have a primary key for 1-N relationships."
                )
                return
        elif rel_type == "N-N":
            a_pks = table_a.get_primary_keys()
            b_pks = table_b.get_primary_keys()
            if not a_pks or not b_pks:
                QMessageBox.warning(
                    self.view,
                    "Invalid Relationship",
                    "Both tables must have primary keys for N-N relationships."
                )
                return

        # Create relationship
        rel = Relationship(table_a=table_a, table_b=table_b, rel_type=rel_type)
        self.schema.add_relationship(rel)

        # Draw relationship line
        widget_a = self._table_widgets.get(a_name)
        widget_b = self._table_widgets.get(b_name)
        if widget_a and widget_b:
            self.view.canvas.add_relationship(a_name, b_name, rel_type, widget_a, widget_b)

        self._recreate_db()

    def on_generate_sql(self) -> None:
        """Generate and show SQL only when button is clicked."""
        # Basic validation
        errors = []
        for table in self.schema.tables:
            if not table.get_primary_keys():
                errors.append(f"Table '{table.name}' has no primary key.")
        if errors:
            # Show error dialog
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self.view, "Schema Validation Error", "\n".join(errors))
            return
        
        sql = sql_engine.generate_create_table_statements(self.schema)
        self.view.set_generated_sql(sql)

    def on_execute_sql(self, sql: str) -> None:
        """Execute SQL using the sql_engine module."""
        if not sql.strip():
            model = QStandardItemModel()
            model.setColumnCount(1)
            model.setHorizontalHeaderLabels(["Message"])
            model.appendRow([QStandardItem("No SQL to execute. Please enter SQL in the console.")])
            self.view.set_query_results_model(model)
            return

        # Use the sql_engine.execute_sql function
        columns, rows = sql_engine.execute_sql(self._conn, sql)
        
        model = QStandardItemModel()
        
        if columns is not None:
            # SELECT query - show results in table
            model.setColumnCount(len(columns))
            model.setHorizontalHeaderLabels(columns)
            if rows:
                for row in rows:
                    items = [QStandardItem(str(value) if value is not None else "NULL") for value in row]
                    model.appendRow(items)
            else:
                # No rows returned
                model.appendRow([QStandardItem("(empty result)")] + [QStandardItem("") for _ in range(len(columns) - 1)])
        else:
            # Non-SELECT query or error - show message
            model.setColumnCount(1)
            model.setHorizontalHeaderLabels(["Result"])
            for row in rows:
                model.appendRow([QStandardItem(str(row[0]))])
        
        self.view.set_query_results_model(model)

    def _create_table_widget(self, table: Table) -> None:
        canvas = self.view.canvas
        
        # Create widget with canvas as parent
        widget = TableWidget(table.name, parent=canvas)
        
        # Set initial content
        lines = [a.name for a in table.attributes]
        widget.update_attributes_text(lines)
        
        # Set size and position
        widget.resize(200, 120)
        widget.move(self._next_x, self._next_y)
        
        # Make widget visible
        widget.show()
        widget.raise_()
        
        # Store widget reference
        self._table_widgets[table.name] = widget

        # Connect widget signals
        widget.delete_table_requested.connect(self.view.delete_table_requested)
        widget.delete_attribute_requested.connect(self.view.delete_attribute_requested)

        # Update relationship drawings with new widget
        self._refresh_all_relationships()

        # Update position for next widget
        self._next_x += self._grid_step
        canvas_width = canvas.width()
        if canvas_width > 0 and self._next_x + self._grid_step > canvas_width:
            self._next_x = 20
            self._next_y += self._grid_step

    def _refresh_table_widget(self, table: Table) -> None:
        widget = self._table_widgets.get(table.name)
        if not widget:
            return
        lines = [a.name for a in table.attributes]
        widget.update_attributes_text(lines)
        # Resize widget to fit content
        widget.adjustSize()
        # Ensure minimum size
        if widget.width() < 180:
            widget.resize(180, widget.height())
        if widget.height() < 100:
            widget.resize(widget.width(), max(100, 50 + len(lines) * 20))

    def _refresh_all_relationships(self) -> None:
        """Refresh all relationship lines on the canvas."""
        self.view.canvas.clear_relationships()
        for rel in self.schema.relationships:
            table_a_name = rel.table_a.name
            table_b_name = rel.table_b.name
            widget_a = self._table_widgets.get(table_a_name)
            widget_b = self._table_widgets.get(table_b_name)
            if widget_a and widget_b:
                self.view.canvas.add_relationship(
                    table_a_name, table_b_name, rel.rel_type, widget_a, widget_b
                )

    def on_delete_table(self, table_name: str) -> None:
        table = self.schema.find_table(table_name)
        if not table:
            return
        # Remove from schema
        self.schema.remove_table(table_name)
        # Remove widget
        widget = self._table_widgets.pop(table_name, None)
        if widget:
            widget.hide()
            widget.deleteLater()
        # Refresh relationships
        self._refresh_all_relationships()
        # Recreate DB
        self._recreate_db()

    def on_delete_attribute(self, table_name: str, attr_name: str) -> None:
        table = self.schema.find_table(table_name)
        if not table:
            return
        # Remove attribute
        table.remove_attribute(attr_name)
        # Refresh widget
        self._refresh_table_widget(table)
        # Recreate DB
        self._recreate_db()

    def on_delete_relationship(self, table_a_name: str, table_b_name: str) -> None:
        # Find and remove relationship
        self.schema.relationships = [
            r for r in self.schema.relationships
            if not ((r.table_a.name == table_a_name and r.table_b.name == table_b_name) or
                    (r.table_a.name == table_b_name and r.table_b.name == table_a_name))
        ]
        # Refresh canvas
        self._refresh_all_relationships()
        # Recreate DB
        self._recreate_db()