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
