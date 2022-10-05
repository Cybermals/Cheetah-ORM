"""Cheetah ORM - Dummy Data Model"""


#Classes
#=======
class DataModel(object):
    """Base class for a dummy data model."""
    _cursor = None
    table = ""

    @classmethod
    def init_table(cls):
        """Initialize the table for this data model."""
        pass

    @classmethod
    def filter(cls, order_by = None, **kwargs):
        """Fetch all models that fit the given criteria."""
        pass

    @classmethod
    def _get_fields(cls):
        """Return a list of (name, field) pairs for each field in this data model."""
        return []

    def __init__(self, id = None, **kwargs):
        """Setup this data model."""
        pass

    def save(self):
        """Save changes to this data model to the database."""
        pass

    def discard(self):
        """Discard unsaved changes to the database."""
        pass
