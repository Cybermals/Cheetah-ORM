# Cheetah-ORM
A lightweight and high-performance object relational mappper written in pure Python.


## Installation
`pip install cheetah_orm`

Note: To use MySQL or MariaDB you will need to install the "mysql_connector_python" package as well. And
to use PostgreSQL, you will need to install the "psycopg" package too. SQLite support requires no
additonal packages.


## Building
1. clone this repo
2. install the "wheel" package by executing `pip install wheel`
3. from the repo folder, execute `./setup.py bdist_wheel`
4. there will be a wheel file inside the "dist" folder


## Features
* support for sqlite3, MariaDB/MySQL, and PostgreSQL
* high-level database-neutral API written in pure Python
* automatically generates the needed SQL statements for whichever database system you prefer to
  use
* rich filtering API supports equality, inequality, less than, greater than, less than or equal 
  to, greater than or equal to, logical or, and logical and as well as sorting and limits


## Known Bugs
* dropping a table fails when a PostgreSQL table was recently accessed during a database session due to
  table locking


## Usage
```python
#Connect to a database. This must be done before importing the data model and field classes.
from cheetah_orm import db
db.connect("sqlite3", database = ":memory:")

#Import the data model and field classes
from cheetah_orm.db import DataModel, fields

#Define one or more data models. Some fields such as the "PswdField" and "DateTimeField" have
#additional functionality. For example, password fields automatically hash the password before
#storing it and return a "Password" object when fetching the value in the field. You can then
#compare the password object to the unhashed password with the "==" operator.
class User(DataModel):
    table = "users"
    name = StringField(length = 32, unique = True, not_null = True, key = True)
    pswd = PswdField(length = 128, not_null = True)
    email = StringField(length = 256, not_null = True)
    logins = IntField(default = 0)

class Post(DataModel):
    table = "posts"
    user = IntField(foreign_key = User)
    date = DateTimeField()
    content = StringField(length = 65535)

#Initialize the table for each data model. This only needs to be done once per data model, but
#doing it each time you run the program is harmless.
User.init_table()
Post.init_table()

#Create data model instances and save them to the database. You can initialize the fields by
#passing their values as keyword parameters or by setting their values after creating the data
#model instance. The field data will be cached in the data model instance until you save it to
#the database. Notice that you can defer committing the transaction by passing "commit = False"
#to the "save" method of the data model. Calling the "save" method without any parameters will
#commit the entire transaction.
dylan = User(
    name = "Dylan",
    pswd = "cheetah,
    email = "cybermals@googlegroups.com"
)
dylan.save(commit = False)

fiona = User()
fiona.name = "Fiona"
fiona.pswd = "fox"
fiona.email = "cybermals@googlegroups.com"
fiona.save(commit = False)

daniel = User(
    name = "Daniel",
    pswd = "lion",
    email = "cybermals@googlegroups.com"
)
daniel.save()

#Modifying data is achieved by setting fields on a data model instance and calling its "save"
#method. Calling the "discard" method will instead discard the changes you have made since the
#last time you called "save" on any data model.
dylan.logins = 200
dylan.save()

fiona.logins = 100
fiona.save()

daniel.logins = 300
daniel.discard()

#You can pass data model instances directly into foreign key fields which reference that given
#type of data model. You can pass datetime instances into date time fields too.
Post(
    user = dylan,
    date = datetime.now(),
    content = "Hello World!"
).save(commit = False)

Post(
    user = fiona,
    date = datetime.now(),
    content = "Hello Dylan! How are you?"
).save(commit = False)

Post(
    user = dylan,
    date = datetime.now(),
    content = "I am well. How about you?"
).save(commit = False)

Post(
    user = fiona,
    date = datetime.now(),
    content = "I am fabulous! ^^"
).save()

#You can retrieve data from the database by using the "filter" method of a data model class.
#Calling the filter method with no parameters will return all instances of a particular data
#model sorted by ID. Use keyword parameters to narrow down your search. The filter method
#understands keywords such as "name_eq", "and_email_neq", and "or_date_gt", which represent
#various combinations of SQL condition keywords. You can also choose a field to sort by with the
#"order_by" keyword and limit the number of results with the "limit" keyword.
users = User.filter(order_by = "name", logins_lt = 200)

#Data models that are referenced by a foreign key field in another model will have a backreference
#to the collection of data models which refer to that particular data model. Said backreference
#will always have the same name as the type of the model that is referring to the other model with
#the letter "s" added to the end of the name.
my_first_post = dylan.Posts[0]
```
