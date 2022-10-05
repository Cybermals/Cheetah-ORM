"""Cheetah ORM - Dummy Fields"""

from .common import Field


#Classes
#=======
class IntField(Field):
    """An integer field."""
    pass


class FloatField(Field):
    """A float field."""
    pass


class StringField(Field):
    """A string field."""
    pass


class BinaryField(Field):
    """A field for binary data."""
    pass


class DateTimeField(Field):
    """A field for temporal data."""
    pass


class PswdField(Field):
    """A password field."""
    pass