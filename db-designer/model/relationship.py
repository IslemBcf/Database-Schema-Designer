from __future__ import annotations

from dataclasses import dataclass

from .table import Table


@dataclass
class Relationship:
    """Represents a relationship between two tables."""
    table_a: Table
    table_b: Table
    rel_type: str  # "1-N" or "N-N"
