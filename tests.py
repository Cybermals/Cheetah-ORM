"""Cheetah ORM - Unit Tests"""

import os
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

        dt2 = datetime.now()
        p2 = Player(
            name = "Jake",
            pswd = "tiger",
            age = 30,
            avg_score = 50.9,
            token = tok2,
            joined = dt2
        )

        dt3 = datetime.now()
        p3 = Player(
            name = "Susan",
            pswd = "wolf",
            age = 80,
            avg_score = 5000,
            token = tok3,
            joined = dt3
        )

        dt4 = datetime.now()
        p4 = Player(
            name = "Billy",
            pswd = "boy",
            age = 10,
            token = tok4,
            joined = dt4
        )
        print(p1._insert_sql)

        #Save all 4 players
        p1.save()
        p2.save()
        p3.save()
        p4.save()

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

        #Modify Billy and discard the changes
        billy = Player(id = 4)
        billy.age = 40
        billy.discard()

        #Modify Susan and save the changes
        susan = Player(id = 3)
        susan.age = 20
        susan.save()

        #Test data
        self.assertEqual(billy.age, 10)
        self.assertEqual(susan.age, 20)

    def test_4_filtering(self):
        """Test SQLite model filtering."""
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

            def __str__(self):
                """Return the string representation of this data model."""
                return f"Player(\n    id = {self.id}\n    name = '{self.name}', \n    pswd = '{self.pswd}', \n    age = {self.age}, \n    avg_score = {self.avg_score}, \n    token = '{self.token}', \n    joined = '{self.joined}'\n)"

        #Fetch all players sorted by name
        players = Player.filter(order_by = "name")
        print()
        print("Players")
        print("=======")
        
        for player in players:
            print(player)

        #Fetch all players with an age of 20
        players = Player.filter(age_eq = 20)
        print()
        print("Players with an Age of 20")
        print("=========================")

        for player in players:
            print(player)
            self.assertEqual(player.age, 20)

        #Fetch all players with an age that isn't 20
        players = Player.filter(age_neq = 20)
        print()
        print("Players with an Age that isn't 20")
        print("=================================")

        for player in players:
            print(player)
            self.assertNotEqual(player.age, 20)

        #Fetch all players with a score less than 5000
        players = Player.filter(avg_score_lt = 5000)
        print()
        print("Players with a Score Less Than 5000")
        print("===================================")

        for player in players:
            print(player)
            self.assertLess(player.avg_score, 5000)

        #Fetch all players with a score greater than 50
        players = Player.filter(avg_score_gt = 50)
        print()
        print("Players with a Score Greater Than 50")
        print("====================================")

        for player in players:
            print(player)
            self.assertGreater(player.avg_score, 50)

        #Fetch all players with a score less than or equal to 50.9
        players = Player.filter(avg_score_lte = 50.9)
        print()
        print("Players with a Score Less Than or Equal to 50.9")
        print("================================================")

        for player in players:
            print(player)
            self.assertLessEqual(player.avg_score, 50.9)

        #Fetch all players with an age greater than or equal to 20
        players = Player.filter(age_gte = 20)
        print()
        print("Players with an Age Greater Than or Equal to 20")
        print("===============================================")

        for player in players:
            print(player)
            self.assertGreaterEqual(player.age, 20)

        #Fetch all players with an age greater than or equal to 20 and a score greater than 50
        players = Player.filter(age_gte = 20, and_avg_score_gt = 50)
        print()
        print("Players with an Age Greater Than or Equal to 20 and a Score Greater Than 50")
        print("===========================================================================")

        for player in players:
            print(player)
            self.assertGreaterEqual(player.age, 20)
            self.assertGreater(player.avg_score, 50)

        #Fetch all players with an age less than 30 or a score greater than 50
        players = Player.filter(age_lt = 30, or_avg_score_gt = 50)
        print()
        print("Players with an Age Less Than 30 or a Score Greater Than 50")
        print("===========================================================")

        for player in players:
            print(player)
            self.assertTrue(player.age < 30 or player.avg_score > 50)

    def test_5_indexes(self):
        """Test SQLite indexes."""
        from datetime import datetime
        from sqlite3 import IntegrityError

        from cheetah_orm.db import DataModel, fields

        #Create data model
        class User(DataModel):
            table = "users"
            name = fields.StringField(length = 32, unique = True, not_null = True, key = True)
            pswd = fields.PswdField(length = 128, not_null = True)
            email = fields.StringField(length = 256, unique = True, not_null = True)
            ban = fields.DateTimeField(default = datetime.now())

        User.init_table()

        #Create some users
        User(
            name = "Dylan",
            pswd = "cheetah",
            email = "cybermals@googlegroups.com"
        ).save()

        User(
            name = "Fiona",
            pswd = "fox",
            email = "cybermals.group@gmail.com"
        ).save()

        #This should cause the unique constraint to fail
        self.assertRaises(
            IntegrityError,
            User(
                name = "Daniel",
                pswd = "lion",
                email = "cybermals.group@gmail.com"
            ).save
        )


#Entry Point
#===========
if __name__ == "__main__":
    unittest.main()
