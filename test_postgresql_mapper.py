"""Cheetah ORM - PostgreSQL Mapper Unit Tests"""

from datetime import datetime
import unittest

from cheetah_orm.fields import (
    BigIntField,
    BlobField,
    DateTimeField,
    DoubleField,
    IntField,
    FloatField,
    PasswordField,
    StringField
)
from cheetah_orm.indexes import ForeignKey, Index, UniqueIndex
from cheetah_orm.mappers import PostgreSQLMapper
from cheetah_orm.model import DataModel


# Classes
# =======
class User(DataModel):
    table      = "users"
    name       = StringField(length=32, not_null=True)
    pswd       = PasswordField(length=128, not_null=True)
    email      = StringField(length=128, not_null=True)
    question   = StringField(length=128, not_null=True)
    answer     = StringField(length=128, not_null=True)
    joined     = DateTimeField(not_null=True, default="now()")
    ban        = DateTimeField(not_null=True, default="now()")
    name_idx   = UniqueIndex("name")
    email_idx  = UniqueIndex("email")
    joined_idx = Index("joined")


class Post(DataModel):
    table      = "posts"
    user       = BigIntField(not_null=True)
    date       = DateTimeField(not_null=True, default="now()")
    content    = StringField(length=65535, not_null=True)
    user_idx   = ForeignKey(User, "id")
    date_idx   = Index("date")


