"""Cheetah ORM - Data Model Unit Tests"""

from datetime import datetime
import math
import unittest

from cheetah_orm.constants import *
from cheetah_orm.fields import (
    BigIntField, 
    BlobField, 
    DateTimeField,
    FloatField, 
    DoubleField, 
    IntField, 
    PasswordField, 
    StringField
)
from cheetah_orm.indexes import ForeignKey, Index, UniqueIndex
from cheetah_orm.model import DataModel


# Classes
# =======
class TestDataModel(unittest.TestCase):
    """Data Model Tests"""
    def test_1_model_definition(self):
        """Test data model definitions"""
        # Define 2 data models
        class Model1(DataModel):
            field1 = IntField()
            field2 = IntField()
            field3 = IntField()


        class Point(DataModel):
            x = IntField()
            y = IntField()

        # Ensure that the two classes have different field metadata
        self.assertNotEqual(Model1._fields, Point._fields)

    def test_2_model_instance(self):
        """Test data model instances."""
        # Define a point
        class Point(DataModel):
            x = IntField()
            y = IntField()

        # Create 2 points
        p1 = Point()
        p1.x = 5
        p1.y = 7

        p2 = Point()
        p2.x = 6
        p2.y = 3

        # Ensure that each instance has separate field data storage
        self.assertNotEqual(p1.x, p2.x)
        self.assertNotEqual(p1.y, p2.y)

    def test_3_model_initializer(self):
        """Test model keyword initialization."""
        # Define a point
        class Point(DataModel):
            x = IntField()
            y = IntField()

        # Create a point
        p = Point(
            x=10,
            y=7
        )

        # Ensure that the data model was properly initialized
        self.assertEqual(p.x, 10)
        self.assertEqual(p.y, 7)

    def test_4_fields(self):
        """Test all field types."""
        # Define a data model
        class Model(DataModel):
            field1 = IntField()
            field2 = BigIntField()
            field3 = FloatField()
            field4 = DoubleField()
            field5 = StringField()
            field6 = BlobField()
            field7 = DateTimeField()
            field8 = PasswordField()

        # Ceate an instance
        dt = datetime.now()
        m = Model(
            field1=5,
            field2=1824027104730264027,
            field3=7.2,
            field4=math.pi,
            field5="Hello World!",
            field6=b"My Precious Data",
            field7=dt,
            field8="My Secret Password"
        )

        # Verify field metadata
        self.assertEqual(
            m._fields,
            [
                ("field1", FIELD_TYPE_INT, 10, None),
                ("field2", FIELD_TYPE_BIGINT, 19, None),
                ("field3", FIELD_TYPE_FLOAT, None, None),
                ("field4", FIELD_TYPE_DOUBLE, None, None),
                ("field5", FIELD_TYPE_STRING, 256, None),
                ("field6", FIELD_TYPE_BLOB, 256, None),
                ("field7", FIELD_TYPE_DATETIME, None, None),
                ("field8", FIELD_TYPE_PSWD, 256, None)
            ]
        )

        # Ensure that the data model was properly initialized
        self.assertEqual(m.field1, 5)
        self.assertEqual(m.field2, 1824027104730264027)
        self.assertEqual(m.field3, 7.2)
        self.assertEqual(m.field4, math.pi)
        self.assertEqual(m.field5, "Hello World!")
        self.assertEqual(m.field6, b"My Precious Data")
        self.assertEqual(m.field7, dt)
        self.assertTrue(m.field8 == "My Secret Password")

    def test_5_indexes(self):
        """Test indexes."""
        # Define a data model
        class Customer(DataModel):
            first_name  = StringField(length=32)
            last_name   = StringField(length=32)
            address     = StringField(length=64)
            email       = StringField(length=128)
            name_idx    = UniqueIndex("first_name", "last_name")
            address_idx = Index("address")
            email_idx   = UniqueIndex("email")

        # Verify index metadata
        self.assertEqual(
            Customer._indexes,
            [
                ("name_idx", INDEX_TYPE_UNIQUE_KEY, ("first_name", "last_name")),
                ("address_idx", INDEX_TYPE_KEY, ("address",)),
                ("email_idx", INDEX_TYPE_UNIQUE_KEY, ("email",))
            ]
        )

    def test_6_foreign_keys(self):
        """Test foreign keys."""
        # Define 2 data models
        class User(DataModel):
            name     = StringField(length=32, not_null=True)
            pswd     = PasswordField(length=256, not_null=True)
            email    = StringField(length=128, not_null=True)
            question = StringField(length=128, not_null=True, default="")
            answer   = StringField(length=128, not_null=True, default="")
            name_idx = UniqueIndex("name")
            email    = UniqueIndex("email")

        class Post(DataModel):
            user     = BigIntField(unsigned=True, not_null=True)
            date     = StringField()
            content  = StringField(length=4096, not_null=True)
            user_idx = ForeignKey(User, "id")

        # Verify index metadata
        self.assertEqual(
            Post._indexes,
            [
                ("user_idx", INDEX_TYPE_FOREIGN_KEY, (User, "id"), (FK_CASCADE, FK_RESTRICT))
            ]
        )
