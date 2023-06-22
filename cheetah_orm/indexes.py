"""Cheetah ORM - Index Classes

Use the index classes to add varies types of indexes to a data model. The index, primary key, and unique
index classes accept one or more field names as parameters. Each given column will be used for the index.
The foreign key class accepts one data model object, and one field name as required parameters that refer
to a field in another data model. You can also optionally control the foreign key behavior by setting the
"on_delete" and/or "on_update" parameters to one of the FK_* constants.
"""

from .constants import *


# Classes
# =======
class Index(object):
    """An normal index."""
    def __init__(self, *args):
        """Setup this index."""
        self.fields = args

    def __set_name__(self, owner, name):
        """Add this index to the data model."""
        # Create the model metadata if it doesn't exist
        if not owner._indexes:
            owner._indexes = []

        # Add this index to the model metadata
        owner._indexes.append((
            name,
            INDEX_TYPE_KEY,
            self.fields
        ))


class UniqueIndex(object):
    """A unique index."""
    def __init__(self, *args):
        """Setup this index."""
        self.fields = args

    def __set_name__(self, owner, name):
        """Add this index to the data model."""
        # Create the model metadata if it doesn't exist
        if not owner._indexes:
            owner._indexes = []

        # Add this index to the model metadata
        owner._indexes.append((
            name,
            INDEX_TYPE_UNIQUE_KEY,
            self.fields
        ))


class ForeignKey(object):
    """A foreign key."""
    def __init__(self, model, field, on_delete=FK_CASCADE, on_update=FK_RESTRICT):
        """Setup this index."""
        self.model     = model
        self.field     = field
        self.on_delete = on_delete
        self.on_update = on_update

    def __set_name__(self, owner, name):
        """Add this index to the data model."""
        # Create the model metadata if it doesn't exist
        if not owner._indexes:
            owner._indexes = []

        # Add this index to the model metadata
        owner._indexes.append((
            name,
            INDEX_TYPE_FOREIGN_KEY,
            (
                self.model,
                self.field
            ),
            (
                self.on_delete,
                self.on_update
            )
        ))
