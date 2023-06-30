"""Cheetah ORM - Mapper Classes"""

from .constants import *
from .error import InvalidParamsError, InvalidTypeError


# Classes
# =======
class Mapper(object):
    """Base class for a data model mapper."""
    def __init__(self):
        """Setup this mapper."""
        self._db = None
        self._cur = None
        self._cache = {}

    def _gen_sql_stmts(self, model):
        """Generate SQL statements for a data model.
        
        This should be overridden by a derived class.
        """
        pass

    def connect(self, **kwargs):
        """Connect to a database.

        This should be overridden by a derived class.
        """
        pass

    def disconnect(self):
        """Disconnect from a database.
        
        This should be overridden by a derived class.
        """
        pass

    def commit(self):
        """Commit changes to a database.
        
        This should be overridden by a derived class.
        """
        pass

    def rollback(self):
        """Rollback changes to a database.
        
        This should be overridden by a derived class.
        """
        pass

    def init_model(self, model):
        """Initialize the table for a data model.
        
        This should be overridden by a derived class.
        """
        pass

    def save_model(self, model):
        """Save a data model to the database.
        
        This should be overridden by a derived class.
        """
        pass

    def delete_model(self, model):
        """Delete a data model in the database.
        
        This should be overridden by a derived class.
        """
        pass

    def filter(self, model, condition="", *args, **kwargs):
        """Filter data in a database.
        
        This should be overridden by a derived class.
        """
        pass


