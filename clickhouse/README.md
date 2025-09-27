# Clickhouse

## Overview

Clickhouse is a column-oriented online analytical processing (OLAP) database
optimized for real-time analytics.

Clickhouse was launched in 2012 and open-sourced in 2016, and is built with
C++.

## Concepts

https://clickhouse.com/docs/managing-data/core-concepts

### Parts

When data is loaded into Clickhouse, records are grouped into **parts**. These
parts are analogous to segments in other databases such as Pinot or Druid, and
are immutable collections of sorted rows.

Physically, a part is a directory containing files storing column data, on
disk.

Ingested records that make up a part go through the following steps:
1. Sorting according to the table sort key (`ORDER BY` clause in the
    `CREATE TABLE` statement) and a sparse primary index is created based on
    the sort key.
2. Columns are split then compressed.
3. Part data is stored on disk.

A background job periodically merges parts into larger parts (up to a maximum
part size, 150 GB by default). After some time, old inactive parts that were
merged together are deleted. This hierarchical structure of merge parts gives
the name to the storage engine: MergeTree.

Parts can be queried:
```
SELECT _part FROM <table>
```

Conversely:
```
SELECT
    name
    , level
    , row
FROM system.parts
WHERE database = '<database>' AND table = '<table>' AND active
```

Parts follow the naming convention
`partition_min-block-number_max-block-number_level` where the partition is
defined by the table sorting key, and blocks are part subdivisions.

### Partitions

Partitions are defined by the `PARTITION BY` clause of a `CREATE TABLE`
statement, and help manage data.

When a table is partitioned, instead of creating a single part for a group of
rows, Clickhouse creates a part for each partition present in the rows. Also, a
min-max index is added for every part, containing the minimum and maximum value
of the partition columns for as specific part.

Care should be taken when selecting a partition key, because this could lead to
the creation of lots of partitions, which can result in a 'Too many parts'
error when inserting records. A partition key should have a cardinality between
1,000 and 10,000.

Parts are merged withing partitions, not across partitions.

Partitions are useful for:
* Data management: setting a `TTL` on a table allows to delete whole partitions
    to be deleted without rewriting parts.
* Query optimization: partition pruning and granule pruning allow to reduce the
    amount of scanned data. This is only useful if queries filter by the
    partition key. Queries not using the partition key can be slower due to
    the scanning of a larger number of parts.

### Part merges

Parts are hierarchically merged into larger parts. After each merge, a part
`level` is increased by 1 (starting at level 0 for unmerged parts)

Merging is a multi-threaded background process working in a loop:
1. Decide which parts to merge and load them into memory
2. Merge parts in memory into larger part
3. Write resulting part to dis'

Defering merges to an asynchronous background process makes inserts faster.

Not all parts to be merged are necessarily loaded into memory at once, the
merging process works on chunks of parts.

Merging steps:
1. Decompress and load column files into memory
2. Merging per se (preserving sorting order)
3. Generate a new primary index
4. Compress and save column files to disk

Replacing merges operate on a `ReplacingMergeTree` engine table, and keep the
most recent version of each row uniquely defined by the sorting key and the
creation timestamp of the part that contains the row.

In a `SummingMergeTree`, merges replace rows identified by the same sorting key
by a row with the same sorting key and a value equal to the sum of the old
rows. An `AggregatingMergeTree` can also be defined, with a column that has
`AggregateFunction` as type, leading to this specific function being applied
during merges to calculate the value of the new row.

Merges can be monitored using the `/merges` API endpoint.

### Table shards and replicas

This section does not apply to Clickhouse Cloud.

Data can be split across several servers in the form of table shards that make
up a distributed table.

A distributed table is creating by specifying the `Distributed` engine:
```
CREATE TABLE ...
ENGINE = Distributed('<cluster-name>', '<database>', '<table>', <sharding-key>)
```

Shards are replicated across servers for fault-tolerance and query performance
(different queries can run on different replicas in parallel).

### Primary indexes

The sparse primary index helps improve query performance by identifying
granules (logical blocks of 8,192 rows) that match query filters using sorting
key columns. Granules are the smallest unit of data that Clickhouse works with.

The sparse index contains one sorting key value per granule (the first row).
Since the index is small, it fits in memory and allows fast data filtering.

Primary indexes can be queried using the `mergeTreeIndex` table function.

The `EXPLAIN` query shows how the primary index is used (if it is).

### Architecture overview

Components:
* Query processing layer
* Storage layer
* Integration layer
* Access layer (manages user sessions)

Single C++ binary, statically-linked without dependencies.

Vectorized execution model and opportunistic query compilation.

Storage layer has several table engines categories:
1. `MergeTree` family, based on LSM trees. Each engine differs in the way the
   merge works.
2. Special-purpose table engines: in-memory key-value, in-memory temporary
   tables, `Distributed` table engine, etc.
