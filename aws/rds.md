# AWS Relational Database Service (RDS)

## Introduction

AWS RDS is a service which facilitates the provisioning and management of
[relational databases](https://en.wikipedia.org/wiki/Relational_database) in the cloud.

RDS provides a range of database *backends* (database engines provided by
different companies or free and open source initiatives):

* SQL Server (proprietary, Microsoft)
* MySQL (open source or prioprietary, Oracle Corp.)
* Oracle (proprietary, Oracle Corp.)
* Aurora (proprietary, AWS)
* MariaDB (open source, community-supported fork of MySQL)
* PostgreSQL (open source)

## RDS features

### Delegate database administration to AWS

When you setup and RDS database, AWS will manage the following actions for you:

* provision infrastructure (e.g. servers)
* install the database software
* data backups
* software updates
* data replication (if multi-AZ is used, see below)

You retain control of:

* database settings
* management of tables, users, and relational schemas

In a nutshell, RDS allows you to focus on the the application and data logic,
while delegating most of database administration to AWS.

###  Online Transactional Processing (OLTP)

Relational databases are well-suited for **Online Transactional Processing** (OLTP)
workloads. OLTP typically involved inserting, updating, and deleting small
volumes of data in a database. Usually, OLTP involves a single record, or a
small number of records.

For example, when registering to a website or subscribing to a newsletter, the
website will insert a row in a database containing your name, your email, your
password, and other user details. A user may later update his personal details,
in this case the website application will update the row corresponding to this
user in the database. Eventually, a user will unsubscribe and the website will
then delete the user from the database. These actions are typical of OLTP.

OLTP is often discussed in contrast to Online Analytical Processing (OLAP).
OLAP is typically used to perform business intelligence, i.e. analysts query
large amounts of information, often joining multiple databases, to aggregate
data and generate high level metrics (average, sum, etc) which support business
management. OLAP may use the same data as OLTP, but OLAP typically involves a
larger volume of data, and much more complex SQL queries.

### ACID transactions

ACID is a set of properties of database transactions that guarantee data
validity despite errors, power failures, and other problems. ACID stands for:

* Atomicity: transactions succeed completely or fail completely. If a single
  statement in a transaction fails, the whole transaction fails and the
  database is left unchanged.
* Consistency: transactions can only bring the database from one valid state to
  another valid state, preventing data corruption by invalid transactions.
* Isolation: concurrent transactions leave the database in the same state as
  sequential transaction, through locking mechanisms. The order in which
  transactions are made is irrelevant and leads to the same results in the
  database.
* Durability: committed transactions are premanent on the database, regardless
  of external errors (loss of power, etc).

### Multi-AZ

Multi-AZ deployments means that RDS will automatically provision and maintain a
standby database replica in a different availibility zone (AZ). Data updates to the
database are synchronously replicated across AZs to protect data in the even of
a database failure. This is useful to establish a *disaster recovery* plan. In
the event of database or AZ failure, RDS will *fail over* to the standby
instance to maintain data access.

### Read replicas

Read replicas rely on a database engine's built-in replication functionality to
asynchronously replicate data across several database instances. This is useful
to ease heavy read traffic on a database, by distributing read traffic amongst
replicas, and improve performance of read-heavy workloads.

## Creating and connecting to your own database instance

Follow [this tutorial](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_GettingStarted.CreatingConnecting.PostgreSQL.html) to create a PostgreSQL database instance and connect to it.
