"""Cheetah ORM - Exceptions"""


#Classes
#=======
class ORMException(Exception):
    """Base class for an ORM exception."""
    def __init__(self, msg):
        """Setup this exception."""
        self.msg = msg

    def __str__(self):
        """Return the string representation of this exception."""
        return self.msg


class UnknownDBDriver(ORMException):
    def __init__(self, driver):
        """Setup this exception."""
        super().__init__(f"Unknown database driver '{driver}'.")
