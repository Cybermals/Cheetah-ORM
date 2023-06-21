"""Cheetah ORM - SQLite Migrator Unit Tests"""

import unittest

from cheetah_orm.fields import FloatField, IntField, StringField
from cheetah_orm.indexes import UniqueIndex
from cheetah_orm.mappers import SQLiteMapper
from cheetah_orm.migrators import SQLiteMigrator
from cheetah_orm.model import DataModel


# Classes
# =======
class PlayerStats(DataModel):
    table     = "player_stats"
    name      = StringField(length=32, not_null=True)
    highscore = IntField(not_null=True)
    name_idx  = UniqueIndex("name")


class TestSQLiteMigrator(unittest.TestCase):
    """SQLite migrator tests."""
    @classmethod
    def setUpClass(cls):
        """Setup test suite."""
        # Establish a database connection
        cls.mapper = SQLiteMapper()
        cls.mapper.connect(database="test.db")

        # Cleanup last test
        cls.mapper._cur.execute("DROP TABLE IF EXISTS `player_stats`;")
        cls.mapper._cur.execute("DROP TABLE IF EXISTS `migration_metadata`;")

        # Initialize data models
        cls.mapper.init_model(PlayerStats)

        # Initialize migrator
        cls.migrator = SQLiteMigrator(cls.mapper)

    @classmethod
    def tearDownClass(cls):
        """Cleanup test suite."""
        # Disconnect from the database
        cls.mapper.disconnect()

    def test_1_init_metadata(self):
        """Test migration metadata initialization."""
        # Init data model migration metadata
        self.migrator.migrate(PlayerStats)

        # Add some player stats
        dylan = PlayerStats(
            name="Dylan",
            highscore=100
        )
        emmi = PlayerStats(
            name="Emmi",
            highscore=100
        )

        self.mapper.save_model(dylan)
        self.mapper.save_model(emmi)

    def test_2_add_field(self):
        """Test field adding."""
        # Redefine the player stats data model
        class PlayerStats(DataModel):
            table     = "player_stats"
            name      = StringField(length=32, not_null=True)
            highscore = IntField(not_null=True)
            best_time = IntField(default=0, not_null=True)
            name_idx  = UniqueIndex("name")

        # Apply migrations
        self.migrator.migrate(PlayerStats)

    def test_3_change_field_type(self):
        """Test field type changing."""
        # Redefine the player stats data model
        class PlayerStats(DataModel):
            table     = "player_stats"
            name      = StringField(length=32, not_null=True)
            highscore = IntField(not_null=True)
            best_time = FloatField(default=0, not_null=True)
            name_idx  = UniqueIndex("name")

        # Apply migrations
        self.migrator.migrate(PlayerStats)

    def test_4_remove_field(self):
        """Test field removal."""
        # Apply migrations (this will revert back to the original data model we defined globally)
        self.migrator.migrate(PlayerStats)
