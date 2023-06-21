"""Cheetah ORM - Migrator Classes

Migrators are used to keep the structure of tables in a database synced with their corresponding data models.
"""

import json

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
