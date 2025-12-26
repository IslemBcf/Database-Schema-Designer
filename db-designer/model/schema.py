from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .table import Table
from .relationship import Relationship


@dataclass
class Schema:
    """Root schema model holding tables and relationships."""
    tables: List[Table] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)

    def add_table(self, table: Table) -> None:
        if self.find_table(table.name) is not None:
            return
        self.tables.append(table)

    def remove_table(self, table_name: str) -> None:
        self.tables = [t for t in self.tables if t.name != table_name]
        # Remove relationships that involve this table
        self.relationships = [
            r
            for r in self.relationships
            if r.table_a.name != table_name and r.table_b.name != table_name
        ]

    def add_relationship(self, relationship: Relationship) -> None:
        for r in self.relationships:
            if (
                r.table_a is relationship.table_a
                and r.table_b is relationship.table_b
                and r.rel_type == relationship.rel_type
            ):
                return
        self.relationships.append(relationship)

    def find_table(self, name: str) -> Optional[Table]:
        for t in self.tables:
            if t.name == name:
                return t
        return None
