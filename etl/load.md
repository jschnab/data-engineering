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
