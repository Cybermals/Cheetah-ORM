"""Cheetah ORM - SQLite Unit Tests"""

import unittest


# Classes
# =======
class TestSQLiteDBDriver(unittest.TestCase):
    """SQLite database driver tests."""
    @classmethod
    def setUpClass(cls):
        """Setup this test case."""
        # Delete old database file
        import os

        try:
            os.unlink("test.db")

        except FileNotFoundError:
            pass

        # Connect to database
        from cheetah_orm import db
        db.connect("sqlite3", database="test.db")

    def test_01_model(self):
        """Test SQLite data model."""
        from cheetah_orm.db import DataModel, fields

        # Create 2 different data models
        class Numbers(DataModel):
            table = "numbers"
            num1 = fields.IntField()
            num2 = fields.IntField()

        class MoreNumbers(DataModel):
            table = "more_numbers"
            num3 = fields.IntField(default=5)
            num4 = fields.IntField(unique=True)
            num5 = fields.IntField(not_null=True)

        # Initialize tables
        Numbers.init_table()
        MoreNumbers.init_table()

        # Create an instance of each data model
        n = Numbers()
        mn = MoreNumbers()

        # Each data model class should have its own unique SQL code
        self.assertEqual(
            n._insert_sql, "INSERT INTO numbers(`num1`, `num2`) VALUES (?, ?);")
        self.assertEqual(
            mn._insert_sql, "INSERT INTO more_numbers(`num3`, `num4`, `num5`) VALUES (?, ?, ?);")
        self.assertNotEqual(n._insert_sql, mn._insert_sql)
        self.assertEqual(DataModel._insert_sql, None)

    def test_02_fields(self):
        """Test SQLite fields."""
        from datetime import datetime
        import os

        from cheetah_orm.db import DataModel, fields

        # Create data model
        class Player(DataModel):
            table = "players"
            name = fields.StringField(length=32, unique=True, not_null=True)
            pswd = fields.PswdField(length=128, not_null=True)
            age = fields.IntField(not_null=True)
            avg_score = fields.FloatField(default=0, not_null=True)
            token = fields.BinaryField(not_null=True)
            joined = fields.DateTimeField(not_null=True)
            player_id = fields.BigIntField(not_null=True)

        Player.init_table()

        # Generate some random tokens
        tok1 = os.urandom(32)
        tok2 = os.urandom(32)
        tok3 = os.urandom(32)
        tok4 = os.urandom(32)

        # Create some players
        dt1 = datetime.now()
        p1 = Player(
            name="Sam",
            pswd="cat",
            age=20,
            avg_score=21.5,
            token=tok1,
            joined=dt1,
            player_id=468523841384123841
        )

        dt2 = datetime.now()
        p2 = Player(
            name="Jake",
            pswd="tiger",
            age=30,
            avg_score=50.9,
            token=tok2,
            joined=dt2,
            player_id=987225841357412593
        )

        dt3 = datetime.now()
        p3 = Player(
            name="Susan",
            pswd="wolf",
            age=80,
            avg_score=5000,
            token=tok3,
            joined=dt3,
            player_id=1236479546317896537
        )

        dt4 = datetime.now()
        p4 = Player(
            name="Billy",
            pswd="boy",
            age=10,
            token=tok4,
            joined=dt4,
            player_id=3248978531364965324
        )
        # print(p1._insert_sql)

        # Save all 4 players
        p1.save(commit=False)
        p2.save(commit=False)
        p3.save(commit=False)
        p4.save()

        # Verify the data
        self.assertEqual(p1.id, 1)
        self.assertEqual(p1.name, "Sam")
        self.assertEqual(p1.pswd, "cat")
        self.assertEqual(p1.age, 20)
        self.assertEqual(p1.avg_score, 21.5)
        self.assertEqual(p1.token, tok1)
        self.assertEqual(p1.joined, dt1)
        self.assertEqual(p1.player_id, 468523841384123841)

        self.assertEqual(p2.id, 2)
        self.assertEqual(p2.name, "Jake")
        self.assertEqual(p2.pswd, "tiger")
        self.assertEqual(p2.age, 30)
        self.assertEqual(p2.avg_score, 50.9)
        self.assertEqual(p2.token, tok2)
        self.assertEqual(p2.joined, dt2)
        self.assertEqual(p2.player_id, 987225841357412593)

        self.assertEqual(p3.id, 3)
        self.assertEqual(p3.name, "Susan")
        self.assertEqual(p3.pswd, "wolf")
        self.assertEqual(p3.age, 80)
        self.assertEqual(p3.avg_score, 5000)
        self.assertEqual(p3.token, tok3)
        self.assertEqual(p3.joined, dt3)
        self.assertEqual(p3.player_id, 1236479546317896537)

        self.assertEqual(p4.id, 4)
        self.assertEqual(p4.name, "Billy")
        self.assertEqual(p4.pswd, "boy")
        self.assertEqual(p4.age, 10)
        self.assertEqual(p4.avg_score, 0)
        self.assertEqual(p4.token, tok4)
        self.assertEqual(p4.joined, dt4)
        self.assertEqual(p4.player_id, 3248978531364965324)

    def test_03_field_modification(self):
        """Test SQLite field modification."""
        from cheetah_orm.db import DataModel, fields

        # Create data model
        class Player(DataModel):
            table = "players"
            name = fields.StringField(length=32, unique=True, not_null=True)
            pswd = fields.PswdField(length=128, not_null=True)
            age = fields.IntField(not_null=True)
            avg_score = fields.FloatField(default=0, not_null=True)
            token = fields.BinaryField(not_null=True)
            joined = fields.DateTimeField(not_null=True)

        # Modify Billy and discard the changes
        billy = Player(id=4)
        billy.age = 40
        billy.discard()

        # Modify Susan and save the changes
        susan = Player(id=3)
        susan.age = 20
        susan.save()

        # Verify the data
        self.assertEqual(billy.age, 10)
        self.assertEqual(susan.age, 20)

    def test_04_filtering(self):
        """Test SQLite model filtering."""
        from cheetah_orm.db import DataModel, fields

        # Create data model
        class Player(DataModel):
            table = "players"
            name = fields.StringField(length=32, unique=True, not_null=True)
            pswd = fields.PswdField(length=128, not_null=True)
            age = fields.IntField(not_null=True)
            avg_score = fields.FloatField(default=0, not_null=True)
            token = fields.BinaryField(not_null=True)
            joined = fields.DateTimeField(not_null=True)

            def __str__(self):
                """Return the string representation of this data model."""
                return f"Player(\n    id = {self.id}\n    name = '{self.name}', \n    pswd = '{self.pswd}', \n    age = {self.age}, \n    avg_score = {self.avg_score}, \n    token = '{self.token}', \n    joined = '{self.joined}'\n)"

        # Fetch all players sorted by name
        players = Player.filter(order_by="name")
        # print()
        # print("Players")
        # print("=======")

        # for player in players:
        #     print(player)

        self.assertEqual(len(players), 4)

        # Fetch all players sorted in descending order by name
        players = Player.filter(order_by="name", descending=True)
        # print()
        # print("Players in Descending Order")
        # print("===========================")

        # for player in players:
        #     print(player)

        self.assertEqual(players[0].name, "Susan")

        # Fetch all players with an age of 20
        players = Player.filter(age_eq=20)
        # print()
        # print("Players with an Age of 20")
        # print("=========================")

        for player in players:
            # print(player)
            self.assertEqual(player.age, 20)

        # Fetch all players with an age that isn't 20
        players = Player.filter(age_neq=20)
        # print()
        # print("Players with an Age that isn't 20")
        # print("=================================")

        for player in players:
            # print(player)
            self.assertNotEqual(player.age, 20)

        # Fetch all players with a score less than 5000
        players = Player.filter(avg_score_lt=5000)
        # print()
        # print("Players with a Score Less Than 5000")
        # print("===================================")

        for player in players:
            # print(player)
            self.assertLess(player.avg_score, 5000)

        # Fetch all players with a score greater than 50
        players = Player.filter(avg_score_gt=50)
        # print()
        # print("Players with a Score Greater Than 50")
        # print("====================================")

        for player in players:
            # print(player)
            self.assertGreater(player.avg_score, 50)

        # Fetch all players with a score less than or equal to 50.9
        players = Player.filter(avg_score_lte=50.9)
        # print()
        # print("Players with a Score Less Than or Equal to 50.9")
        # print("================================================")

        for player in players:
            # print(player)
            self.assertLessEqual(player.avg_score, 50.9)

        # Fetch all players with an age greater than or equal to 20
        players = Player.filter(age_gte=20)
        # print()
        # print("Players with an Age Greater Than or Equal to 20")
        # print("===============================================")

        for player in players:
            # print(player)
            self.assertGreaterEqual(player.age, 20)

        # Fetch all players with an age greater than or equal to 20 and a score greater than 50
        players = Player.filter(age_gte=20, and_avg_score_gt=50)
        # print()
        # print("Players with an Age Greater Than or Equal to 20 and a Score Greater Than 50")
        # print("===========================================================================")

        for player in players:
            # print(player)
            self.assertTrue(player.age >= 20 and player.avg_score > 50)

        # Fetch all players with an age less than 30 or a score greater than 50
        players = Player.filter(age_lt=30, or_avg_score_gt=50)
        # print()
        # print("Players with an Age Less Than 30 or a Score Greater Than 50")
        # print("===========================================================")

        for player in players:
            # print(player)
            self.assertTrue(player.age < 30 or player.avg_score > 50)

        # Fetch the middle 2 players
        players = Player.filter(offset=1, limit=2)
        # print()
        # print("Middle 2 Players")
        # print("================")

        # for player in players:
        #     print(player)

        self.assertEqual(len(players), 2)

    def test_05_indexes(self):
        """Test SQLite indexes."""
        from datetime import datetime
        from sqlite3 import IntegrityError

        from cheetah_orm.db import DataModel, fields

        # Create data model
        class User(DataModel):
            table = "users"
            name = fields.StringField(
                length=32, unique=True, not_null=True, key=True)
            pswd = fields.PswdField(length=128, not_null=True)
            email = fields.StringField(length=256, unique=True, not_null=True)
            ban = fields.DateTimeField(default=datetime.now())

        User.init_table()

        # Create some users
        User(
            name="Dylan",
            pswd="cheetah",
            email="cybermals@googlegroups.com"
        ).save(commit=False)

        User(
            name="Fiona",
            pswd="fox",
            email="cybermals.group@gmail.com"
        ).save(commit=False)
        User(
            name="Zorcodo",
            pswd="moose",
            email="none"
        ).save()

        # This should cause the unique constraint to fail
        self.assertRaises(
            IntegrityError,
            User(
                name="Daniel",
                pswd="lion",
                email="cybermals.group@gmail.com"
            ).save
        )

    def test_06_foreign_keys(self):
        """Test SQLite foreign keys."""
        from datetime import datetime

        from cheetah_orm.db import DataModel, fields

        # Create data models
        class User(DataModel):
            table = "users"
            name = fields.StringField(
                length=32, unique=True, not_null=True, key=True)
            pswd = fields.PswdField(length=128, not_null=True)
            email = fields.StringField(length=256, unique=True, not_null=True)
            ban = fields.DateTimeField(default=datetime.now())

        class Post(DataModel):
            table = "posts"
            author = fields.IntField(foreign_key=User)
            date = fields.DateTimeField(not_null=True)
            content = fields.StringField(length=65535, not_null=True)

        Post.init_table()

        # Fetch 2 users
        dylan, zorcodo = User.filter(name_eq="Dylan", or_name_eq="Zorcodo")

        # Create some posts
        Post(
            author=dylan,
            date=datetime.now(),
            content="Welcome everyone!"
        ).save(commit=False)
        Post(
            author=dylan,
            date=datetime.now(),
            content="How's everyone doing today?"
        ).save(commit=False)
        Post(
            author=zorcodo,
            date=datetime.now(),
            content="Mwahaha! You'll see."
        ).save(commit=False)
        Post(
            author=zorcodo,
            date=datetime.now(),
            content="My evil plan is about to come to fruition."
        ).save()

        # Verify the data
        latest_post = Post.filter(order_by="date")[-1]
        self.assertEqual(latest_post.author.name, zorcodo.name)
        self.assertEqual(len(dylan.Posts), 2)

        # Delete a user that has posted
        zorcodo.delete()

        # Verify the data
        users = User.filter()
        posts = Post.filter()
        self.assertTrue(len(users) == 2 and len(posts) == 2)

    def test_07_drop_table(self):
        """Test dropping an SQLite table."""
        from sqlite3 import OperationalError

        from cheetah_orm.db import DataModel, fields

        # Create data model
        class Player(DataModel):
            table = "players"
            name = fields.StringField(length=32, unique=True, not_null=True)
            pswd = fields.PswdField(length=128, not_null=True)
            age = fields.IntField(not_null=True)
            avg_score = fields.FloatField(default=0, not_null=True)
            token = fields.BinaryField(not_null=True)
            joined = fields.DateTimeField(not_null=True)
            player_id = fields.BigIntField(not_null=True)

        Player.drop_table()

        # Ensure that the table no longer exists
        self.assertRaises(
            OperationalError,
            Player.filter
        )

    def test_08_string_field_default(self):
        """Test string field default value."""
        from cheetah_orm.db import DataModel, fields

        # Create data model
        class Word(DataModel):
            table = "words"
            word = fields.StringField(length=32, not_null=True, default="")

        Word.init_table()

    def test_09_filter_by_foreign_key(self):
        """Test filtering by a foreign key."""
        from datetime import datetime

        from cheetah_orm.db import DataModel, fields

        # Create data models
        class User(DataModel):
            table = "users"
            name = fields.StringField(
                length=32, unique=True, not_null=True, key=True)
            pswd = fields.PswdField(length=128, not_null=True)
            email = fields.StringField(length=256, unique=True, not_null=True)
            ban = fields.DateTimeField(default=datetime.now())

        class Post(DataModel):
            table = "posts"
            author = fields.IntField(foreign_key=User)
            date = fields.DateTimeField(not_null=True)
            content = fields.StringField(length=65535, not_null=True)

        # Fetch Dylan
        dylan = User.filter(name_eq="Dylan")[0]

        # Fetch Dylan's posts without using the backref
        self.assertEqual(len(Post.filter(author_eq=dylan)), 2)

    def test_10_invalid_filter(self):
        """Test invalid filter."""
        from datetime import datetime

        from cheetah_orm.db import DataModel, fields
        from cheetah_orm.exceptions import InvalidFilter

        # Create data models
        class User(DataModel):
            table = "users"
            name = fields.StringField(
                length=32, unique=True, not_null=True, key=True)
            pswd = fields.PswdField(length=128, not_null=True)
            email = fields.StringField(length=256, unique=True, not_null=True)
            ban = fields.DateTimeField(default=datetime.now())

        # Try using invalid filters
        self.assertRaises(
            InvalidFilter,
            User.filter,
            name_eq="Dylan",
            email_eq="cybermals@googlegroups.com"
        )

        self.assertRaises(
            InvalidFilter,
            User.filter,
            name="Dylan"
        )

    def test_11_compound_index(self):
        """Test compound index."""
        from cheetah_orm.db import DataModel, fields

        # Create data models
        class Customer(DataModel):
            table = "customers"
            first_name = fields.StringField(length=32)
            last_name = fields.StringField(length=32)
            address = fields.StringField(length=256)

        Customer.init_table()
        Customer.create_index("name", True, "first_name", "last_name")

        # Create some records
        Customer(
            first_name="John",
            last_name="Doe",
            address="1234 Somewhere"
        ).save(commit=False)
        Customer(
            first_name="Jane",
            last_name="Doe",
            address="5678 Somewhere Else"
        ).save()

    def test_12_migrations(self):
        """Test data migrations."""
        from datetime import datetime

        from cheetah_orm.db import DataModel, fields

        # Create data models
        class Customer(DataModel):
            table = "customers"
            first_name = fields.StringField(length=32)
            last_name = fields.StringField(length=32)
            address = fields.StringField(length=256)
            phone_num = fields.StringField(length=16)

        Customer.init_table()
        Customer.create_index("name", True, "first_name", "last_name")

        # Verify data integrity
        customers = Customer.filter()

        self.assertEqual(customers[0].first_name, "John")
        self.assertEqual(customers[0].last_name, "Doe")
        self.assertEqual(customers[0].address, "1234 Somewhere")
        self.assertEqual(customers[0].phone_num, None)

        self.assertEqual(customers[1].first_name, "Jane")
        self.assertEqual(customers[1].last_name, "Doe")
        self.assertEqual(customers[1].address, "5678 Somewhere Else")
        self.assertEqual(customers[1].phone_num, None)

        # Create data models
        class User(DataModel):
            table = "users"
            name = fields.StringField(
                length=32, unique=True, not_null=True, key=True)
            pswd = fields.PswdField(length=128, not_null=True)
            email = fields.StringField(length=256, unique=True, not_null=True)
            question = fields.StringField(length=256, not_null=True, default="")
            answer = fields.StringField(length=256, not_null=True, default="")

        User.init_table()

        class Post(DataModel):
            table = "posts"
            author = fields.IntField(foreign_key=User)
            date = fields.DateTimeField(not_null=True)
            token = fields.StringField(length=128, unique=True, not_null=True, default="")
            content = fields.StringField(length=65535, not_null=True)

        Post.init_table()

        # Test foreign keys after migration
        dylan = User.filter(name_eq="Dylan")[0]
        self.assertEqual(len(dylan.Posts), 2)

    def test_13_rename_field(self):
        """Test field renaming."""
        from cheetah_orm.db import DataModel, fields

        # Create data models
        class User(DataModel):
            table = "users"
            name = fields.StringField(
                length=32, unique=True, not_null=True, key=True)
            pswd = fields.PswdField(length=128, not_null=True)
            email = fields.StringField(length=256, unique=True, not_null=True)
            question = fields.StringField(length=256, not_null=True, default="")
            answer = fields.StringField(length=256, not_null=True, default="")

        User.init_table()

        class Post(DataModel):
            table = "posts"
            author = fields.IntField(foreign_key=User)
            date = fields.DateTimeField(not_null=True)
            token = fields.StringField(length=128, unique=True, not_null=True, default="")
            message = fields.StringField(length=65535, not_null=True, default="")

        Post.init_table()

        # Verify data integrity
        posts = Post.filter()

        for post in posts:
            self.assertNotEqual(post.message, "")

    def test_14_invalid_column_name(self):
        """Test invalid column names."""
        from cheetah_orm.db import DataModel, fields

        # Create data models
        class InvalidData(DataModel):
            table = "invalid_data"
            group = fields.IntField()

        InvalidData.init_table()


# Entry Point
# ===========
if __name__ == "__main__":
    unittest.main()