class SQLiteMapper(Mapper):
    """A data model mapper for SQLite databases."""
    def _gen_sql_stmts(self, model):
        """Generate SQL statements for the given model."""
        cache_entry = {}

        # Generate insert statement
        cols = ",".join([f"`{col[0]}`" for col in model._fields])
        placeholders = ",".join(["?" for col in model._fields])
        cache_entry["insert"] = f"INSERT INTO `{model.table}`({cols}) VALUES ({placeholders});"

        # Generate update statement
        cols = ",".join([f"`{col[0]}`=?" for col in model._fields])
        cache_entry["update"] = f"UPDATE `{model.table}` SET {cols} WHERE `id`=?;"

        # Generate delete statement
        cache_entry["delete"] = f"DELETE FROM `{model.table}` WHERE `id`=?;"

        # Generate select statement
        cols = ",".join([f"`{col[0]}`" for col in model._fields])
        cache_entry["select"] = f"SELECT `id`,{cols} FROM `{model.table}`"

        # Generate count statement
        cache_entry["count"] = f"SELECT COUNT(`id`) FROM `{model.table}`"

        # Add cache entry
        self._cache[model] = cache_entry

    def connect(self, database):
        """Connect to an SQLite database."""
        # Connect to the database and get a cursor object
        import sqlite3

        self._db  = sqlite3.connect(database)
        self._db.row_factory = sqlite3.Row
        self._cur = self._db.cursor()

        # Enable foreign key checks
        self._cur.execute("PRAGMA foreign_keys=ON;")

    def disconnect(self):
        """Disconnect from an SQLite database."""
        self._cur.close()
        self._db.close()
        self._cur = None
        self._db  = None

    def commit(self):
        """Commit changes to the database."""
        self._db.commit()

    def rollback(self):
        """Rollback changes to the database."""
        self._db.rollback()

    def init_model(self, model):
        """Initialize the table for a data model."""
        # Build field SQL
        field_sql = "`id` INTEGER PRIMARY KEY,"

        for name, type, length, default in model._fields:
            # Generate column name
            col = f"`{name}` "

            # Unsigned?
            if type & FIELD_TYPE_UNSIGNED:
                col += "UNSIGNED "

            # Add column type
            if type & FIELD_TYPE_INT:
                col += "INT"

            elif type & FIELD_TYPE_BIGINT:
                col += "BIGINT"

            elif type & FIELD_TYPE_FLOAT:
                col += "FLOAT"

            elif type & FIELD_TYPE_DOUBLE:
                col += "FLOAT"

            elif type & FIELD_TYPE_STRING:
                col += "VARCHAR"

            elif type & FIELD_TYPE_BLOB:
                col += "BLOB"

            elif type & FIELD_TYPE_DATETIME:
                col += "DATETIME"

            elif type & FIELD_TYPE_PSWD:
                col += "BLOB"

            else:
                raise InvalidTypeError(f"Field type {type} is not a valid type.")

            # Add length
            if length:
                col += f"({length})"

            # Not null?
            if type & FIELD_TYPE_NOT_NULL:
                col += f" NOT NULL"

            # Add default value
            if default is not None:
                # Handle now()
                if default == "now()":
                    default = "'now()'"

                col += f" DEFAULT {default}"

            field_sql += f"{col},"

        if field_sql[-1] == ",":
            field_sql = field_sql[:-1]

        # Build index SQL
        index_sql = ""
        indexes = []

        for index in model._indexes:
            # Generate index name
            idx = f"CONSTRAINT `{model.table}_{index[0]}` "

            # Add index type
            if index[1] & INDEX_TYPE_KEY:
                # Normal indexes must be created with "CREATE INDEX" in SQLite
                indexes.append(index)
                continue

            elif index[1] & INDEX_TYPE_UNIQUE_KEY:
                fields = ",".join([f"`{field}`" for field in index[2]])
                idx += f"UNIQUE({fields})"

            elif index[1] & INDEX_TYPE_FOREIGN_KEY:
                idx += f"FOREIGN KEY(`{index[0][:-4]}`) REFERENCES `{index[2][0]}`(`{index[2][1]}`)"

                # On delete clause
                idx += " ON DELETE "

                if index[3][0] & FK_SET_NULL:
                    idx += "SET NULL"

                elif index[3][0] & FK_SET_DEFAULT:
                    idx += "SET DEFAULT"

                elif index[3][0] & FK_CASCADE:
                    idx += "CASCADE"

                elif index[3][0] & FK_RESTRICT:
                    idx += "RESTRICT"

                elif index[3][0] & FK_NO_ACTION:
                    idx += "NO ACTION"

                # On update clause
                idx += " ON UPDATE "

                if index[3][1] & FK_SET_NULL:
                    idx += "SET NULL"

                elif index[3][1] & FK_SET_DEFAULT:
                    idx += "SET DEFAULT"

                elif index[3][1] & FK_CASCADE:
                    idx += "CASCADE"

                elif index[3][1] & FK_RESTRICT:
                    idx += "RESTRICT"

                elif index[3][1] & FK_NO_ACTION:
                    idx += "NO ACTION"

            else:
                raise InvalidTypeError(f"Index type {index[1]} is not a valid type.")

            index_sql += f"{idx},"

        if index_sql[-1] == ",":
            index_sql = index_sql[:-1]

        # Build table SQL
        sql = f"CREATE TABLE IF NOT EXISTS `{model.table}`({field_sql},{index_sql});"

        # Create the table
        # print(sql)
        self._cur.execute(sql)

        # Create normal indexes
        for index in indexes:
            fields = ",".join([field for field in index[2]])
            sql = f"CREATE INDEX IF NOT EXISTS `{model.table}_{index[0]}` ON `{model.table}`({fields});"
            self._cur.execute(sql)

        # Generate SQL statements for the given model
        self._gen_sql_stmts(model)

    def save_model(self, model):
        """Save the given model to the database.
        
        This method will choose to do an insert if the model has not been previously saved. Otherwise it 
        will perform and update to the existing row in the corresponding database table.
        """
        # Has the model been saved previously?
        if "id" in model._data:
            # Update existing row in the database
            values = [value for key, value in model._data.items() if key != "id"]
            values.append(model._data["id"])
            self._cur.execute(self._cache[model.__class__]["update"], values)

        else:
            # Insert the data model into the table and fetch its ID
            values = list(model._data.values())
            self._cur.execute(self._cache[model.__class__]["insert"], values)
            model._data["id"] = self._cur.lastrowid

    def delete_model(self, model):
        """Delete the given model from the database."""
        self._cur.execute(self._cache[model.__class__]["delete"], (model.id,))

    def filter(self, model, condition="", *args, **kwargs):
        """Filter data in the database."""
        sql = self._cache[model]["select"]

        # Is there a condition?
        if condition != "":
            sql += f" WHERE {condition}"

        # Are there columns to order by?
        if "order_by" in kwargs:
            direction = kwargs.get("order", "ASC")
            cols = ",".join([f"`{col}`" for col in kwargs["order_by"]])
            sql += f" ORDER BY {cols} {direction}"

        # Is there a limit?
        if "limit" in kwargs:
            sql += f" LIMIT {kwargs['limit']}"

            # Is there an offset?
            if "offset" in kwargs:
                sql += f" OFFSET {kwargs['offset']}"

        sql += ";"

        # Execute query and fetch results
        self._cur.execute(sql, args)
        results = [model(**dict(row)) for row in self._cur.fetchall()]
        return results
    
    def count(self, model, condition="", *args, **kwargs):
        """Count data in the database."""
        sql = self._cache[model]["count"]

        # Is there a condition?
        if condition != "":
            sql += f" WHERE {condition}"

        sql += ";"

        # Execute query and fetch results
        self._cur.execute(sql, args)
        return self._cur.fetchall()[0][0]
    

