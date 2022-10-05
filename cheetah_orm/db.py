"""Cheetah ORM - Database Driver"""

from . import dummy_fields as fields
from .dummy_model import DataModel
from .exceptions import UnknownDBDriver


#Globals
#=======
_db = None


#Functions
#=========
def connect(driver = "sqlite3", **kwargs):
    """Connect to a database."""
    global _db, fields, DataModel

    #SQLite?
    if driver == "sqlite3":
        #Establish database connection
        import sqlite3
        _db = sqlite3.connect(**kwargs)
        _db.cursor().execute("PRAGMA foreign_keys = ON;")

        #Import SQLite data model and field classes
        from . import sqlite3_fields as fields
        from .sqlite3_model import DataModel

    #MySQL/MariaDB?
    elif driver in ["mysql", "mariadb"]:
        #Establish database connection
        import mysql.connector
        _db = mysql.connector.connect(**kwargs)

        #Import MySQL field classes
        from . import mysql_fields as fields
        from .mysql_model import DataModel

    #PostgreSQL?
    elif driver == "postgresql":
        #Establish database connection
        import psycopg
        _db = psycopg.connect(**kwargs)

        #Import PostgreSQL field classes
        from . import postgresql_fields as fields
        from .postgresql_model import DataModel

    #Unknown?
    else:
        raise UnknownDBDriver(driver)

    #Pass cursor to fields module and model class
    fields.Field._cursor = _db.cursor()
    DataModel._cursor = fields.Field._cursor
