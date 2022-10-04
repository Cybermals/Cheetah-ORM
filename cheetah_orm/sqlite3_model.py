"""Cheetah ORM - SQLite3 Data Model"""

import inspect

from .common import Field
from .filters import _fields


#Classes
#=======
class DataModel(object):
    """Base class for an SQLite3 data model."""
    _cursor = None
    _insert_sql = None
    table = ""

    @classmethod
    def init_table(cls):
        """Initialize the table for this data model."""
        #Generate create SQL
        sql = f"CREATE TABLE IF NOT EXISTS {cls.table}(id INTEGER PRIMARY KEY, "

        for name, field in cls._get_fields():
            #Skip __weakref__
            if name == "__weakref__":
                continue

            #Add next field
            sql += f"{name} {field._type}"

            if field._default is not None:
                sql += f" DEFAULT {field._default}"

            elif field._unique:
                sql += " UNIQUE"

            if field._not_null:
                sql += " NOT NULL"

            sql += ", "

        sql = sql[:-2] + ");"
        print(sql)

        #Create table
        cls._cursor.execute(sql)

    @classmethod
    def filter(cls, order_by = None, **kwargs):
        """Fetch all models which fit the given criteria."""
        #Generate filter SQL
        sql = f"SELECT id FROM {cls.table}"
        order = " ORDER BY id;"

        if order_by is not None:
            order = f" ORDER BY {order_by};"

        if len(kwargs):
            #Build WHERE clause
            sql += " WHERE"

            for name, value in kwargs.items():
                #Equal?
                if name.startswith("eq_"):
                    sql += f" {name[3:]} = ?"

                #Not equal?
                elif name.startswith("neq_"):
                    sql += f" {name[4:]} != ?"

                #Less than?
                elif name.startswith("lt_"):
                    sql += f" {name[3:]} < ?"

                #Greater than?
                elif name.startswith("gt_"):
                    sql += f" {name[3:]} > ?"

                #Less than or equal to?
                elif name.startswith("lte_"):
                    sql += f" {name[4:]} <= ?"

                #Greater than or equal to?
                elif name.startswith("gte_"):
                    sql += f" {name[4:]} >= ?"

            #Return results
            sql += order
            print(sql)
            return [cls(id = row[0]) for row in cls._cursor.execute(sql, tuple(kwargs.values()))]

        #Return results
        sql += order
        print(sql)
        return [cls(id = row[0]) for row in cls._cursor.execute(sql)]

    @classmethod
    def _get_fields(cls):
        """Return a list of (name, field) pairs for each field in this data model."""
        return [item for item in inspect.getmembers(cls, _fields) if item[0] != "__weakref__"]

    def __init__(self, id = None, **kwargs):
        """Setup this data model."""
        self.id = id
        self._cache = {}

        #Initialize fields
        for key, value in kwargs.items():
            setattr(self, key, value)

        #Build insert query string?
        if self._insert_sql is None:
            head = f"INSERT INTO {self.table}("
            tail = ") VALUES ("

            for name, field in self._get_fields():
                #Skip __weakref__
                if name == "__weakref__":
                    continue

                #Add next field
                head += f"{name}, "
                tail += "?, "

            self.__class__._insert_sql = head[:-2] + tail[:-2] + ");"
            print(self._insert_sql)

    def save(self):
        """Save changes to this data model to the database."""
        #Does the record for this data model exist in the database?
        if self.id is None:
            #Insert the data model into its table and fetch its ID
            self._cursor.execute(self._insert_sql, 
                [value._pop_cache(self) for name, value in self._get_fields()])
            self.id = self._cursor.execute("SELECT LAST_INSERT_ROWID();").fetchone()[0]

        #Commit the transaction
        self._cursor.execute("COMMIT;")

    def discard(self):
        """Discard unsaved changes to the database."""
        self._cursor.execute("ROLLBACK;")