class MySQLMapper(Mapper):
    """A data model mapper for MySQL/MariaDB databases."""
    def _gen_sql_stmts(self, model):
        """Generate SQL statements for the given model."""
        cache_entry = {}

        # Generate insert statement
        cols = ",".join([f"`{col[0]}`" for col in model._fields])
        placeholders = ",".join(["%s" for col in model._fields])
        cache_entry["insert"] = f"INSERT INTO `{model.table}`({cols}) VALUES ({placeholders});"

        # Generate update statement
        cols = ",".join([f"`{col[0]}`=%s" for col in model._fields])
        cache_entry["update"] = f"UPDATE `{model.table}` SET {cols} WHERE `id`=%s;"

        # Generate delete statement
        cache_entry["delete"] = f"DELETE FROM `{model.table}` WHERE `id`=%s;"

        # Generate select statement
        cols = ",".join([f"`{col[0]}`" for col in model._fields])
        cache_entry["select"] = f"SELECT `id`,{cols} FROM `{model.table}`"

        # Generate count statement
        cache_entry["count"] = f"SELECT COUNT(`id`) FROM `{model.table}`"

        # Add cache entry
        self._cache[model] = cache_entry

    def connect(self, host, user, passwd, database):
        """Connect to a MySQL/MariaDB database."""
        # Connect to the database and get a cursor object
        import pymysql
        from pymysql.cursors import DictCursor

        self._db  = pymysql.connect(host=host, user=user, passwd=passwd, database=database)
        self._cur = self._db.cursor(DictCursor)

    def disconnect(self):
        """Disconnect from a MySQL/MariaDB database."""
        self._cur.close()
        self._db.close()
        self._cur = None
        self._db  = None

    def commit(self):
        """Commit changes to the database."""
        self._db.commit()

    def rollback(self):
        """Rollback changes to the database."""
        self._db.rollback()

    def init_model(self, model):
        """Initialize the table for a data model."""
        # Build field SQL
        field_sql = "`id` BIGINT PRIMARY KEY AUTO_INCREMENT,"

        for name, type, length, default in model._fields:
            # Generate column name
            col = f"`{name}` "

            # Unsigned?
            if type & FIELD_TYPE_UNSIGNED:
                col += "UNSIGNED "

            # Add column type
            if type & FIELD_TYPE_INT:
                col += "INT"

            elif type & FIELD_TYPE_BIGINT:
                col += "BIGINT"

            elif type & FIELD_TYPE_FLOAT:
                col += "FLOAT"

            elif type & FIELD_TYPE_DOUBLE:
                col += "FLOAT"

            elif type & FIELD_TYPE_STRING:
                col += "TEXT"

            elif type & FIELD_TYPE_BLOB:
                col += "BLOB"

            elif type & FIELD_TYPE_DATETIME:
                col += "DATETIME"

            elif type & FIELD_TYPE_PSWD:
                col += "BLOB"

            else:
                raise InvalidTypeError(f"Field type {type} is not a valid type.")

            # Add length
            if length:
                col += f"({length})"

            # Not null?
            if type & FIELD_TYPE_NOT_NULL:
                col += f" NOT NULL"

            # Add default value
            if default is not None:
                col += f" DEFAULT {default}"

            field_sql += f"{col},"

        if field_sql[-1] == ",":
            field_sql = field_sql[:-1]

        # Build index SQL
        index_sql = ""
        indexes = []

        for index in model._indexes:
            # Generate index name
            idx = f"CONSTRAINT `{model.table}_{index[0]}` "

            # Add index type
            if index[1] & INDEX_TYPE_KEY:
                # Normal indexes must be created with "CREATE INDEX" in MySQL/MariaDB
                indexes.append(index)
                continue

            elif index[1] & INDEX_TYPE_UNIQUE_KEY:
                fields = ",".join([f"`{field}`" for field in index[2]])
                idx += f"UNIQUE({fields})"

            elif index[1] & INDEX_TYPE_FOREIGN_KEY:
                idx += f"FOREIGN KEY(`{index[0][:-4]}`) REFERENCES `{index[2][0]}`(`{index[2][1]}`)"

                # On delete clause
                idx += " ON DELETE "

                if index[3][0] & FK_SET_NULL:
                    idx += "SET NULL"

                elif index[3][0] & FK_SET_DEFAULT:
                    idx += "SET DEFAULT"

                elif index[3][0] & FK_CASCADE:
                    idx += "CASCADE"

                elif index[3][0] & FK_RESTRICT:
                    idx += "RESTRICT"

                elif index[3][0] & FK_NO_ACTION:
                    idx += "NO ACTION"

                # On update clause
                idx += " ON UPDATE "

                if index[3][1] & FK_SET_NULL:
                    idx += "SET NULL"

                elif index[3][1] & FK_SET_DEFAULT:
                    idx += "SET DEFAULT"

                elif index[3][1] & FK_CASCADE:
                    idx += "CASCADE"

                elif index[3][1] & FK_RESTRICT:
                    idx += "RESTRICT"

                elif index[3][1] & FK_NO_ACTION:
                    idx += "NO ACTION"

            else:
                raise InvalidTypeError(f"Index type {index[1]} is not a valid type.")

            index_sql += f"{idx},"

        if index_sql[-1] == ",":
            index_sql = index_sql[:-1]

        # Build table SQL
        sql = f"CREATE TABLE IF NOT EXISTS `{model.table}`({field_sql},{index_sql});"

        # Create the table
        # print(sql)
        self._cur.execute(sql)

        # Create normal indexes
        for index in indexes:
            fields = ",".join([f"`{field}`" for field in index[2]])
            sql = f"CREATE INDEX IF NOT EXISTS `{model.table}_{index[0]}` ON `{model.table}`({fields});"
            self._cur.execute(sql)

        # Generate SQL statements for the given model
        self._gen_sql_stmts(model)

    def save_model(self, model):
        """Save the given model to the database.
        
        This method will choose to do an insert if the model has not been previously saved. Otherwise it 
        will perform and update to the existing row in the corresponding database table.
        """
        # Has the model been saved previously?
        if "id" in model._data:
            # Update existing row in the database
            values = [value for key, value in model._data.items() if key != "id"]
            values.append(model._data["id"])
            self._cur.execute(self._cache[model.__class__]["update"], values)

        else:
            # Insert the data model into the table and fetch its ID
            values = list(model._data.values())
            self._cur.execute(self._cache[model.__class__]["insert"], values)
            model._data["id"] = self._cur.lastrowid

    def delete_model(self, model):
        """Delete the given model from the database."""
        self._cur.execute(self._cache[model.__class__]["delete"], (model.id,))

    def filter(self, model, condition="", *args, **kwargs):
        """Filter data in the database."""
        sql = self._cache[model]["select"]

        # Replace "?" placeholders with "%s" placeholders in the condition format string
        condition = condition.replace("?", "%s")

        # Is there a condition?
        if condition != "":
            sql += f" WHERE {condition}"

        # Are there columns to order by?
        if "order_by" in kwargs:
            direction = kwargs.get("order", "ASC")
            cols = ",".join([f"`{col}`" for col in kwargs["order_by"]])
            sql += f" ORDER BY {cols} {direction}"

        # Is there a limit?
        if "limit" in kwargs:
            sql += f" LIMIT {kwargs['limit']}"

            # Is there an offset?
            if "offset" in kwargs:
                sql += f" OFFSET {kwargs['offset']}"

        sql += ";"

        # Execute query and fetch results
        self._cur.execute(sql, args)
        results = [model(**dict(row)) for row in self._cur.fetchall()]
        return results
    
    def count(self, model, condition="", *args, **kwargs):
        """Count data in the database."""
        sql = self._cache[model]["count"]

        # Replace "?" placeholders with "%s" placeholders in the condition format string
        condition = condition.replace("?", "%s")

        # Is there a condition?
        if condition != "":
            sql += f" WHERE {condition}"

        sql += ";"

        # Execute query and fetch results
        self._cur.execute(sql, args)
        return self._cur.fetchall()[0]["COUNT(`id`)"]
    

