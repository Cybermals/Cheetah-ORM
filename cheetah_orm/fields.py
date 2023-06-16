"""Cheetah ORM - Field Classes

Use the classes derived from the field base class to define fields inside a data model class. Every field
class supports the "default", "length", "unsigned", and "not_null" keyword arguments. Here is a description
of each possible keyword argument:

default  - sets the default value of the field
length   - sets the maximum length of the field (used by IntField, BigIntField, StringField, BlobField,
           and PasswordField)
unsigned - makes the field unsigned (used by IntField, BigIntField, FloatField, and DoubleField)
not_null - prevents the field from being null


The password field automatically hashes any password you store into it and fetching its value gives you
the hash as a password object rather than the original password. The returned password object can be
verified against an unhashed password via the normal equality operator "==".
"""

from collections import OrderedDict
from datetime import datetime

from passlib.hash import pbkdf2_sha256

from .constants import *


# Classes
# =======
class Field(object):
    """Base class for a field."""
    def __init__(self, **kwargs):
        """Setup this field."""
        self.default = kwargs.get("default")
        self.length  = kwargs.get("length")

        # Calculate flags
        self.flags = 0

        if kwargs.get("unsigned", False):
            self.flags |= FIELD_TYPE_UNSIGNED

        if kwargs.get("not_null", False):
            self.flags |= FIELD_TYPE_NOT_NULL

    def __set_name__(self, owner, name):
        """Store the field name for later use."""
        self.name = name

    def __get__(self, obj, objtype=None):
        """Get the value of this field."""
        return obj._data[self.name]
    
    def __set__(self, obj, value):
        """Set the value of this field."""
        obj._data[self.name] = value


class IntField(Field):
    """An integer field."""
    def __set_name__(self, owner, name):
        """Add the metadata for this field to the parent data model."""
        super().__set_name__(owner, name)

        # Create the model metadata if it doesn't exist
        if not owner._fields:
            owner._fields = []

        # Add this field to the model metadata
        owner._fields.append((
            name, 
            FIELD_TYPE_INT | self.flags, 
            self.length if self.length else 10, 
            self.default
        ))


class BigIntField(Field):
    """A big integer field."""
    def __set_name__(self, owner, name):
        """Add the metadata for this field to the parent data model."""
        super().__set_name__(owner, name)

        # Create the model metadata if it doesn't exist
        if not owner._fields:
            owner._fields = []

        # Add this field to the model metadata
        owner._fields.append((
            name, 
            FIELD_TYPE_BIGINT | self.flags, 
            self.length if self.length else 19, 
            self.default
        ))


class FloatField(Field):
    """A float field."""
    def __set_name__(self, owner, name):
        """Add the metadata for this field to the parent data model."""
        super().__set_name__(owner, name)

        # Create the model metadata if it doesn't exist
        if not owner._fields:
            owner._fields = []

        # Add this field to the model metadata
        owner._fields.append((
            name, 
            FIELD_TYPE_FLOAT | self.flags, 
            None,             # length doesn't apply to this data type
            self.default
        ))


class DoubleField(Field):
    """A double-precision float field."""
    def __set_name__(self, owner, name):
        """Add the metadata for this field to the parent data model."""
        super().__set_name__(owner, name)

        # Create the model metadata if it doesn't exist
        if not owner._fields:
            owner._fields = []

        # Add this field to the model metadata
        owner._fields.append((
            name, 
            FIELD_TYPE_DOUBLE | self.flags, 
            None,             # length doesn't apply to this data type
            self.default
        ))


class StringField(Field):
    """A string field."""
    def __set_name__(self, owner, name):
        """Add the metadata for this field to the parent data model."""
        super().__set_name__(owner, name)

        # Create the model metadata if it doesn't exist
        if not owner._fields:
            owner._fields = []

        # Add this field to the model metadata
        owner._fields.append((
            name, 
            FIELD_TYPE_STRING | self.flags, 
            self.length if self.length else 256, 
            self.default
        ))


class BlobField(Field):
    """A blob field."""
    def __set_name__(self, owner, name):
        """Add the metadata for this field to the parent data model."""
        super().__set_name__(owner, name)

        # Create the model metadata if it doesn't exist
        if not owner._fields:
            owner._fields = []

        # Add this field to the model metadata
        owner._fields.append((
            name, 
            FIELD_TYPE_BLOB | self.flags, 
            self.length if self.length else 256, 
            self.default
        ))


class DateTimeField(Field):
    """A datetime field."""
    def __set_name__(self, owner, name):
        """Add the metadata for this field to the parent data model."""
        super().__set_name__(owner, name)

        # Create the model metadata if it doesn't exist
        if not owner._fields:
            owner._fields = []

        # Add this field to the model metadata
        owner._fields.append((
            name, 
            FIELD_TYPE_DATETIME | self.flags, 
            None,        # length doesn't apply to this data type 
            self.default
        ))

    def __set__(self, obj, value):
        """Set the value of this field."""
        # Handle special values
        if isinstance(value, str) and value.lower() == "now()":
            value = datetime.now()

        super().__set__(obj, value)


class Password(object):
    """Container for a password."""
    def __init__(self, value):
        """Setup this password."""
        self.value = value

    def __eq__(self, value):
        """Compare the given password with the password hash."""
        return pbkdf2_sha256.verify(value, self.value)


class PasswordField(Field):
    """A password field."""
    def __set_name__(self, owner, name):
        """Add the metadata for this field to the parent data model."""
        super().__set_name__(owner, name)

        # Create the model metadata if it doesn't exist
        if not owner._fields:
            owner._fields = []

        # Add this field to the model metadata
        owner._fields.append((
            name, 
            FIELD_TYPE_PSWD | self.flags, 
            self.length if self.length else 256, 
            self.default
        ))

    def __get__(self, obj, objtype=None):
        """Return the password."""
        return Password(super().__get__(obj, objtype))

    def __set__(self, obj, value):
        """Hash the given password before storing it."""
        # Handle None
        if value is None:
            value = ""

        super().__set__(obj, pbkdf2_sha256.hash(value))
