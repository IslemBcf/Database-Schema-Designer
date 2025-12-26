from __future__ import annotations

import sqlite3
import re
from typing import List, Tuple, Optional

from model.schema import Schema
from model.table import Table
from model.attribute import Attribute


def _quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def generate_create_table_statements(schema: Schema) -> str:
    lines: List[str] = []
    fk_constraints: dict[str, List[str]] = {}
    junction_tables: List[Tuple[str, str, str]] = []

    # Track which tables need foreign key columns added
    fk_columns_to_add: dict[str, List[Attribute]] = {}
    
    for rel in schema.relationships:
        a = rel.table_a
        b = rel.table_b
        if rel.rel_type == "1-N":
            pk_attrs = a.get_primary_keys()
            if not pk_attrs:
                # Skip this relationship if no primary key exists
                # This should have been caught earlier, but handle gracefully
                continue
            for pk in pk_attrs:
                # Check if table_b has a column with the same name as the primary key
                fk_column_exists = any(attr.name == pk.name for attr in b.attributes)
                if not fk_column_exists:
                    # We need to add this foreign key column to table_b
                    fk_attr = Attribute(
                        name=pk.name,
                        data_type=pk.data_type,
                        is_primary_key=False,
                        is_nullable=True,
                        is_unique=False
                    )
                    fk_columns_to_add.setdefault(b.name, []).append(fk_attr)
                
                fk_constraints.setdefault(b.name, [])
                fk_constraints[b.name].append(
                    f"FOREIGN KEY ({_quote_identifier(pk.name)}) "
                    f"REFERENCES {_quote_identifier(a.name)}({_quote_identifier(pk.name)})"
                )
        elif rel.rel_type == "N-N":
            name = f"{a.name}_{b.name}"
            junction_tables.append((name, a.name, b.name))

    for table in schema.tables:
        col_defs: List[str] = []
        pk_cols: List[str] = []

        # Add regular attributes
        for attr in table.attributes:
            parts = [f"{_quote_identifier(attr.name)} {attr.data_type}"]
            if attr.is_primary_key:
                pk_cols.append(_quote_identifier(attr.name))
            if not attr.is_nullable:
                parts.append("NOT NULL")
            if attr.is_unique and not attr.is_primary_key:
                parts.append("UNIQUE")
            col_defs.append(" ".join(parts))
        
        # Add foreign key columns if needed (for 1-N relationships)
        if table.name in fk_columns_to_add:
            for fk_attr in fk_columns_to_add[table.name]:
                # Only add if it doesn't already exist
                if not any(attr.name == fk_attr.name for attr in table.attributes):
                    parts = [f"{_quote_identifier(fk_attr.name)} {fk_attr.data_type}"]
                    if not fk_attr.is_nullable:
                        parts.append("NOT NULL")
                    col_defs.append(" ".join(parts))

        if pk_cols:
            col_defs.append(f"PRIMARY KEY ({', '.join(pk_cols)})")

        col_defs.extend(fk_constraints.get(table.name, []))

        create_stmt = (
            f"CREATE TABLE IF NOT EXISTS {_quote_identifier(table.name)} (\n    "
            + ",\n    ".join(col_defs)
            + "\n);\n"
        )
        lines.append(create_stmt)

    for jname, aname, bname in junction_tables:
        atable: Optional[Table] = schema.find_table(aname)
        btable: Optional[Table] = schema.find_table(bname)
        if not atable or not btable:
            continue
        apks = atable.get_primary_keys()
        bpks = btable.get_primary_keys()
        if not apks or not bpks:
            continue

        cols = []
        fk_constraints_junction = []
        pk_cols = []
        for apk in apks:
            col_name = f"{aname.lower()}_{apk.name}"
            cols.append(f"{_quote_identifier(col_name)} {apk.data_type} NOT NULL")
            pk_cols.append(col_name)
            fk_constraints_junction.append(
                f"FOREIGN KEY ({_quote_identifier(col_name)}) "
                f"REFERENCES {_quote_identifier(aname)}({_quote_identifier(apk.name)})"
            )
        for bpk in bpks:
            col_name = f"{bname.lower()}_{bpk.name}"
            cols.append(f"{_quote_identifier(col_name)} {bpk.data_type} NOT NULL")
            pk_cols.append(col_name)
            fk_constraints_junction.append(
                f"FOREIGN KEY ({_quote_identifier(col_name)}) "
                f"REFERENCES {_quote_identifier(bname)}({_quote_identifier(bpk.name)})"
            )
        cols.append(f"PRIMARY KEY ({', '.join(_quote_identifier(c) for c in pk_cols)})")
        cols.extend(fk_constraints_junction)
        create_stmt = (
            f"CREATE TABLE IF NOT EXISTS {_quote_identifier(jname)} (\n    "
            + ",\n    ".join(cols)
            + "\n);\n"
        )
        lines.append(create_stmt)

    return "".join(lines)


def _split_sql_statements(sql: str) -> List[str]:
    """Split SQL string into individual statements, handling quoted strings and comments."""
    statements = []
    current = []
    in_string = False
    string_char = None
    in_line_comment = False
    in_block_comment = False
    
    i = 0
    while i < len(sql):
        char = sql[i]
        
        # Handle block comments /* */
        if not in_string and not in_line_comment:
            if char == '/' and i + 1 < len(sql) and sql[i + 1] == '*':
                in_block_comment = True
                i += 1  # skip *
                continue
            elif char == '*' and i + 1 < len(sql) and sql[i + 1] == '/':
                in_block_comment = False
                i += 1  # skip /
                continue
        
        if in_block_comment:
            i += 1
            continue
        
        # Handle line comments --
        if not in_string and char == '-' and i + 1 < len(sql) and sql[i + 1] == '-':
            in_line_comment = True
        
        if in_line_comment:
            if char == '\n':
                in_line_comment = False
            i += 1
            continue
        
        # Handle string literals
        if char in ('"', "'") and (i == 0 or sql[i-1] != '\\'):
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
                string_char = None
        
        # Handle semicolon
        if char == ';' and not in_string:
            stmt = ''.join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
        else:
            current.append(char)
        
        i += 1
    
    # Add last statement if exists
    stmt = ''.join(current).strip()
    if stmt:
        statements.append(stmt)
    
    return statements


def execute_sql(conn: sqlite3.Connection, sql: str) -> Tuple[Optional[list[str]], list[tuple]]:
    cursor = conn.cursor()

    if not sql.strip():
        return None, [("No SQL",)]

    try:
        # Split statements properly
        statements = _split_sql_statements(sql)
        
        if not statements:
            return None, [("No valid SQL statements",)]
        
        last_columns = None
        last_rows = []
        total_affected = 0
        
        for statement in statements:
            if not statement:
                continue
                
            cursor.execute(statement)
            
            # Check if this was a SELECT statement
            if cursor.description:
                last_columns = [d[0] for d in cursor.description]
                last_rows = cursor.fetchall()
            else:
                # For INSERT, UPDATE, DELETE
                total_affected += cursor.rowcount
        
        conn.commit()
        
        # If the last statement was a SELECT, return its results
        if last_columns:
            return last_columns, last_rows
        
        # Otherwise, return success message with row count
        return None, [(f"Success: {total_affected} rows affected",)]
        
    except sqlite3.Error as e:
        conn.rollback()
        return None, [(f"SQL Error: {str(e)}",)]
    except Exception as e:
        conn.rollback()
        return None, [(f"Error: {str(e)}",)]