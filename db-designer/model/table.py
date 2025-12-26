from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .attribute import Attribute


@dataclass
class Table:
    """Represents a database table in the schema model."""
    name: str
    attributes: List[Attribute] = field(default_factory=list)

    def add_attribute(self, attribute: Attribute) -> None:
        """Add a new attribute if name is unique."""
        if any(a.name == attribute.name for a in self.attributes):
            return
        self.attributes.append(attribute)

    def remove_attribute(self, attr_name: str) -> None:
        """Remove an attribute by name."""
        self.attributes = [a for a in self.attributes if a.name != attr_name]

    def get_primary_keys(self) -> List[Attribute]:
        """Return list of attributes that are primary keys."""
        return [a for a in self.attributes if a.is_primary_key]
