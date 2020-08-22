# Extract Transform Load Pipelines

## Overview

Extract Transform Load (ETL) pipelines are common data pipelines architectures.
They consist of three main steps during which data is first extract from a
source, eventually validated and transformed in order to be loaded into a
target data store (e.g. a relational database).

Here, we'll provide principles are concrete examples of the extract, transform
and load steps. We'll explore how to download data from the most common sources
(web servers, application programming interfaces, etc), how to validate and
transform data, and finally how to load and store it in the main types of data
stores and databases (AWS S3, relational databases, NoSQL database, etc).

We'll use the Python standard library as much as possible, and indicate popular
third party libraries which help build ETL pipelines more easily.

## ETL versus ELT

ELT stands for Extract Load Transform. This is a variation on the "traditional"
ETL pipeline where data is loaded as-is, before any transformation. Loading
data before any transformation has several advantages, including better
pipeline reproducibility. Indeed, storing the raw data before any
transformation will help re-running a data pipeline using the original data,
for example to fix a pipeline bug or failure. In many cases it may even be impossible to re-run a pipeline in the exact same conditions as originally, if the data source does not exist or is updated frequently. Depending on the loading target (database, object storage, etc), you may be restricted on where you can load data without any transformation.

Also, may end users would like to have access to raw data for exploratory
analyses, and make their own transformations, so loading raw data may be a
pipeline requirement.

Loading raw data is becoming easier with improvements on databases, which now
accept many data formats such as CSV, JSON (often returned by REST APIs),
Apache Parquet, etc. In any case, raw data should be stored in an object or
block storage before any transformation, to enforce reproducibility.
