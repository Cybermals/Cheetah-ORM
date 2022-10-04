"""Cheetah ORM - SQLite3 Fields"""

from datetime import datetime

from .common import Field, Password


#Classes
#=======
class IntField(Field):
    """An integer field."""
    _type = "INT"

    def __set_name__(self, owner, name):
        """Generate the metadata and get/set SQL for this field."""
        super().__set_name__(owner, name)

        #Generate SQL statements
        self._get = f"SELECT {name} FROM {owner.table} WHERE id = ?;"
        self._set = f"UPDATE {owner.table} SET {name} = ? WHERE id = ?;"


class FloatField(Field):
    """A float field."""
    _type = "FLOAT"

    def __set_name__(self, owner, name):
        """Generate the get/set SQL for this field."""
        super().__set_name__(owner, name)

        #Generate SQL statements
        self._get = f"SELECT {name} FROM {owner.table} WHERE id = ?;"
        self._set = f"UPDATE {owner.table} SET {name} = ? WHERE id = ?;"


class StringField(Field):
    """A string field."""
    _type = "VARCHAR"

    def __init__(self, **kwargs):
        """Setup this field."""
        super().__init__(**kwargs)
        length = (kwargs["length"] if "length" in kwargs else 65535)
        self._type = f"VARCHAR({length})"

    def __set_name__(self, owner, name):
        """Generate get/set SQL for this field."""
        super().__set_name__(owner, name)

        #Generate SQL statements
        self._get = f"SELECT {name} FROM {owner.table} WHERE id = ?;"
        self._set = f"UPDATE {owner.table} SET {name} = ? WHERE id = ?;"


class BinaryField(Field):
    """A field for binary data."""
    _type = "BLOB"

    def __set_name__(self, owner, name):
        """Generate get/set SQL for this field."""
        super().__set_name__(owner, name)

        #Generate SQL statements
        self._get = f"SELECT {name} FROM {owner.table} WHERE id = ?;"
        self._set = f"UPDATE {owner.table} SET {name} = ? WHERE id = ?;"


class DateTimeField(Field):
    """A field for temporal data."""
    _type = "DATETIME"

    def __set_name__(self, owner, name):
        """Generate get/set SQL for this field."""
        super().__set_name__(owner, name)

        #Generate SQL statements
        self._get = f"SELECT {name} FROM {owner.table} WHERE id = ?;"
        self._set = f"UPDATE {owner.table} SET {name} = ? WHERE id = ?;"

    def __get__(self, instance, owner = None):
        """Get the value of this field."""
        return datetime.fromtimestamp(super().__get__(instance, owner))

    def __set__(self, instance, value):
        """Set the value of this field."""
        super().__set__(instance, value.timestamp())


class PswdField(StringField):
    """A password field."""
    def __set_name__(self, owner, name):
        """Generate get/set SQL for this field."""
        super().__set_name__(owner, name)

        #Generate SQL statements
        self._get = f"SELECT {name} FROM {owner.table} WHERE id = ?;"
        self._set = f"UPDATE {owner.table} SET {name} = ? WHERE id = ?;"

    def __get__(self, instance, owner = None):
        """Get the value of this field."""
        return Password(hash = super().__get__(instance, owner))

    def __set__(self, instance, value):
        """Set the value of this field."""
        super().__set__(instance, str(Password(pswd = value)))
