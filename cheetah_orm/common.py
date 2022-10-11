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
        self._foreign_key = None
        self._get = None
        self._set = None

    def __set_name__(self, owner, name):
        """Store field name."""
        self._name = name
        self._full_name = f"{owner.table}({name})"

    def __get__(self, instance, owner = None):
        """Get the value of this field."""
        #Does the record for the data model exist in the database?
        if instance.id is not None:
            self._cursor.execute(self._get, (instance.id,))
            return self._cursor.fetchone()[0]

        return (instance._cache[self._name] if self._name in instance._cache else self._default)

    def __set__(self, instance, value):
        """Set the value of this field."""
        #Does the record for the data model exist in the database?
        if instance.id is not None:
            self._cursor.execute(self._set, (value, instance.id))

        else:
            instance._cache[self._name] = value

    def _pop_cache(self, instance):
        """Pop the cached value for this field."""
        #Is there a cached value?
        if self._name in instance._cache:
            value = instance._cache[self._name]
            del instance._cache[self._name]
            return value

        #Return default value
        return self._default


class BackReference(object):
    """A reference to a collection of data models that refer to a given data model."""
    def __init__(self, foreign_model, foreign_key):
        """Setup this back refernce."""
        self._foreign_model = foreign_model
        self._foreign_key = foreign_key

    def __get__(self, instance, owner = None):
        """Return all data models of the foreign model's type that have a foeign key which refers
        to the given model instance.
        """
        kwargs = {self._foreign_key + "_eq": instance.id}
        return self._foreign_model.filter(**kwargs)
