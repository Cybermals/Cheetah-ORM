"""Cheetah ORM - MySQL/MariaDB Fields"""

from datetime import datetime

from .common import BackReference, Field, Password


# Classes
# =======
class IntField(Field):
    """An integer field."""
    _type = "INTEGER"

    def __init__(self, **kwargs):
        """Setup this field."""
        super().__init__(**kwargs)
        self._foreign_key = (kwargs["foreign_key"]
                             if "foreign_key" in kwargs else None)

    def __set_name__(self, owner, name):
        """Generate the metadata and get/set SQL for this field and add a foreign key
        backreference if necessary.
        """
        super().__set_name__(owner, name)

        # Generate SQL statements
        self._get = f"SELECT `{name}` FROM `{owner.table}` WHERE id = %s;"
        self._set = f"UPDATE `{owner.table}` SET `{name}` = %s WHERE id = %s;"

        # Add foreign key backreference?
        if self._foreign_key is not None:
            setattr(self._foreign_key, owner.__name__ +
                    "s", BackReference(owner, name))

    def __get__(self, instance, owner=None):
        """Get the value of this field."""
        value = super().__get__(instance, owner)

        # Is this field a foreign key?
        if self._foreign_key is not None:
            return self._foreign_key(id=value)

        return value

    def __set__(self, instance, value):
        """Set the value of this field."""
        # If the value a foreign key instance?
        if self._foreign_key is not None and isinstance(value, self._foreign_key):
            value = value.id

        super().__set__(instance, value)


class BigIntField(IntField):
    """A big integer field."""
    _type = "BIGINT"


class FloatField(Field):
    """A float field."""
    _type = "FLOAT"

    def __set_name__(self, owner, name):
        """Generate the get/set SQL for this field."""
        super().__set_name__(owner, name)

        # Generate SQL statements
        self._get = f"SELECT `{name}` FROM `{owner.table}` WHERE id = %s;"
        self._set = f"UPDATE `{owner.table}` SET `{name}` = %s WHERE id = %s;"


class StringField(Field):
    """A string field."""
    _type = "VARCHAR"

    def __init__(self, **kwargs):
        """Setup this field."""
        super().__init__(**kwargs)
        length = (kwargs["length"] if "length" in kwargs else 65535)
        self._type = ("TEXT" if length > 21844 else f"VARCHAR({length})")

    def __set_name__(self, owner, name):
        """Generate get/set SQL for this field."""
        super().__set_name__(owner, name)

        # Generate SQL statements
        self._get = f"SELECT `{name}` FROM `{owner.table}` WHERE id = %s;"
        self._set = f"UPDATE `{owner.table}` SET `{name}` = %s WHERE id = %s;"


class BinaryField(Field):
    """A field for binary data."""
    _type = "BLOB"

    def __set_name__(self, owner, name):
        """Generate get/set SQL for this field."""
        super().__set_name__(owner, name)

        # Generate SQL statements
        self._get = f"SELECT `{name}` FROM `{owner.table}` WHERE id = %s;"
        self._set = f"UPDATE `{owner.table}` SET `{name}` = %s WHERE id = %s;"


class DateTimeField(Field):
    """A field for temporal data."""
    _type = "DATETIME"

    def __set_name__(self, owner, name):
        """Generate get/set SQL for this field."""
        super().__set_name__(owner, name)

        # Generate SQL statements
        self._get = f"SELECT `{name}` FROM `{owner.table}` WHERE id = %s;"
        self._set = f"UPDATE `{owner.table}` SET `{name}` = %s WHERE id = %s;"

    def __get__(self, instance, owner=None):
        """Get the value of this field."""
        return super().__get__(instance, owner)

    def __set__(self, instance, value):
        """Set the value of this field."""
        super().__set__(instance, value.isoformat())


class PswdField(StringField):
    """A password field."""

    def __set_name__(self, owner, name):
        """Generate get/set SQL for this field."""
        super().__set_name__(owner, name)

        # Generate SQL statements
        self._get = f"SELECT `{name}` FROM `{owner.table}` WHERE id = %s;"
        self._set = f"UPDATE `{owner.table}` SET `{name}` = %s WHERE id = %s;"

    def __get__(self, instance, owner=None):
        """Get the value of this field."""
        return Password(hash=super().__get__(instance, owner))

    def __set__(self, instance, value):
        """Set the value of this field."""
        super().__set__(instance, str(Password(pswd=value)))