MariaDBMapper = MySQLMapper


class PostgreSQLMapper(Mapper):
    """A data model mapper for PostgreSQL databases."""
    def _gen_sql_stmts(self, model):
        """Generate SQL statements for the given model."""
        cache_entry = {}

        # Generate insert statement
        cols = ",".join([f'"{col[0]}"' for col in model._fields])
        placeholders = ",".join(["%s" for col in model._fields])
        cache_entry["insert"] = f'INSERT INTO "{model.table}"({cols}) VALUES ({placeholders}) RETURNING "id";'

        # Generate update statement
        cols = ",".join([f'"{col[0]}"=%s' for col in model._fields])
        cache_entry["update"] = f'UPDATE "{model.table}" SET {cols} WHERE "id"=%s;'

        # Generate delete statement
        cache_entry["delete"] = f'DELETE FROM "{model.table}" WHERE "id"=%s;'

        # Generate select statement
        cols = ",".join([f'"{col[0]}"' for col in model._fields])
        cache_entry["select"] = f'SELECT "id",{cols} FROM "{model.table}"'

        # Generate count statement
        cache_entry["count"] = f'SELECT COUNT("id") FROM "{model.table}"'

        # Add cache entry
        self._cache[model] = cache_entry

    def connect(self, host, user, password, dbname):
        """Connect to a PostgreSQL database."""
        # Connect to the database and get a cursor object
        import psycopg
        from psycopg.rows import dict_row

        self._db  = psycopg.connect(host=host, user=user, password=password, dbname=dbname)
        self._db.row_factory = dict_row
        self._cur = self._db.cursor()

    def disconnect(self):
        """Disconnect from a PostgreSQL database."""
        self._cur.close()
        self._db.close()
        self._cur = None
        self._db  = None

    def commit(self):
        """Commit changes to the database."""
        self._db.commit()

    def rollback(self):
        """Rollback changes to the database."""
        self._db.rollback()

    def init_model(self, model):
        """Initialize the table for a data model."""
        # Build field SQL
        field_sql = '"id" BIGSERIAL PRIMARY KEY,'

        for name, type, length, default in model._fields:
            # Generate column name
            col = f'"{name}" '

            # Unsigned?
            if type & FIELD_TYPE_UNSIGNED:
                col += "UNSIGNED "

            # Add column type
            if type & FIELD_TYPE_INT:
                col += "INT"

            elif type & FIELD_TYPE_BIGINT:
                col += "BIGINT"

            elif type & FIELD_TYPE_FLOAT:
                col += "FLOAT"

            elif type & FIELD_TYPE_DOUBLE:
                col += "FLOAT"

            elif type & FIELD_TYPE_STRING:
                col += "VARCHAR"

            elif type & FIELD_TYPE_BLOB:
                col += "BYTEA"

            elif type & FIELD_TYPE_DATETIME:
                col += "TIMESTAMP"

            elif type & FIELD_TYPE_PSWD:
                col += "BYTEA"

            else:
                raise InvalidTypeError(f"Field type {type} is not a valid type.")

            # Add length
            if length and not (type & FIELD_TYPE_INT or type & FIELD_TYPE_BIGINT or type & FIELD_TYPE_BLOB or type & FIELD_TYPE_PSWD):
                col += f"({length})"

            # Not null?
            if type & FIELD_TYPE_NOT_NULL:
                col += f" NOT NULL"

            # Add default value
            if default is not None:
                col += f" DEFAULT {default}"

            field_sql += f"{col},"

        if field_sql[-1] == ",":
            field_sql = field_sql[:-1]

        # Build index SQL
        index_sql = ""
        indexes = []

        for index in model._indexes:
            # Generate index name
            idx = f'CONSTRAINT "{model.table}_{index[0]}" '

            # Add index type
            if index[1] & INDEX_TYPE_KEY:
                # Normal indexes must be created with "CREATE INDEX" in PostgreSQL
                indexes.append(index)
                continue

            elif index[1] & INDEX_TYPE_UNIQUE_KEY:
                fields = ",".join([f'"{field}"' for field in index[2]])
                idx += f"UNIQUE({fields})"

            elif index[1] & INDEX_TYPE_FOREIGN_KEY:
                idx += f'FOREIGN KEY("{index[0][:-4]}") REFERENCES "{index[2][0]}"("{index[2][1]}")'

                # On delete clause
                idx += " ON DELETE "

                if index[3][0] & FK_SET_NULL:
                    idx += "SET NULL"

                elif index[3][0] & FK_SET_DEFAULT:
                    idx += "SET DEFAULT"

                elif index[3][0] & FK_CASCADE:
                    idx += "CASCADE"

                elif index[3][0] & FK_RESTRICT:
                    idx += "RESTRICT"

                elif index[3][0] & FK_NO_ACTION:
                    idx += "NO ACTION"

                # On update clause
                idx += " ON UPDATE "

                if index[3][1] & FK_SET_NULL:
                    idx += "SET NULL"

                elif index[3][1] & FK_SET_DEFAULT:
                    idx += "SET DEFAULT"

                elif index[3][1] & FK_CASCADE:
                    idx += "CASCADE"

                elif index[3][1] & FK_RESTRICT:
                    idx += "RESTRICT"

                elif index[3][1] & FK_NO_ACTION:
                    idx += "NO ACTION"

            else:
                raise InvalidTypeError(f"Index type {index[1]} is not a valid type.")

            index_sql += f"{idx},"

        if index_sql[-1] == ",":
            index_sql = index_sql[:-1]

        # Build table SQL
        sql = f'CREATE TABLE IF NOT EXISTS "{model.table}"({field_sql},{index_sql});'

        # Create the table
        # print(sql)
        self._cur.execute(sql)

        # Create normal indexes
        for index in indexes:
            fields = ",".join([f'"{field}"' for field in index[2]])
            sql = f'CREATE INDEX IF NOT EXISTS "{model.table}_{index[0]}" ON "{model.table}"({fields});'
            self._cur.execute(sql)

        # Generate SQL statements for the given model
        self._gen_sql_stmts(model)

    def save_model(self, model):
        """Save the given model to the database.
        
        This method will choose to do an insert if the model has not been previously saved. Otherwise it 
        will perform and update to the existing row in the corresponding database table.
        """
        # Has the model been saved previously?
        if "id" in model._data:
            # Update existing row in the database
            values = [value for key, value in model._data.items() if key != "id"]
            values.append(model._data["id"])
            self._cur.execute(self._cache[model.__class__]["update"], values)

        else:
            # Insert the data model into the table and fetch its ID
            values = list(model._data.values())
            self._cur.execute(self._cache[model.__class__]["insert"], values)
            model._data["id"] = self._cur.fetchall()[0]["id"]

    def delete_model(self, model):
        """Delete the given model from the database."""
        self._cur.execute(self._cache[model.__class__]["delete"], (model.id,))

    def filter(self, model, condition="", *args, **kwargs):
        """Filter data in the database."""
        sql = self._cache[model]["select"]

        # Replace "?" placeholders with "%s" placeholders and replace backticks with double quotes in the 
        # condition format string
        condition = condition.replace("?", "%s").replace("`", '"')

        # Is there a condition?
        if condition != "":
            sql += f" WHERE {condition}"

        # Are there columns to order by?
        if "order_by" in kwargs:
            direction = kwargs.get("order", "ASC")
            cols = ",".join([f'"{col}"' for col in kwargs["order_by"]])
            sql += f" ORDER BY {cols} {direction}"

        # Is there a limit?
        if "limit" in kwargs:
            sql += f" LIMIT {kwargs['limit']}"

            # Is there an offset?
            if "offset" in kwargs:
                sql += f" OFFSET {kwargs['offset']}"

        sql += ";"

        # Execute query and fetch results
        self._cur.execute(sql, args)
        results = [model(**dict(row)) for row in self._cur.fetchall()]
        return results
    
    def count(self, model, condition="", *args, **kwargs):
        """Count data in the database."""
        sql = self._cache[model]["count"]

        # Replace "?" placeholders with "%s" placeholders and replace backticks with double quotes in the 
        # condition format string
        condition = condition.replace("?", "%s").replace("`", '"')

        # Is there a condition?
        if condition != "":
            sql += f" WHERE {condition}"

        sql += ";"

        # Execute query and fetch results
        self._cur.execute(sql, args)
        return self._cur.fetchall()[0]["count"]