class TestPostgreSQLMapper(unittest.TestCase):
    """PostgreSQL Mapper Tests"""
    @classmethod
    def setUpClass(cls):
        """Cleanup data from last test."""
        mapper = PostgreSQLMapper()
        mapper.connect(host="localhost", user="tester", password="test", dbname="testing")
        mapper._cur.execute('DROP TABLE IF EXISTS "posts";')
        mapper._cur.execute('DROP TABLE IF EXISTS "users";')
        mapper.commit()
        mapper.disconnect()

    def test_1_connection(self):
        """Test database connection."""
        # Establish a database connection
        mapper = PostgreSQLMapper()
        mapper.connect(host="localhost", user="tester", password="test", dbname="testing")

        # Disconnect from the database
        mapper.disconnect()

    def test_2_init_model(self):
        """Test data model initialization."""
        # Establish a database connection
        mapper = PostgreSQLMapper()
        mapper.connect(host="localhost", user="tester", password="test", dbname="testing")

        # Initialize data models
        mapper.init_model(User)
        mapper.init_model(Post)

        # Check SQL cache
        self.assertEqual(mapper._cache[User]["insert"], 'INSERT INTO "users"("name","pswd","email","question","answer","joined","ban") VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING "id";')
        self.assertEqual(mapper._cache[User]["update"], 'UPDATE "users" SET "name"=%s,"pswd"=%s,"email"=%s,"question"=%s,"answer"=%s,"joined"=%s,"ban"=%s WHERE "id"=%s;')
        self.assertEqual(mapper._cache[User]["delete"], 'DELETE FROM "users" WHERE "id"=%s;')
        self.assertEqual(mapper._cache[User]["select"], 'SELECT "id","name","pswd","email","question","answer","joined","ban" FROM "users"')
        self.assertEqual(mapper._cache[Post]["insert"], 'INSERT INTO "posts"("user","date","content") VALUES (%s,%s,%s) RETURNING "id";')
        self.assertEqual(mapper._cache[Post]["update"], 'UPDATE "posts" SET "user"=%s,"date"=%s,"content"=%s WHERE "id"=%s;')
        self.assertEqual(mapper._cache[Post]["delete"], 'DELETE FROM "posts" WHERE "id"=%s;')
        self.assertEqual(mapper._cache[Post]["select"], 'SELECT "id","user","date","content" FROM "posts"')

        # Disconnect from the database
        mapper.disconnect()

    def test_3_save_model(self):
        """Test data model saving."""
        # Establish a database connection
        mapper = PostgreSQLMapper()
        mapper.connect(host="localhost", user="tester", password="test", dbname="testing")

        # Initialize data models
        mapper.init_model(User)
        mapper.init_model(Post)

        # Create some data models and save them
        daniel = User(
            name="Daniel",
            pswd="lion",
            email="daniel@lionzrule.com",
            question="Favorite species?",
            answer="lion"
        )
        leila = User(
            name="Leila",
            pswd="lioness",
            email="leila@lionzrule.com",
            question="Favorite species?",
            answer="lioness"
        )
        james = User(
            name="James",
            pswd="cheetah",
            email="james@cheetahzrule.com",
            question="Favorite species?",
            answer="cheetah"
        )
        abby = User(
            name="Abby",
            pswd="cheetahess",
            email="abby@cheetahzrule.com",
            question="Favorite species?",
            answer="cheetah"
        )
        fiona = User(
            name="Fiona",
            pswd="fox",
            email="fiona@foxezrule.com",
            question="Favorite species?",
            answer="fox"
        )
        unknown = User(
            name="Unknown",
            pswd="",
            email="",
            question="",
            answer=""
        )

        mapper.save_model(daniel)
        mapper.save_model(leila)
        mapper.save_model(james)
        mapper.save_model(abby)
        mapper.save_model(fiona)
        mapper.save_model(unknown)
        mapper.commit()

        # Check model IDs
        self.assertEqual(daniel.id, 1)
        self.assertEqual(leila.id, 2)
        self.assertEqual(james.id, 3)
        self.assertEqual(abby.id, 4)
        self.assertEqual(fiona.id, 5)
        self.assertEqual(unknown.id, 6)

        # Update the models and save them
        daniel.question = "Favorite animal?"
        leila.question = "Favorite animal?"
        james.question = "Favorite animal?"
        abby.question = "Favorite animal?"
        fiona.question = "Favorite animal?"

        mapper.save_model(daniel)
        mapper.save_model(leila)
        mapper.save_model(james)
        mapper.save_model(abby)
        mapper.save_model(fiona)
        mapper.commit()

        # Disconnect from the database
        mapper.disconnect()

    def test_4_delete_model(self):
        """Test data model deletion."""
        # Establish a database connection
        mapper = PostgreSQLMapper()
        mapper.connect(host="localhost", user="tester", password="test", dbname="testing")

        # Initialize data models
        mapper.init_model(User)
        mapper.init_model(Post)

        # Delete a model
        mapper.delete_model(User(id=6))
        mapper.commit()

        # Disconnect from the database
        mapper.disconnect()

    def test_5_filter(self):
        """Test data model filtering."""
        # Establish a database connection
        mapper = PostgreSQLMapper()
        mapper.connect(host="localhost", user="tester", password="test", dbname="testing")

        # Initialize data models
        mapper.init_model(User)
        mapper.init_model(Post)

        # Fetch all users
        users = mapper.filter(User)
        self.assertEqual(len(users), 5)

        # Fetch Daniel
        users = mapper.filter(User, "`name`=?", "Daniel")
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].name, "Daniel")

        # Fetch Leila and Abby
        users = mapper.filter(User, "`name`=? OR `name`=?", "Leila", "Abby")
        self.assertEqual(len(users), 2)
        
        for user in users:
            self.assertTrue(user.name in ["Leila", "Abby"])

        # Fetch all users with "Favorite animal?" as their security question ordered by username
        users = mapper.filter(User, "`question`=?", "Favorite animal?", order_by=["name"])
        self.assertEqual(len(users), 5)
        self.assertEqual(users[0].name, "Abby")
        self.assertEqual(users[4].name, "Leila")

        # The middle 2 users
        users = mapper.filter(User, "`question`=?", "Favorite animal?", order_by=["name"], offset=1, limit=2)
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].name, "Daniel")
        self.assertEqual(users[1].name, "Fiona")

        # Disconnect from the database
        mapper.disconnect()

    def test_6_foreign_keys(self):
        """Test foreign keys."""
        # Establish a database connection
        mapper = PostgreSQLMapper()
        mapper.connect(host="localhost", user="tester", password="test", dbname="testing")

        # Initialize data models
        mapper.init_model(User)
        mapper.init_model(Post)

        # Create some posts
        post = Post(
            user=1,
            content="Hello everyone!"
        )
        mapper.save_model(post)

        post = Post(
            user=2,
            content="Hello!"
        )
        mapper.save_model(post)

        post = Post(
            user=3,
            content="Hi!"
        )
        mapper.save_model(post)

        post = Post(
            user=4,
            content="Heya!"
        )
        mapper.save_model(post)

        post = Post(
            user=5,
            content="Hello darling!"
        )
        mapper.save_model(post)

        post = Post(
            user=5,
            content="Huh? ...Help!"
        )
        mapper.save_model(post)

        post = Post(
            user=1,
            content="Oh no!"
        )
        mapper.save_model(post)

        # Now delete a user
        mapper.delete_model(User(id=5))
        mapper.commit()

        # Verify that the user's posts were deleted too
        posts = mapper.filter(Post, "`user`=?", 5)
        self.assertEqual(len(posts), 0)

        # Disconnect from the database
        mapper.disconnect()

    def test_7_count_results(self):
        """Test result counting."""
        # Establish a database connection
        mapper = PostgreSQLMapper()
        mapper.connect(host="localhost", user="tester", password="test", dbname="testing")

        # Initialize data models
        mapper.init_model(User)
        mapper.init_model(Post)

        # Test result counting
        user_cnt = mapper.count(User)
        users = mapper.filter(User)
        self.assertEqual(user_cnt, len(users))

        # Disconnect from the database
        mapper.disconnect()
