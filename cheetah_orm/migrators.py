"""Cheetah ORM - Migrator Classes

Migrators are used to keep the structure of tables in a database synced with their corresponding data models.
"""

import json

from .constants import *
from .error import InvalidTypeError
from .fields import StringField
from .indexes import UniqueIndex
from .model import DataModel


# Data Models
# ===========
class MigrationMetadata(DataModel):
    table    = "migration_metadata"
    name     = StringField(length=256, not_null=True)
    fields   = StringField(length=65535, not_null=True)
    indexes  = StringField(length=65535, not_null=True)
    name_idx = UniqueIndex("name")


# Classes
# =======
class Migrator(object):
    """Base class for a migrator."""
    def __init__(self, mapper):
        """Setup this migrator."""
        self._mapper = mapper
        mapper.init_model(MigrationMetadata)

    def migrate(self, model):
        """Migrate a data model if necessary."""
        pass


class SQLiteMigrator(Migrator):
    """An SQLite migrator."""
    def migrate(self, model):
        """Migrate a data model if necessary."""
        # Does migration metadata for the given data model exist?
        records = self._mapper.filter(MigrationMetadata, "name=?", model.table)

        if len(records):
            # Fetch migration metadata and import it
            metadata = records[0]
            fields = json.loads(metadata.fields)
            indexes = json.loads(metadata.indexes)

            # Has the data model changed?
            if fields != model._fields or indexes != model._indexes:
                # Rename the old table
                self._mapper._cur.execute(f"ALTER TABLE `{model.table}` RENAME TO `tmp_{model.table}`;")

                # Initialize new data model
                self._mapper.init_model(model)

                # Generate migration SQL
                field_names1 = [f"`{field[0]}`" for field in fields]
                field_names2 = [f"`{field[0]}`" for field in model._fields]
                fields = list(set(field_names1).intersection(field_names2))
                field_sql = ",".join(fields)
                sql = f"INSERT INTO `{model.table}`({field_sql}) SELECT {field_sql} FROM `tmp_{model.table}`;"

                # Migrate data
                self._mapper._cur.execute(sql)
                self._mapper.commit()

                # Drop old table
                self._mapper._cur.execute(f"DROP TABLE `tmp_{model.table}`;")

                # Update migration metadata
                metadata.fields = json.dumps(model._fields)
                metadata.indexes = json.dumps(model._indexes)
                self._mapper.save_model(metadata)
                self._mapper.commit()

        else:
            # Create migration metadata
            metadata = MigrationMetadata(
                name=model.table,
                fields=json.dumps(model._fields),
                indexes=json.dumps(model._indexes)
            )
            self._mapper.save_model(metadata)
            self._mapper.commit()


class MySQLMigrator(Migrator):
    """A MySQL migrator."""
    def migrate(self, model):
        """Migrate a data model if necessary."""
        # Does migration metadata for the given data model exist?
        records = self._mapper.filter(MigrationMetadata, "name=?", model.table)

        if len(records):
            # Fetch migration metadata and import it
            metadata = records[0]
            fields = json.loads(metadata.fields)
            indexes = json.loads(metadata.indexes)

            # Convert field metadata to dictionaries
            fields1 = {field[0]: field[1:] for field in fields}
            fields2 = {field[0]: field[1:] for field in model._fields}

            # Check fields for changes
            for name, (type, length, default) in fields1.items():
                # Was this field removed?
                if name not in fields2:
                    self._mapper._cur.execute(f"ALTER TABLE `{model.table}` DROP COLUMN `{name}`;")

            for name, (type, length, default) in fields2.items():
                # Was this field added?
                if name not in fields1:
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

                    # Add the new column
                    self._mapper._cur.execute(f"ALTER TABLE `{model.table}` ADD COLUMN {col};")

                # Check if the field was modified
                elif fields1[name] != [type, length, default]:
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

                    # Modify the column
                    self._mapper._cur.execute(f"ALTER TABLE `{model.table}` MODIFY COLUMN {col};")
                

            # Update migration metadata
            metadata.fields = json.dumps(model._fields)
            metadata.indexes = json.dumps(model._indexes)
            self._mapper.save_model(metadata)
            self._mapper.commit()

        else:
            # Create migration metadata
            metadata = MigrationMetadata(
                name=model.table,
                fields=json.dumps(model._fields),
                indexes=json.dumps(model._indexes)
            )
            self._mapper.save_model(metadata)
            self._mapper.commit()


class PostgreSQLMigrator(Migrator):
    """A PostgreSQL migrator."""
    def migrate(self, model):
        """Migrate a data model if necessary."""
        # Does migration metadata for the given data model exist?
        records = self._mapper.filter(MigrationMetadata, "name=?", model.table)

        if len(records):
            # Fetch migration metadata and import it
            metadata = records[0]
            fields = json.loads(metadata.fields)
            indexes = json.loads(metadata.indexes)

            # Convert field metadata to dictionaries
            fields1 = {field[0]: field[1:] for field in fields}
            fields2 = {field[0]: field[1:] for field in model._fields}

            # Check fields for changes
            for name, (type, length, default) in fields1.items():
                # Was this field removed?
                if name not in fields2:
                    self._mapper._cur.execute(f'ALTER TABLE "{model.table}" DROP COLUMN "{name}";')

            for name, (type, length, default) in fields2.items():
                # Was this field added?
                if name not in fields1:
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

                    # Add the new column
                    self._mapper._cur.execute(f'ALTER TABLE "{model.table}" ADD COLUMN {col};')

                # Check if the field was modified
                elif fields1[name] != [type, length, default]:
                    # Generate column name
                    col = ""

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

                    # Modify the column type
                    self._mapper._cur.execute(f'ALTER TABLE "{model.table}" ALTER COLUMN "{name}" TYPE {col};')

                    # Not null?
                    if type & FIELD_TYPE_NOT_NULL:
                        self._mapper._cur.execute(f'ALTER TABLE "{model.table}" ALTER COLUMN "{name}" SET NOT NULL;')

                    else:
                        self._mapper._cur.execute(f'ALTER TABLE "{model.table}" ALTER COLUMN "{name}" DROP NOT NULL;')

                    # Add default value?
                    if default is not None:
                        self._mapper._cur.execute(f'ALTER TABLE "{model.table}" ALTER COLUMN "{name}" SET DEFAULT {default};')

                    else:
                        self._mapper._cur.execute(f'ALTER TABLE "{model.table}" ALTER COLUMN "{name}" SET DEFAULT NULL;')
                

            # Update migration metadata
            metadata.fields = json.dumps(model._fields)
            metadata.indexes = json.dumps(model._indexes)
            self._mapper.save_model(metadata)
            self._mapper.commit()

        else:
            # Create migration metadata
            metadata = MigrationMetadata(
                name=model.table,
                fields=json.dumps(model._fields),
                indexes=json.dumps(model._indexes)
            )
            self._mapper.save_model(metadata)
            self._mapper.commit()
