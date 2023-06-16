"""Cheetah ORM - Error Classes"""


# Classes
# =======
class ORMError(Exception):
    """Base class for an ORM error."""
    def __init__(self, msg):
        """Setup this error."""
        self._msg = msg

    def __str__(self):
        """Return the error message."""
        return self._msg
    

class InvalidParamsError(ORMError):
    """Invalid parameters error."""
    pass


class InvalidTypeError(ORMError):
    """Invalid column type."""
    pass
