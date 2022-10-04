"""Cheetah ORM - Common Fields"""

from passlib.context import CryptContext


#Globals
#=======
hasher = CryptContext(
    schemes = ["pbkdf2_sha256", "bcrypt", "argon2"],
    deprecated = "auto"
)


#Classes
#=======
class Password(object):
    """Password abstraction wrapper."""
    def __init__(self, **kwargs):
        """Setup this password."""
        #Raw password or hash?
        if "pswd" in kwargs:
            self._hash = hasher.hash(kwargs["pswd"])

        else:
            self._hash = kwargs["hash"]

    def __str__(self):
        """Return the password hash."""
        return self._hash

    def __eq__(self, n):
        """Compare this hashed password with a raw password."""
        return hasher.verify(n, self._hash)


class Field(object):
    """Base class for a field."""
    _cursor = None
    _type = None

    def __init__(self, **kwargs):
        """Setup this field."""
        self._default = (kwargs["default"] if "default" in kwargs else None)
        self._unique = (kwargs["unique"] if "unique" in kwargs else False)
        self._not_null = (kwargs["not_null"] if "not_null" in kwargs else False)
        self._key = (kwargs["key"] if "key" in kwargs else False)
        self._get = None
        self._set = None
        self._value = self._default

    def __set_name__(self, owner, name):
        """Generate get/set SQL for this field."""
        pass

    def __get__(self, instance, owner = None):
        """Get the value of this field."""
        #Does the record for the data model exist in the database?
        if instance.id is not None:
            return self._cursor.execute(self._get, (instance.id,)).fetchone()[0]

        return self._value

    def __set__(self, instance, value):
        """Set the value of this field."""
        #Does the record for the data model exist in the database?
        if instance.id is not None:
            self._cursor.execute(self._set, (value, instance.id))

        else:
            self._value = value

    def pop_cache(self):
        """Remove and return the cached value of this field."""
        value = self._value
        self._value = self._default
        return value