3. Virtual engines for data exchange with external systems (relational
   databases, pub/sub systems, data lakes, object storage, etc.

Operation modes:
* on-premise
* cloud
* standalone (single server, kind of command line utility to transform files)
* in-process mode called chDB, has a Python API, kind of like DuckDB

## Updating data

Clickhouse is not optimized for row updates, and these operations need to be
designed carefully to avoid potential high I/O.

https://clickhouse.com/docs/updating-data

### Update mutation

```
ALTER TABLE <table-name> UPDATE ... WHERE ...
```

This is a heavy I/O operation that rewrites all parts that match the `WHERE`
clause, negatively affecting `SELECT` queries performance. Also, the update is
not atomic and queries can see data as is it being mutated, potentially leading
to inconsistent results.

The table `systems.mutations` shows update progress.

This is an operation that is useful when data should be updated immediately,
e.g. for compliance reasons.

The lack of atomicity of mutations can be addressed by setting the parameter
`apply_mutations_on_fly = 1`. The same high I/O concerns apply.

### Lightweight updates

```
UPDATE <table> SET .. WHERE ...
```

This create 'patch' parts containing only updated rows and columns, instead of
rewriting full parts. Patch parts are immediately visible to `SELECT` queries
and are stitched together with normal parts. This adds overhead to `SELECT`
queries, but avoid high I/O because parts are updated during the merge process.

### ReplacingMergeTree

This is the favorite way to update data. During parts merges, rows that have
the same sorting key are deduplicated and the most recent one is retained.
Merges happen at unknown times in the background, so data may remain duplicated
for some time. This is useful to save space, but does not guarantee the absence
of duplicates.

A cap on the de-duplication interval can be set with the parameter
`min_age_to_force_merge_seconds`, which forces merging of parts older than this
value.

`SELECT` queries can use the clause `FINAL` to force de-duplication at query
time.

There is also a `CollapsingMergeTree` engine but full rows need to be inserted
to perform an update. It's unclear which use cases this serves.

## Delete data

https://clickhouse.com/docs/managing-data/deleting-data/overview

Deleting data follows similar tradeoffs between consistency and performance
compared to updates.

Delete mutations are issued with `ALTER TABLE <table-name> DELETE ...`, and are
applied immediately but not atomically and negatively affect `SELECT` queries.

Lightweight deletions `DELETE FROM ...` are immediately visible but do not
modify physical data until the next merge. This works by adding a `_row_exists`
column to rows, which is used to filter deleted rows.

Truncating a table is performed with a `TRUNCATE TABLE` query, and is a
lightweight operation.

Partitions can be deleted with `ALTER TABLE DROP PARTITION ...` queries.

## Data modeling

https://clickhouse.com/docs/data-modeling/overview

### Schema design

Clickhouse is optimized for reading Parquet files and can read tens of millions
of records per second from Parquet files stored in S3.

#### Optimizing data types

Choosing the right data types allow Clickhouse to compress columns better,
leading to faster queries.

Avoid nullable columns because they create an additional column. E.g. for
numerical values use 0, for string an empty string, etc.

Use the smallest possible size for numeric types, as well as temporal types.

Use LowCardinality and FixedString types if possible.

Enums allow data validation at insert time, and allow to exploit natural
ordering of non-numeric values.

#### Ordering key

The ordering key is specified by the `ORDER BY` clause when creating a table,
and can be composed of several columns.

The ordering key is the primary key of the sparse index associated with a part,
and determine how rows are sorted within a part. This affects column
compression and therefore query speed (more compression = faster queries).

Guidelines to select ordering keys:
* 5 keys maximum is sufficient* 5 keys maximum is sufficient* 5 keys maximum is
    sufficient* 5 keys maximum is sufficient* 5 keys maximum is sufficient* 5
    keys maximum is sufficient* 5 keys maximum is sufficient* 5 keys maximum is
    sufficient* 5 keys maximum is sufficient
* should align with common query filters, so that more rows can be skipped
    during queries using these filters
* prefer columns that are correlated with other columns, in order to maximize
    compression of all columns
* organize key columns by order of increasing cardinality

### Dictionaries

Dictionaries are in-memory key-value representations of data optimized for low
query latency. They are useful for:
* remove the need for joins
* enrich data during ingestion (no need to do it at query time anymore)

A dictionary is created with the `CREATE DICTIONARY` query.

The `dictGet('<dict-name>', '<key-name>', <query-value>)` is used to query a
dictionary.

### Materialized views

Shift some cost of computation from query time to insert time. Can be
'incremental' or 'refreshable' (need to be periodically executed).

Incremental materialized views are not like in relational databases, they are
triggers that query data as it is inserted in a source table, then transform it
(or aggregate, filter, etc.) and insert it in a target table. This saves time
during queries, but increases ingestion latency. The target table is updated
in real time, without a need for periodic execution. 

Incremental materialized views are created with:
```
CREATE MATERIALIZED VIEW <view-name> TO <target-table> AS
<query-from-source-table>
```

The materialized view generally takes advantage of a particular table engine to
aggregate rows during asynchronous merges. Therefore recently inserted rows may
not be aggregated yet, an issue that can be solved using the `FINAL` clause in
the `SELECT` query, or by performing the usual aggregation in the `SELECT`
query.

Tip: for maximum performance, the `GROUP BY` clause should use keys from the
`ORDER BY` clause of the `CREATE TABLE` statement.

To avoid storing raw data, the table where rows are inserted can use the `Null`
engine. Inserted data will only populate the target table of the materialized
view.

Materialized views can use `JOIN`s, but the view will only be triggered when
the left-most table of the join is updated. Dictionaries may be preferrable to
joins for better performance.

Refreshable materialized views are another type of views that differs from
incremental materialized view on two aspects:
* they completely replace the target table with query results (unless `APPEND`
    is added to the view definition, in which case rows are appended to the
    table)
* they run on schedule (and can also be triggered manually)

The statement to create a refreshable materialized view is:
```
CREATE MATERIALIZED VIEW <view-name> REFRESH EVERY <time-value> <time-unit>
[APPEND] TO <target-table> AS
```

### Projections

Projections are a reordering of table rows, and therefore have a different
primary index. This helps speed up some queries that take advantage of this
new data ordering. Projections are automatically kept in sync with the original
table.

Compared to the original table, projections can have:
* a different primary index
* pre-computed aggregates

When a query is run, Clickhouse automatically selects the projection that will
read the least amount of data, and therefore yield the fastest query.

There is two ways to define a projection:
* store full columns (lots of additional storage but the fastest)
* store only a primary index with parts offsets, which is basically an index
    (least amount of data stored, but more I/O and slower queries)

Limitations:
* does not allow a different TTL than the original table
* lightweight updates and deletes are not supported
* projections cannot be chained like materialized views
* projections cannot be joined
* projections do not support `WHERE` clauses

Statement to create a projection:
```
ALTER TABLE <table-name>
ADD PROJECTION <projection-name>
(
    SELECT *
    ORDER BY <sorting-key-columns>
    [GROUP BY ...]
)
```

If there is an aggregation in the projection, then the projection table storage
uses the `AggregatingMergeTree` engine.

Then one must materialize the projection:
```
ALTER TABLE <table-name> MATERIALIZE PROJECTION <projection-name>
```

A projection based on part offsets is created like this:
```
CREATE TABLE <table-name> (
    PROJECTION <projection-name>
        (
            SELECT _part_offset ORDER BY <sorting-key-columns>
        ),
        ...
)
ENGINE = ...
```

Projections VS materialized views:
* projections update asynchronously, (incremental) materialized views update
    synchronously
* projections are queried transparently when a user queries the source table,
    materialized views are explicitly queried
* projections are not compatible with deletes (unless the parameter
    `lightweight_mutation_projection_mode` is used), and materialized views do
    not react to deletes or updates (only to inserts)
* projections cannot be defined using joins, while materialized views can (only
    the leftmost part of the join triggers a materialization)
* projections cannot be defined with `WHERE` clauses, materialized views can
* projections cannot be chained, while materialized views can
* projections are only available for merge tree engines, while materialized
    views are compatible with a broad list of table engines
* for projections insert failures do not lead to data loss, while a
    materialized view insert failure leads to target table data loss
* projections have lower operational burden
* projections do not work with `FINAL` queries, while materialized views do

### Compression

Algorithms used for column compression can be controlled when a table is
created:
```
CREATE TABLE <table-name> (
    <column-name> CODEC(<algo-1>, ...)
    ...
)
...
```

E.g. `ZSTD` works well in most cases, `Delta` works well for monotonically
increasing values. These can be combined, and `ZSTD` compresses well data
already compressed with `Delta`.

## Advanced features

https://clickhouse.com/docs/guides/developer/overview

### Dynamic column selection

Can select columns based on regular expression, and exclude some of them:
```
FROM <table>
SELECT COLUMNS('<regex-1>') [COLUMNS('<regex-2>'), ...] EXCEPT(<col-1)
```


Can apply functions on all columns, e.g. `max`, `avg`, etc. and functions can
be chained:
```
FROM <table>
SELECT COLUMNS('<regex>') APPLY(<func-1>) [APPLY(<func-2>), ...]
```

Can adjust some columns and leave the other untouched:
```
FROM <table>
SELECT
    COLUMNS('<regex>')
    REPLACE(
        <col-1> * 2 AS <col-1>
        , <col-2> / 1.5 AS <col-2>
    )
APPLY(<func-1>)
```

### Merge tables

A merge table does not store data but allows to query from multiple tables
simultaneously by taking a union of table columns and deriving common types
(for columns that have different types).

```
SELECT <cols>
FROM merge(['db_name',] 'tables_regexp')
```

### Query dialects

`clickhouse` is the default query dialect, but we can also use Pipeline
Relational Query Language ([PRQL](https://prql-lang.org/)) or
[Kusto](https://learn.microsoft.com/en-us/kusto/query/?view=azure-data-explorer&preserve-view=true).

```
SET prql
SET kusto
```

### Cascading materialized views


