#!/usr/bin/python3
"""Cheetah ORM - Demo"""

from datetime import datetime
import os
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
from cheetah_orm.mappers import SQLiteMapper
from cheetah_orm.model import DataModel


# Delete last database
try:
    os.unlink("users.db")

except:
    pass


# Define data models
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


# Establish a database connection
mapper = SQLiteMapper()
mapper.connect(database="users.db")

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

# Delete a model
mapper.delete_model(User(id=6))
mapper.commit()

# Fetch all users
users = mapper.filter(User)
print("Users:")

for user in users:
    print(user)

print()

# Fetch Daniel
users = mapper.filter(User, "`name`=?", "Daniel")
print("Users Named 'Daniel':")

for user in users:
    print(user)

print()

# Fetch Leila and Abby
users = mapper.filter(User, "`name`=? OR `name`=?", "Leila", "Abby")
print("Users Named 'Leila' or 'Abby':")

for user in users:
    print(user)

print()

# Fetch all users with "Favorite animal?" as their security question ordered by username
users = mapper.filter(User, "`question`=?", "Favorite animal?", order_by=["name"])
print("Users with the Security Question 'Favorite animal?' Ordered by Username:")

for user in users:
    print(user)

print()

# The middle 2 users
users = mapper.filter(User, "`question`=?", "Favorite animal?", order_by=["name"], offset=1, limit=2)
print("The Middle 2 Users:")

for user in users:
    print(user)

print()

# Create some posts
post = Post(
    user=daniel.id,
    content="Hello everyone!"
)
mapper.save_model(post)

post = Post(
    user=leila.id,
    content="Hello!"
)
mapper.save_model(post)

post = Post(
    user=james.id,
    content="Hi!"
)
mapper.save_model(post)

post = Post(
    user=abby.id,
    content="Heya!"
)
mapper.save_model(post)

post = Post(
    user=fiona.id,
    content="Hello darling!"
)
mapper.save_model(post)

post = Post(
    user=fiona.id,
    content="Huh? ...Help!"
)
mapper.save_model(post)

post = Post(
    user=daniel.id,
    content="Oh no!"
)
mapper.save_model(post)

# Now delete a user
mapper.delete_model(fiona)
mapper.commit()

# Verify that the user's posts were deleted too
post_cnt = mapper.count(Post, "`user`=?", 5)
print(f"Fiona has {post_cnt} post(s).")

# Disconnect from the database
mapper.disconnect()
