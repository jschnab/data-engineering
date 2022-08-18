# Data Loading

## Overview

Data loading is one of the main step of an Extract Transform Load (ETL)
pipeline. Loading is the process of storing data in a file or object store, or
a database. The goal is to permanently store the data for subsequent processing
step, such as data transformation or analysis.

When loading data it is important to make sure it is performed according to
core data engineering principles such as predictability and reproducibility
(I know where the data is stored), immutability (new data should usually not
overwrite old data), idempotency (it is safe to load the same data several
times to the same location).

In this chapter we will mainly discuss loading data into SQL and NoSQL
databases. Loading to object stores such as AWS S3 is discussed in a different
chapter so we will not repeat this here.

## The SQL language

The is a [plethora](https://skillcrush.com/blog/learn-sql-online/) of free
online resources to learn SQL. We will just point the read to the following
online courses to get started with SQL:

* Khan Academy's [intro to
  SQL](https://www.khanacademy.org/computing/computer-programming/sql) learning
  unit contains videos, quizzes, and mini projects.

* W3Schools [SQL tutorial](https://www.w3schools.com/sql/) is clear and
  interactive. It's a great reference to come back to when we know we can do
  something in SQL but we forgot how.

* [SQLCourse.com](https://www.sqlcourse.com) is clear, provides exercises and
  an interactive SQL interpreter. Don't let the old-school design of the
  website fool you.

* PostgreSQL tutorials at
  [CrunchyData](https://crunchydata.com/developers/playground/psql-basics).

## Interacting programmatically with PostgreSQL databases using Psycopg

### Introduction

[Psycopg](https://www.psycopg.org/docs/) is one of the main PostgreSQL database
adapters for Python. You can install it with `pip` by running:

```
pip install psycopg2-binary
```

The package `psycopg2-binary` is a pre-compiled version of the module that does
not require the requirements described in the [installation
documentation](https://www.psycopg.org/docs/install.html), which makes it
easier to get started.

### Basic usage

We provide an overview of the basic usage described
[here](https://www.psycopg.org/docs/usage.html).

Psycopg's main entry point is the `connect()` function. It creates a new
database session and returns a `connection` object that can be used to open a
`cursor` object and perform SQL queries. Read more about the `connect()`
function [here](https://www.psycopg.org/docs/module.html#psycopg2.connect).

```
import psycopg2

con = psycopg2.connect(
    dbname="test",
    user="postgres",
    password="secret",
    host="localhost",
    port=5432,
)

cur = con.cursor()

cur.execute("SELECT * FROM users;")

data = cur.fetchall()

con.close()
```

### Execute commands

The `cursor` object supports the `execute()` and `executemany()` commands to
send commands to the database. `execute()` will run a single command, while
`executemany()` will run a command several times with a list of provided
command parameters.

```
cmd = "INSERT INTO users (id, name) VALUES (%s, %s);"

new_users = [(1, "Jaynee"), (2, "Jonathan")]

cur.executemany(cmd, new_users)
```

Read more about
[`execute()`](https://www.psycopg.org/docs/cursor.html#cursor.execute) and
[`executemany()`](https://www.psycopg.org/docs/cursor.html#cursor.executemany).

### Fetch query results

The `execute()` method returns `None` and results of individual queries
executed by `executemany()` are discarded. To fetch query results, call the
following functions:

* `fetchone()`: fetch the next row of results, or None when no data is
  available
* `fetchmany()`: fetch the next *set of rows* of results, you pass an integer
  to indicated the desired number of rows
* `fetchall()`: fetch all remaining rows of results, or an empty list when no
  data is available

```
cur.execute("SELECT * FROM users;")

first_user = cur.fetchone()

next_four = cur.fetchmany(4)

remaining_users = cur.fetchall()
```

Read more about fetching results in the
[documentation](https://www.psycopg.org/docs/cursor.html#cursor.fetchone).

### Commit or rollback transactions

Commands executed by a relational database are included in transactions, which
help provide ACID guarantees on the database.

After opening a connection to the database with `connect()`, the first time a
command is sent to the database, a new transaction is created. The following
database commands will be executed in the context of the same transaction, even
commands issued by different cursors of the same connection. A transaction is
terminated by calling either `commit()`, to make eventual changes persistent in the
database, or `rollback()`, to cancel changes.

If any command fails, the current transaction is aborted and no further command will
be executed until `rollback()` is called.

If the connection is closed while the transaction is in progress, the database
will discard the transaction.

It is possible to set the connection to `autocommit`, this will ensure that a
successful command has immediate effect in the database. Autocommit is also
useful to run commands such as `CREATE DATABASE`, which require to be run
outside any transaction.

```
con = psycopg2.connect(dbname="demo_db", user="admin")

con.autocommit = True

cur = con.cursor()

cur.execute("CREATE DATABASE human_resources;")

con.close()
```

Read more about transaction control in the
[documentation](https://www.psycopg.org/docs/connection.html#connection.commit).

### `with` statement

Connections and cursors are *context managers* and can be used with the `with`
statement to terminate a transaction automatically. If no exception has been
raised within the `with` block, the transaction is committed. Otherwise, the
transaction is rolled back.

```
with psycopg2.connect(dbname="demo_db", user="admin") as con:
    with con.cursor() as cur:
        cur.execute("SELECT * FROM users;")
        for row in cur:
            print(row)
```

However, the `with` statement will not close the connection once the block
exits. To do that, you can use a `try-finally` block.

```
con = psycopg2.connect(dbname="demo_db", user="admin")

cur = con.cursor()

try:
    cur.execute("INSERT INTO users (id, name) VALUES (1, 'Jaynee');")
    con.commit()
finally:
    con.close
```

### passing parameters to SQL queries

Passing parameters to a SQL statement happens in functions like `execute()` by
using `%s` placeholders in the SQL statement, and passing a sequence of values
as the second argument of the function.

```
cur.execute("INSERT INTO users (id, name) VALUES (%s, %s);", (1, "Jaynee"))
```

One can also use named arguments using the `%(name)s` placeholder. This is
useful to reuse arguments.

```
cur.execute("""
    INSERT INTO users (id, name, date)
    VALUES (%(id)s, %(name)s, %(date), %(date)s);
    """,
    {"id": 1, "name": "Jaynee", "date": datetime(2000, 1, 1)},
)
```

Using the `%s` only works for query parameters, not for things such as column
names or table names. For these use cases, you can use tools from the
[psycopg2.sql
module](https://www.psycopg.org/docs/sql.html#module-psycopg2.sql), which
provides tools for SQL string composition. 

```
from psycopg2.sql import Identifier, SQL

cur.execute(
    SQL("INSERT INTO {} VALUES (%s, %s);").format(Identifier("users")),
    (1, "Jaynee")
)
```

There is a lot more covered in the
[documentation](https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries).

### using `COPY TO` and `COPY FROM`

The Postgresql [COPY command](https://www.postgresql.org/docs/current/sql-copy.html) is an indispensable weapon in the arsenal of the data engineer. This allows moving data in and out of a database in bulk with a good performance.

The `cursor` object provides a high level interface to the PostgreSQL command
`COPY` through the following functions:

* `copy_from()`: reads data from a file-like object and append them to a table
* `copy_to()`: writes the contents of a table to a file-like object
* `copy_expert()`: allows to use specific `COPY` arguments which are not
  available in the other two functions

Let's load a file into a table:

```
with open("data.csv") as f:
    copy_from(f, table="users", sep=",", columns=("id", "name"))
```

Let's unload a table into a file (we do not specify column so all of them will
be exported).

```
with open("data.csv", "w") as f:
    copy_to(f, table="users", sep=",")
```

Read more about these functions in the
[documentation](https://www.psycopg.org/docs/cursor.html#cursor.copy_from).

## Interacting programmatically with the SQLite database

### SQLite

[SQLite](https://www.sqlite.org/about.html) is a relational database engine
with an open-source code. It is one of the most widely used databases.

Contrary to other databases such as PostgreSQL, SQLite does not have a server
process that you connect to using a client software. SQLite reads and writes
are made directly to disk files, so a complete database is contained within a
disk file.

### the `sqlite3` Python library


#### connect to a database

The library [`sqlite3`](https://docs.python.org/3/library/sqlite3.html) is
built in Python 3. `sqlite3` provides an inferface to connect to and run
queries on SQLite databases. It works very similarly to `psycopg2`.

You can connect to a database by calling the
[`connect()`](https://docs.python.org/3/library/sqlite3.html#sqlite3.connect)
function. This function operates in **autocommit mode by default**, this can be
changed by using the [`isolation_level`
parameter](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.isolation_level).

```
import sqlite3
con = sqlite3.connect("database.sq3")
```

You can create an in-memory database by running:

```
con = sqlite3.connect(":memory:")
```

#### execute basic queries

The `Cursor` method
[`execute()`](https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.execute)
will execute SQL commands.

```
con = sqlite3.connect(":memory:")
cur = con.cursor()

cur.execute("""
    CREATE TABLE stocks
    (date TEXT, action TEXT, ticker TEXT, quantity REAL, price REAL)""")

cur.execute("""
    INSERT INTO stocks
    VALUES ('2020-10-17', 'buy', 'BX', 100, 55.34)""")

con.commit()
con.close()
```

#### parameterize SQL queries

You can use the `?` placeholder when you want to parameterize a value in a
SQLite query, and provide a tuple of values as the second argument of the
cursor's `execute()` method:

```
ticker = ("BX",)
cur.execute("SELECT * FROM stocks WHERE ticker = ?", ticker)
print(cur.fetchone)
```

You can use the method
[`executemany()`](https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.executemany)
to execute several commands:

```
trades = [
    ("2020-10-17", "buy", "AAPL", 10, 119.02),
    ("2020-10-17", "buy", "BX", 20, 55.34),
    ("2020-10-17", "buy", "MSFT", 15, 219.66)
]
cur.executemany("INSERT INTO stocks VALUES (?, ?, ?, ?, ?)", trades)
```

#### reading data from the database

After executing a `SELECT` statement, you can use the `Cursor` as an iterator,
call the method `fetchone()` to get a single result, or call `fetchall()` to
get all results.

```
for row in cur.execute("SELECT * from stocks ORDER BY price DESC"):
    print(row)
```

## Exercises

### Exercise 1: the Facebook page-page network dataset

This dataset contains a graph of Facebook pages relationships. Nodes of the
graph are stored in the *targets* CSV file and and represent individual pages.
Edges of the graph are stored in the *edges* CSV file and represent page-page links.

You can download the dataset
[there](https://archive.ics.uci.edu/ml/datasets/Facebook+Large+Page-Page+Network).

The job is to load the dataset into a database of your choice (e.g. SQLite).
Then, you will query the dataset to join the two tables (nodes and edges) to
reconstitute the graph and filter the results containing a page of your choice
(e.g. "Joe Biden"). Also, order the pages linked to your page of choice by
alphabetical order. Save the results as a CSV file.
