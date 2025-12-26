from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Attribute:
    """Represents a column/attribute of a table in the schema model."""
    name: str
    data_type: str
    is_primary_key: bool = False
    is_nullable: bool = True
    is_unique: bool = False
