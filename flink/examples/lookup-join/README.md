# MariaDB setup

## Docker

Run a Mariadb Docker container:

```bash
docker run --detach --name mariadb --env MARIADB_ROOT_PASSWORD=<your-password-here> mariadb:11.4
```

Create the necessary objects:

```sql
create database customerdb;
use customerdb;

create table customers (
    id serial primary key
    , name varchar(255)
    , country varchar(255)
    , zip varchar(255)
);

insert into customers (name, country, zip)
values ('Alice', 'USA', '10154')
    , ('Bob', 'France', '75007')
    , ('Charlie', 'UK', 'CBX11TU');
```

## Flink

Download the following JARs and place them in the `lib` folder of your Flink
installation, then restart Flink:

* [JDBC
    connector](https://repo.maven.apache.org/maven2/org/apache/flink/flink-connector-jdbc-core/4.0.0-2.0/flink-connector-jdbc-core-4.0.0-2.0.jar)
* [MySQL
    connector](https://repo.maven.apache.org/maven2/org/apache/flink/flink-connector-jdbc-mysql/4.0.0-2.0/flink-connector-jdbc-mysql-4.0.0-2.0.jar)
* [MySQL
    driver](https://repo.maven.apache.org/maven2/mysql/mysql-connector-java/8.0.30/mysql-connector-java-8.0.30.jar)
