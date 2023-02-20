"""Cheetah ORM - MySQL/MariaDB Data Model"""

import inspect

from .exceptions import InvalidFilter
from .filters import _fields


# Classes
# =======
class DataModel(object):
    """Base class for a MySQL/MariaDB data model."""
    _cursor = None
    _insert_sql = None
    table = ""

    @classmethod
    def init_table(cls):
        """Initialize the table for this data model."""
        # Create migration metadata table if it doesn't exist
        cls._cursor.execute("CREATE TABLE IF NOT EXISTS migration_metadata(id INTEGER PRIMARY KEY AUTO_INCREMENT, type VARCHAR(16), name VARCHAR(32), `sql` VARCHAR(1024));")

        # Generate table SQL
        sql = f"CREATE TABLE IF NOT EXISTS {cls.table}(id INTEGER PRIMARY KEY AUTO_INCREMENT, "
        indexes = []
        fields = cls._get_fields()

        for name, field in fields:
            # Skip "__weakref__"
            if name == "__weakref__":
                continue

            # Add next field
            sql += f"{name} {field._type}"

            if field._default is not None:
                if field._type in ["TEXT", "BLOB", "DATETIME"] or field._type.startswith("VARCHAR"):
                    sql += f" DEFAULT '{field._default}'"

                else:
                    sql += f" DEFAULT {field._default}"

            elif field._unique:
                sql += " UNIQUE"

            if field._not_null:
                sql += " NOT NULL"

            # Create index?
            if field._key:
                indexes.append(name)

            # Create foreign key?
            if field._foreign_key is not None:
                sql += f" CONSTRAINT {cls.table}_{name} REFERENCES {field._foreign_key.table}(id) ON DELETE CASCADE"

            sql += ", "

        sql = sql[:-2] + ");"
        # print(sql)

        # Create table
        cls._cursor.execute(sql)

        # Check if this table needs to be migrated
        cls._cursor.execute("SELECT `sql` FROM migration_metadata WHERE type = 'TABLE' AND name = %s;", 
            (cls.table,))
        row = cls._cursor.fetchone()

        if row is not None and row[0] != sql:
            # Disable foreign keys
            cls._cursor.execute("SET foreign_key_checks = OFF;")

            # Check each column and modify the table structure as needed
            for name, field in fields:
                # Skip "__weakref__"
                if name == "__weakref__":
                    continue

                # Lookup column metadata in current table
                cls._cursor.execute(f"SHOW COLUMNS FROM {cls.table} WHERE Field = %s;", (name,))
                row = cls._cursor.fetchone()
                cls._cursor.fetchall()

                if row:
                    # Modify column type if needed
                    if not row[1].startswith(field._type):
                        cls._cursor.execute(f"ALTER TABLE {cls.table} MODIFY {name} {field._type};")

                else:
                    # Generate SQL to add new column
                    sql = f"ALTER TABLE {cls.table} ADD {name} {field._type}"

                    if field._default is not None:
                        if field._type in ["TEXT", "BLOB", "DATETIME"] or field._type.startswith("VARCHAR"):
                            sql += f" DEFAULT '{field._default}'"

                        else:
                            sql += f" DEFAULT {field._default}"

                    elif field._unique:
                        sql += " UNIQUE"

                    if field._not_null:
                        sql += " NOT NULL"

                    # Create foreign key?
                    if field._foreign_key is not None:
                        sql += f" CONSTRAINT {cls.table}_{name} REFERENCES {field._foreign_key.table}(id) ON DELETE CASCADE"

                    # Add new column
                    cls._cursor.execute(f"ALTER TABLE {cls.table} ADD {name} {field._type}")

            # Remove columns that aren't present in the new data model
            columns = [name for name, field in fields]
            cls._cursor.execute(f"SHOW COLUMNS FROM {cls.table};")

            for row in cls._cursor.fetchall():
                if row[0] != "id" and row[0] not in columns:
                    cls._cursor.execute(f"ALTER TABLE {cls.table} DROP {row[0]};")

            # Update table metadata
            cls._cursor.execute("UPDATE migration_metadata SET `sql` = %s WHERE name = %s AND type = 'TABLE';",
                (sql, cls.table))
            cls._cursor.execute("COMMIT;")

            # Enable foreign keys
            cls._cursor.execute("SET foreign_key_checks = ON;")

        elif row is None:
            # Add table metadata
            cls._cursor.execute("INSERT INTO migration_metadata(type, name, `sql`) VALUES (%s, %s, %s);", 
                ("TABLE", cls.table, sql))
            cls._cursor.execute("COMMIT;")

        # Create each index
        for index in indexes:
            sql = f"CREATE INDEX IF NOT EXISTS {cls.table}_{index} ON {cls.table}({index});"
            # print(sql)
            cls._cursor.execute(sql)

    @classmethod
    def create_index(cls, name, unique=False, *args):
        """Add an index to this data model."""
        indexes = ", ".join(args)

        if unique:
            sql = f"CREATE UNIQUE INDEX IF NOT EXISTS {cls.table}_{name} ON {cls.table}({indexes})"

        else:
            sql = f"CREATE INDEX IF NOT EXISTS {cls.table}_{name} ON {cls.table}({indexes})"

        cls._cursor.execute(sql)

    @classmethod
    def drop_table(cls):
        """Drop the table for this data model."""
        cls._cursor.execute(f"DROP TABLE {cls.table};")
        cls._cursor.execute(f"DELETE FROM migration_metadata WHERE name = %s AND type = 'TABLE';",
            (cls.table,))
        cls._cursor.execute("COMMIT;")

    @classmethod
    def filter(cls, order_by="id", descending=False, offset=0, limit=0, **kwargs):
        """Fetch all models which fit the given criteria."""
        # Generate filter SQL
        sql = f"SELECT id FROM {cls.table}"
        order = f" ORDER BY {order_by}" + (" DESC" if descending else "")
        limit = (f" LIMIT {limit} OFFSET {offset};" if limit > 0 else ";")

        if len(kwargs):
            # Build WHERE clause
            sql += " WHERE"
            first_field = True

            for name, value in kwargs.items():
                # And?
                if name.startswith("and_"):
                    sql += " AND"
                    name = name[4:]

                # Or?
                elif name.startswith("or_"):
                    sql += " OR"
                    name = name[3:]

                # First field?
                elif not first_field:
                    raise InvalidFilter("Every field after the first must have a boolean operator.")

                # Equal?
                if name.endswith("_eq"):
                    sql += f" {name[:-3]} = %s"

                # Not equal?
                elif name.endswith("_neq"):
                    sql += f" {name[:-4]} != %s"

                # Less than?
                elif name.endswith("_lt"):
                    sql += f" {name[:-3]} < %s"

                # Greater than?
                elif name.endswith("_gt"):
                    sql += f" {name[:-3]} > %s"

                # Less than or equal to?
                elif name.endswith("_lte"):
                    sql += f" {name[:-4]} <= %s"

                # Greater than or equal to?
                elif name.endswith("_gte"):
                    sql += f" {name[:-4]} >= %s"

                # No comparison operator?
                else:
                    raise InvalidFilter("Every field must have a comparision operator.")

                first_field = False

            # Return results
            sql += order + limit
            params = [(param.id if isinstance(param, DataModel) else param) for param in kwargs.values()]
            # print(sql)
            # print(f"Params: {params}")
            cls._cursor.execute(sql, params)
            return [cls(id=row[0]) for row in cls._cursor.fetchall()]

        # Return results
        sql += order + limit
        # print(sql)
        cls._cursor.execute(sql)
        return [cls(id=row[0]) for row in cls._cursor.fetchall()]

    @classmethod
    def _get_fields(cls):
        """Return a list of (name, field) pairs for each field in this data model."""
        return [item for item in inspect.getmembers(cls, _fields) if item[0] != "__weakref__"]

    def __init__(self, id=None, **kwargs):
        """Setup this data model."""
        self.id = id
        self._cache = {}

        # Initialize fields
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Generate insert row SQL?
        if self._insert_sql is None:
            head = f"INSERT INTO {self.table}("
            tail = ") VALUES ("

            for name, field in self._get_fields():
                # Skip "__weakref__"
                if name == "__weakref__":
                    continue

                # Add next field
                head += f"{name}, "
                tail += "%s, "

            self.__class__._insert_sql = head[:-2] + tail[:-2] + ");"

    def save(self, commit=True):
        """Save changes to this data model to the database."""
        # Does the record for this data model exist in the database?
        if self.id is None:
            # Insert the data model into its table and fetch its ID
            params = [value._pop_cache(self)
                      for name, value in self._get_fields()]
            # print(self._insert_sql)
            # print(f"Params: {params}")
            self._cursor.execute(self._insert_sql, params)
            self.id = self._cursor.lastrowid

        # Commit the transaction?
        if commit:
            self._cursor.execute("COMMIT;")

    def discard(self):
        """Discard unsaved changes to the database."""
        self._cursor.execute("ROLLBACK;")

    def delete(self, commit=True):
        """Delete this data model from the database."""
        sql = f"DELETE FROM {self.table} WHERE id = %s;"
        params = (self.id,)
        self._cursor.execute(sql, params)
        # print(sql)
        # print(f"Params: {params}")

        # Commit the transaction?
        if commit:
            self._cursor.execute("COMMIT;")
