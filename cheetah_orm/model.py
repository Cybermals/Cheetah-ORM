"""Cheetah ORM - Model Class

The data model class should be used as the base class for any data model. In order to properly map
a data model to a table, you should set the table attribute of each derived data model class to the 
name of the table the data model should be associated with. You also need to add one additional 
attribute for each field and index.


Example:

class User(DataModel):
    table    = "users"
    name     = StringField(length=32, not_null=True)
    pswd     = PasswordField(length=128, not_null=True)
    email    = StringField(length=128, not_null=True)
    question = StringField(length=128, not_null=True)
    answer   = StringField(length=128, not_null=True)
    name_idx = UniqueIndex("name")
    email    = UniqueIndex("email")
"""

from collections import OrderedDict


# Classes
# =======
class DataModel(object):
    """Base class for a data model."""
    table    = None
    _fields  = None
    _indexes = None

    def __init__(self, **kwargs):
        """Setup this data model."""
        self._data = OrderedDict()

        # Initialize default values
        for field in self._fields:
            setattr(self, field[0], field[3])

        # Pass keyword args to the corresponding fields
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        """Return the string representation of this data model."""
        return f"{self.__class__.__name__}({self._data})"
    
    def __repr__(self):
        """Return the string representation of this data model."""
        return str(self)

    def _get_id(self):
        """Get the ID of this data model."""
        return self._data["id"]
    
    def _set_id(self, value):
        """Set the ID of this data model."""
        self._data["id"] = value
    
    id = property(_get_id, _set_id)
