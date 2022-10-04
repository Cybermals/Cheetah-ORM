"""Cheetah ORM - Unit Tests"""

import unittest


#Classes
#=======
class TestSQLiteDBDriver(unittest.TestCase):
    """SQLite database driver tests."""
    @classmethod
    def setUpClass(cls):
        """Setup this test case."""
        #Delete old database file
        import os

        try:
            os.unlink("test.db")

        except FileNotFoundError:
            pass

        #Connect to database
        from cheetah_orm import db
        db.connect("sqlite3", database = "test.db")

    def test_1_model(self):
        """Test SQLite data model."""
        from cheetah_orm.db import DataModel, fields

        #Create 2 different data models
        class Numbers(DataModel):
            table = "numbers"
            num1 = fields.IntField()
            num2 = fields.IntField()

        class MoreNumbers(DataModel):
            table = "more_numbers"
            num3 = fields.IntField(default = 5)
            num4 = fields.IntField(unique = True)
            num5 = fields.IntField(not_null = True)

        #Initialize tables
        Numbers.init_table()
        MoreNumbers.init_table()

        #Create an instance of each data model
        n = Numbers()
        mn = MoreNumbers()

        #Each data model class should have its own unique SQL code
        self.assertEqual(n._insert_sql, "INSERT INTO numbers(num1, num2) VALUES (?, ?);")
        self.assertEqual(mn._insert_sql, "INSERT INTO more_numbers(num3, num4, num5) VALUES (?, ?, ?);")
        self.assertNotEqual(n._insert_sql, mn._insert_sql)
        self.assertEqual(DataModel._insert_sql, None)

    def test_2_fields(self):
        """Test SQLite fields."""
        from datetime import datetime
        import os

        from cheetah_orm.db import DataModel, fields

        #Create data model
        class Player(DataModel):
            table = "players"
            name = fields.StringField(length = 32, unique = True, not_null = True)
            pswd = fields.PswdField(length = 128, not_null = True)
            age = fields.IntField(not_null = True)
            avg_score = fields.FloatField(default = 0, not_null = True)
            token = fields.BinaryField(not_null = True)
            joined = fields.DateTimeField(not_null = True)

        Player.init_table()

        #Generate some random tokens
        tok1 = os.urandom(32)
        tok2 = os.urandom(32)
        tok3 = os.urandom(32)
        tok4 = os.urandom(32)

        #Create some players
        dt1 = datetime.now()
        p1 = Player(
            name = "Sam",
            pswd = "cat",
            age = 20,
            avg_score = 21.5,
            token = tok1,
            joined = dt1
        )
        p1.save()

        dt2 = datetime.now()
        p2 = Player(
            name = "Jake",
            pswd = "tiger",
            age = 30,
            avg_score = 50.9,
            token = tok2,
            joined = dt2
        )
        p2.save()

        dt3 = datetime.now()
        p3 = Player(
            name = "Susan",
            pswd = "wolf",
            age = 80,
            avg_score = 5000,
            token = tok3,
            joined = dt3
        )
        p3.save()

        dt4 = datetime.now()
        p4 = Player(
            name = "Billy",
            pswd = "boy",
            age = 10,
            token = tok4,
            joined = dt4
        )
        p4.save()
        print(p1._insert_sql)

        #Test data
        self.assertEqual(p1.id, 1)
        self.assertEqual(p1.name, "Sam")
        self.assertEqual(p1.pswd, "cat")
        self.assertEqual(p1.age, 20)
        self.assertEqual(p1.avg_score, 21.5)
        self.assertEqual(p1.token, tok1)
        self.assertEqual(p1.joined, dt1)

        self.assertEqual(p2.id, 2)
        self.assertEqual(p2.name, "Jake")
        self.assertEqual(p2.pswd, "tiger")
        self.assertEqual(p2.age, 30)
        self.assertEqual(p2.avg_score, 50.9)
        self.assertEqual(p2.token, tok2)
        self.assertEqual(p2.joined, dt2)

        self.assertEqual(p3.id, 3)
        self.assertEqual(p3.name, "Susan")
        self.assertEqual(p3.pswd, "wolf")
        self.assertEqual(p3.age, 80)
        self.assertEqual(p3.avg_score, 5000)
        self.assertEqual(p3.token, tok3)
        self.assertEqual(p3.joined, dt3)
        
        self.assertEqual(p4.id, 4)
        self.assertEqual(p4.name, "Billy")
        self.assertEqual(p4.pswd, "boy")
        self.assertEqual(p4.age, 10)
        self.assertEqual(p4.avg_score, 0)
        self.assertEqual(p4.token, tok4)
        self.assertEqual(p4.joined, dt4)

    def test_3_field_modification(self):
        """Test SQLite field modification."""
        from cheetah_orm.db import DataModel, fields

        #Create data model
        class Player(DataModel):
            table = "players"
            name = fields.StringField(length = 32, unique = True, not_null = True)
            pswd = fields.PswdField(length = 128, not_null = True)
            age = fields.IntField(not_null = True)
            avg_score = fields.FloatField(default = 0, not_null = True)
            token = fields.BinaryField(not_null = True)
            joined = fields.DateTimeField(not_null = True)

        #Modify Billy and save the changes
        billy = Player(id = 4)
        billy.age = 11
        billy.save()

        #Modify Susan and discard the changes
        susan = Player(id = 3)
        susan.age = 2
        susan.discard()

        #Test data
        self.assertEqual(billy.age, 11)
        self.assertEqual(susan.age, 80)


#Entry Point
#===========
if __name__ == "__main__":
    unittest.main()
