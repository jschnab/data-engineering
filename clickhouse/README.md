# Clickhouse

## Overview

Clickhouse is a column-oriented online analytical processing (OLAP) database
optimized for real-time analytics.

Clickhouse was launched in 2012 and open-sourced in 2016, and is built with
C++.

## Concepts

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

## Schema design
