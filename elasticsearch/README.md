# Elasticsearch

Check
[notebooks](https://github.com/elastic/elasticsearch-labs/tree/main/notebooks).

## Architecture

### Nodes

Node types:
* master
* data
* coordinator (all)
* machine learning
* ingest

### Indexing

Words stored in inverted indexes that map word to documents that contain them.

Relevancy algorithm is Best Match 25 (BM25) by default:
* term frequency / inverse document frequency
* document is more relevant if it has more occurrence of a word
* term more relevant if fewer documents contain it
* non-linear function for term frequency to normalize repetitive terms
* normalization for document length (could have higher term frequency)

Stop words (a, if, but, and, etc.) are not filtered by default during indexing.

We can choose the similarity algorithm for each document fields. When creating
the index, specify `mappings`:
```
{
    "mappings": {
        "properties": {
            "<field-1-name>": {
                "type": "text",
                "similarity": "BM25"
            },
            "<field-name-2>: {
                "type: "text",
                "similarity": "boolean"
            }
        }
    }
}
```

BM25 parameters:
* `k1`: non-linear term frequency saturation variable
* `b`: term frequency normalization factor based on document length

These parameters can be changed by passing them to settings when creating the
index:
```
{
    "settings": {
        "index": {
            "similarity": {
                "custom_bm25": {
                    "type": "BM25",
                    "k1": 1.1,
                    "b": 0.85
                }
            }
        }
    }
}

```

## Lucene query syntax

Query specific fields:
```
title:data
```

Query exact sentence (double quotes):
```
"hello, world"
```

Fuzziness (number of characters that can change, with Levenshtein distance):
```
cat~1
```

Slop (number of word permutations, absence/presence, etc.):
```
"great influence"~2
```

## Query DSL

Match field:
```
{
  "query": {
    "match": {
      "title": "data"
    }
  }
}
```

Match prefix:
```
{
  "query": {
    "prefix": {
      "author": "josh"
    }
  }
}
```

Match with operator:
```
{
  "query": {
    "match": {
      "title": {
        "query": "data engineering",
        "operator": "AND"
      }
    }
  }
}
```

Match multiple fields:
```
{
  "query": {
    "multi_match": {
        "query": "data engineering",
        "fields": ["title^3", "body"]
    }
  }
}
```

Match phrase:
```
{
  "query": {
    "match_phrase": {
      "body": "when you manage people"
    }
  }
}
```

Highlight fields that match in results:
```
{
  "highlight": {
    "fields": {
      "title": {},
      "body": {},
    }
  }
}
```

Boolean query (each of `must`, `must_not`, etc. has a list of queries such as
`match`, `match_phrase`, etc.):
```
{
  "query": {
    "bool": {
      "must": [{ }],
      "must_not": [{ }],
      "should": [{ }],
      "filter": [{ }]
    }
  }
}
```

## Working with documents

### Indexing documents

Various API endpoints exist:
* `PUT <index>/_doc/<id>`: Index a document with an identifier. If the document
    already exists, it is updated and the `_version` attribute is incremented.
    Corresponds to the
    [index()](https://elasticsearch-py.readthedocs.io/en/v9.0.3/api/elasticsearch.html#elasticsearch.Elasticsearch.index)
    method of the Python client.
* `POST <index>/_doc/[<id>]`: Index a document with or without an identifier.
    If the identifier is not provided, it is automatically assigned. If the
    document already exists, it is updated. Corresponds to the
    [index()](https://elasticsearch-py.readthedocs.io/en/v9.0.3/api/elasticsearch.html#elasticsearch.Elasticsearch.index)
    method of the Python client.
* `PUT <index>/_create/<id>`. Index a document with an identifier. If the
    document already exists, the operation fails and a 409 (conflict) error is
    returned. Corresponds to the
    [create()](https://elasticsearch-py.readthedocs.io/en/v9.0.3/api/elasticsearch.html#elasticsearch.Elasticsearch.create)
    method of the Python client.

If the target index does not exist, it is created unless the cluster settings
attribute `action.auto_create_index` is `false`.

A document is not searchable before a refresh has occured and the document is
included in data segments. A refresh occurs
every second by default but can be controlled:
* On the server side with the cluster settings attribute
    `index.refresh_interval`.
* On the client side, the request parameter `refresh` (boolean or `wait_for`)
    controls if indexing should be immediately followed by a refresh, or if the
    request should return a response once an automatic refresh has occured.

### Retrieving documents

`GET <index>/_doc/<id>` retrieves the document with the requested identifier.
The boolean response field `found` indicates if the document was found or not.
The response field `_source` contains the document. Corresponds to the
[get()](https://elasticsearch-py.readthedocs.io/en/v9.0.3/api/elasticsearch.html#elasticsearch.Elasticsearch.get)
method of the Python client.

`HEAD <index>/_doc/<id>` determines if the document exists in the index or not.
Corresponds to the
[exists()](https://elasticsearch-py.readthedocs.io/en/v9.0.3/api/elasticsearch.html#elasticsearch.Elasticsearch.exists)
of the Python client (returns 200 if found, else 404).

`GET [<index>/]_mget` retrieves multiple documents with a list of identifiers or
documents. If documents are in the same index, provide the index a the list of
identifiers in the request body. If documents are in different indexes, omit
the index name and provide a list of documents in the request body:
`[{"_index": "zorglub", "_id": 1}, ...]`. Corresponds to the
[mget()](https://elasticsearch-py.readthedocs.io/en/v9.0.3/api/elasticsearch.html#elasticsearch.Elasticsearch.mget)
method of the Python client.

Documents can also be retrieved by identifier with a `GET <index>/_search`
request, if the request body is structured as `{"query": {"ids": {"values": [...]}}}`.

The request parameters `_source` (boolean), `_source_includes` and
`_source_excludes` (both comma-separated value strings) control if and what
document data is retrieved. Field prefixes can be specified with an asterisk,
e.g. `_source_includes=prefix*`.

### Updating documents

Segments are immutable, so Elasticsearch performs updates by reading the
document, modifying it, then storing the modified document. The API endpoint to
perform udpates is `POST <index>/_update/<id>`, corresponds to the
[update()](https://elasticsearch-py.readthedocs.io/en/v9.0.3/api/elasticsearch.html#elasticsearch.Elasticsearch.update)
method of the Python client.

The endpoints used for document indexing can also update a document, but do not
work with partial documents, the full document needs to be provided.

To add fields, pass a partial document with new fields in the request body. To
update an existing field, pass the new field value in the request body. To
update arrays, the full array with existing and new elements must be provided.

Scripts can be used to update documents, e.g.:
```
POST test/_update/1
{
  "script" : {
    "source": "ctx._source.counter += params.count",
    "lang": "painless",
    "params" : {
      "count" : 4
    }
  }
}
```

The request `POST <index>/_update_by_query` allows to provide both a query and
a script to perform updates. If not query is provided, all documents are
updated. If a document changed between the time Elasticsearch received the
request and it performs the update, the update for this document fails.

### Deleting documents

By identifier: `DELETE <index>/_doc/<id>`. The response includes
`"result": "deleted"` and `_version` is incremented if the operation is
successful.

By script with a query following the same syntax as search queries: `POST <index>/_delete_by_query`.

### Bulk operations

The body of the request has two lines per document, the first line indicates
the operation and the second line the document contents, following [new
line-delimited JSON](https://ndjson.org) syntax.
```
POST _bulk
{ "index" : { "_index" : "test", "_id" : "1" } }
{ "field1" : "value1" }
...
```

With the Python client:
```python
resp = client.bulk(
    operations=[
        {
            "index": {
                "_index": "test",
                "_id": "1"
            }
        },
        {
            "field1": "value1"
        },
        {
            "delete": {
                "_index": "test",
                "_id": "2"
            }
        },
        {
            "create": {
                "_index": "test",
                "_id": "3"
            }
        },
        {
            "field1": "value3"
        },
        ...
    ]
)
```

### Reindexing

Reindexing copies documents from a source index to a target index (e.g. with a
different schema).

```
POST _reindex
{
  "source": {
    "index": ["my-index-000001", "my-index-000002"]
  },
  "dest": {
    "index": "my-new-index-000002"
  }
}
```

Reindexing should be performed on a green cluster to avoid potential failures.

## Index operations

### Creating indexes

Indexes are created automatically if the cluster setting
`action.auto_create_index` is `true` (default) and a document is created on a
non-existent index. Default index settings and mappings are used. Disabling
automatic index creation can affect tools like Kibana, which create
house-keeping indexes. Automatic index creation can be enabled for some index
prefixes, e.g. `action.auto_create_index: [".*"]` allows indexes prefixed with
a dot.

When creating indexes, the following configuration can be specified:
* Mappings: document field names and types.
* Settings: number of shards, replicas, compression, etc. Static settings can
    only be specified during creation (e.g. number of shards), while dynamic
    settings can be changed on live indexes (e.g. number of replicas, refresh
    interval, etc.).
* Aliases: alternative names that can be used to refer to the index.

Indexes are created explicitly using the [PUT
<index>](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-indices-create)
API endpoint. Corresponds to the
[indices.create()](https://elasticsearch-py.readthedocs.io/en/latest/api/indices.html#elasticsearch.client.IndicesClient.create)
Python client method.

Dynamic settings can be updated using the `PUT <index>/_settings` endpoint.
Corresponds to the
[indices.put_settings()](https://elasticsearch-py.readthedocs.io/en/latest/api/indices.html#elasticsearch.client.IndicesClient.put_settings)
method on the Python client.

The number of shards is a static setting because this affect document routing.
Changing the number of shards can be achieved via reindexing to a destination
index with the desired number of shards.

Retrieve settings with the `GET <index>/_settings` endpoint.

Mappings can be specified using the following syntax:
```
{
    "mappings": {
        "properties": {
            "<field-name-1": {
                "type": "field-name-1-type",
            },
            "<field-name-2": {
                "properties": {
                    ...
                }
            }
        }
    }
}
```

Fields with properties implictly specific an `object` type.

Aliases allow zero-downtime reindexing, as the alias can point to the new index
when it is ready. Aliases can be specified during index creation as:
```
{
    "aliases": {
        "<index-alias>: {}
    }
}
```

The API endpoint `PUT|POST <index>/_alias/<name>` can also be used to create of
update aliases. The index name can be comma-separate index names, or contain a
wildcard.

If an alias points at several indexes, one must be flagged as the write index
using the `"is_write_index": true` option.

Steps for zero-downtime reindexing:
1. Create alias for existing index.
2. Create new index with desired configuration.
3. Reindex documents from existing to new index.
4. Update alias to point to new index.
5. Delete old index.

### Reading indexes

Use the following endpoints:
* `GET <index>`
* `GET <index>/_settings`
* `GET <index>/_mappings`
* `GET <index>/_aliase`
* `HEAD <index>` to determine if it exists

Hidden indexes are prefixed with a dot, e.g. `.admin`. A query to `GET _all`
will return them.

### Deleting indexes

Endpoint `DELETE <index>`.

### Opening and closing indexes

A closed index does not allow read or write operations. Also, memory allocated
for data structures used for search is reclaimed, resulting in lower cluster
overhead. Close an index with `POST <index>/_close`.

To open an index, query `POST <index>/_open`.

### Index templates

Index templates allow to reuse index configuration.

Two types:
* composable (indexing) templates, made of zero or more components, can exist on their own
* component templates, used to build composable templates

Create indexing templates:
```
PUT _index_template/<name>
{
    "index_patterns": [...],
    "priority": 1,
    "template": {
        "mappings": {},
        "settings": {},
        "aliases": {},
        "lifecycle": {}
    },
    "composed_of": [...]
}
```

Priority defines which template should be used when several match. Highest
priority wins.

Create component templates:
```
PUT _component_template/<name>
{
    "template": {
        ...
    }
}
```

### Monitoring indexes

Index statistics `GET <index>/_stats`. Response `_all` block has stats for all
indices.

Segment statistics `GET <index>/_stats/_segments`.

### Advanced operations

#### Splitting an index

Splitting an index increases the number of shards, useful to increase index
parallelism and keep index configuration.

Steps:
1. Make index read-only by applying setting `index.blocks.write: true`
2. Make split request:
    ```
    POST <source-index>/_split/<target-index>
    {
        "settings": {
            "index.number_of_shards": <n>
        }
    }
    ```

Target index must not exist. New number of shards must be multiple of old
number of shards.

#### Shrink index

Pre-requisites:
* Index must be read-only
* A copy of all shards must be on the same node

```
PUT <index>/_settings
{
    "settings": {
        "index.blocks.write": true,
        "index.routing.allocation.require._name": "<node-name>"
    }
}
```

Shrink the index:
```
PUT <source-index>/_shrink/<target-index>
{
    "settings": {
        "index.blocks.write": null,
        "index.routing.allocation.require._name": null,
        "index.number_of_shards": <n>
    }
}
```

The source number of shards must be a multiple of the target.

#### Rollover an index

Rollover creates a new blank index that is used to write new documents.

Steps:
1. Alias is created on old index:
    ```
    POST _aliases
    {
        "actions": [
            {
                "add": {
                    "index": "<old-index-name>",
                    "alias": "<alias-name>",
                    "is_write_index": true
                }
            }
        ]
    }
    ```
2. Issue rollover request: `POST <alias-name>/_rollover/[<target-index>]`.

The rollover operation will automatically create the new index and remap the
alias to point to it.

If the old index name is suffixed with a number and the target index is not
provided in the request, the new index will have an incremented number, with
6 digits and zero-padded.

#### Index lifecycle management

Index lifecycle management (ILM) can automate rollovers, e.g. writing new logs
to a new index for the day.

We can create an ILM policy and attach it to indexes:
1. Define a policy with `PUT _ilm/policy/<policy-name>`.
2. Create an index with a policy:
    ```
    PUT <index-name>
    {
        "settings": {
            "index.lifecycle.name": "<policy-name>"
        }
    }
    ```

Policies are scanned every 10 minutes by default, can be adjusted with cluster
setting `indices.lifecycle.poll_interval`.

## Text analysis

### Analyzer components

Text is analyzed during indexing and searching (when a query is processed).

Analsysis = tokenization + normalization (token processing such as stemming,
synonyms, removal of irrelevant tokens such as stop words).

API endpoint to test text analysis is 
[GET \_analyze](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-indices-analyze):
```
GET _analyze
{
    "tokenizer": ...,
    "filter": [...],
    "text": ...
}
```

Analysis steps:
1. Character filtering (0 or more filters, e.g. HTML tag filtering)
2. Tokenization (1 mandatory tokenizer)
3. Token filters (0 or more filters, e.g. stop words)

### Built-in analyzers

Standard analyzer has:
* no character filter
* standard tokenizer (grammar-based tokenization, splits at whitespace and
    removes punctuation)
* lowercase token filter

Enable the english stopwords filter on an index analyzer:
```
PUT _index/<index-name>
{
    "settings": {
        "analysis": {
            "analyzer": {
                "standard_with_english_stopwords": {
                    "type": "standard",
                    "stopwords": "_english_",
                }
            }
        }
    }
}
```

Custom stopwords can be stored in a file (put the file in the `config` folder,
one word per line):
```
"analyzer": {
    "standard_with_english_stopwords": {
        "type": "standard",
        "stopwords_path": "custom_stopwords.txt"
    }
}
```

Keyword analyzer:
* no character or token filters
* no-op tokenizer (text is stored as-is)

Fingerprint analyzer:
* no character filter
* standard tokenizer
* token filters: lowercase, ASCII folding (convert all to ASCII), stopwords,
    fingerprint (remove duplicates and store words in sorted order, as a single
    token)

Pattern analyzer uses pattern tokenizer, which uses a regular expression to
split text into tokens.

Language analyzers can tokenize most common languages.

### Custom analyzers

Specify custom analyzer when creating an index:
```
PUT _index/<index-name>
{
    "settings": {
        "analysis": {
            "analyzer": {
                "my_custom_analyzer": {
                    "type": "custom",
                    "char_filter": ["html_strip"],
                    "tokenizer": "standard",
                    "filter": ["lowercase", "stop"]
                }
            },
            "filter": {
                "stop": {
                  "type": "stop",
                  "stopwords": "_english_"
                }
            }
        }
    },
}
```

### Specifying analyzers

Index-level analyzers, specify in the analysis attribute when creating an index
(what most previous examples showed).

Field-level analyzers: specify analyzer in mappings when creating an index.

Query-level analyzers:
* specify as part of the query
* specify during index creation as part of mappings, as `search_analyzer`

Analyzer precedence (from highest to lowest):
1. Query
2. `search_analyzer` index mappings
3. Index

### Character filters

Used to remove, add, or replace characters in the text.

#### HTML strip

Removes HTML tags.

Can specify tags to keep, by specifying a list of `escaped_tags` in a custom
character filter.

#### Mapping characters

Replace characters by using a key-value definition. Characters not specified in
the mapping definition are left untouched.

Mappings can be specified in a file, provide the path in `mappings_path` and
use the following format: one entry per line, `key=>value`.

#### Pattern-replace

Replace characters based on a regular expression. Specify the fields `pattern`
and `replace` in a custom character filter.

### Tokenizers

Standard tokenizer is grammar-based: split text based on word boundaries and
punctuation.

#### N-gram and edge N-gram

N-grams are sequences of a given size prepared given a word. 2-grams for coffee
are: co, of, ff, fe, ee.

Edge N-grams are anchored at the beginning of a word. For coffee: c, co, cof,
coff, coffe, coffee.

Configuration (not exhaustive) for `ngram` and `edge_ngram` tokenizers:
* `min_char`: minimum number of characters
* `max_char`: maximum number of characters
* `token_chars`: list of character classes (letter, digit, etc.) that should be
    included in a token (default [] to include all)

#### Other tokenizers

Keyword, pattern, path hierarchy, etc.

### Token filters

50 token filters available.

Synonyms, word stems, etc.

## Search

![Search request processing](search.png)

### Search fundamentals

Two ways to query search endpoint:
* URI request: `GET <index>/_search?q=title:godfather`
* domain-specific language (DSL):
  ```
  GET movies/_search
  {
    "query": {
      "match": {
        "title": "godfather"
      }
    }
  }
  ```

Search context:
* Query: Calculates a relevance score, important for results ranking. See DSL
    query above for an example.
* Filter: Does not calculate relevance score, binary filtering of results,
    either a document matches or it does not, faster results when ranking is
    not critical. Filters are cached, leading to more efficient queries.

Example filter context query:
```
GET <index>/_search
{
    "query": {
        "bool": {
            "filter": [
                "match": {
                    "title": "godfather"
                }
            ]
        }
    }
}
```

`bool` query is a compound query with several possible clauses: `must`,
`must_not`, `should`, `filter`.

`aggs` queries perform aggregations, e.g.:
```
GET movies/_search
{
  "size": 0, 
  "aggs": {
    "average_movie_rating": {
      "avg": {
        "field": "rating"
      }
    }
  }
}
```

Set `size` to 0 to avoid returning hits, since we are only interested in the
aggregate value.

### Anatomy of a response

Response attributes:
* `took`: Time in milliseconds for the search to complete (excluding HTTP
    request/response overhead time).
* `hits.hits`: Array of search results.

### Query DSL

Query structure:
```
GET <index>/_search
{
    "query": {
        <query-type>": {
            ...
        }
    }
}
```

### Leaf and compound queries

Leaf queries look for a particular value in a particular field.

Compound queries wrap leaf queries or other compound queries to compbine
several searches in a logical fashion (e.g. `bool` query).

### Search features

### Pagination

Set page size with `size` parameter, and the starting result page with `from`:
```
GET <index>/_search
{
  "size": 20,
  "from": 20,
  "query": {
    ...
  }
}
```

This will fetch result items between 20 and 40 (i.e. the second page of
results).

### Highlight

Highlight the search query:
```
GET movies/_search
{
  "_source": false,
  "query": {
    "term": {
      "title": {
        "value": "godfather"
      }
    }
  },
  "highlight": {
    "fields": {
      "title": {}
    },
    "pre_tags": "{{",
    "post_tags": "}}",
  }
}
```

By default, highlight tags are HTML `<em>` tags. Specify custom tags with
`pre_tags` and `post_tags`.

### Explain

Explain how the relevancy score was calculated:
```
GET <index>/_search
{
  "explain": true,
  "query": {
    ...
  }
}
```

Results are explained in the `_explanation` field.

Or use the `_explain` API:
```
GET <index>/_explain/<doc-id>
{
    "query": {
        ...
    }
}
```

### Sort

By default, results are sorted by descending order of relevance score.

We can sort results using different criteria with the `sort` attribute:
```
GET <index>/_search
{
  "query": {
    ...
  },
  "sort": [
    {
      "<field-name>": {
        "order": "desc"
      }
    }
  ]
}
```

We can sort according to multiple fields by adding fields to the `sort` list,
subsequent fields are used to break ties.

### Manipulating results

Suppress documents and just return metadata (document ID, score, highlights,
etc.):
```
GET <index>/_search
{
    "_source": false,
    "query": {
        ...
    }
}
```

Fetching selected fields (which are returned as an array):
```
GET <index>/_search
{
    "_source": false,
    "query": {...}
    "fields": [<field-name-1, <field-name-2, ...],
}
```

Scripting results (results `fields` attribute will contain the field
`top_rated_movie`):
```
GET <index>/_search
{
  "query": {...},
  "script_fields": {
    "top_rated_movie": {
      "script": {
        "lang": "painless",
        "source": "if (doc['rating'].value > 9.0) 'true'; else 'false'"
      }
    }
  }
}
```

Filter document fields:
```
{
    "query": {...},
    "_source": [...]
    }
```

Or:
```
{
    "query": {...},
    "_source": {
        "includes": [...],
        "excludes": [...]
    }
}
```

Searching across indexes, and boost certain indexes:
```
GET _search
{
    "indices_boost": [
        {<index-1>: <float>},
        {<index-2>: <float>},
        ...
    ],
    "query": {...}
}
```

## Term searches

### Overview of term-level search

Term search is suitable when searching for exact matches, usually structured
fields such as dates, booleans, ranges, keywords, etc.

Matching documents have a relevance score by default, but it does not matter
and we can use constant scoring for efficiency (save computation cost, and
cache query).

Term searches are not analyzed (no tokenization or normalization like
lower-casing), so they produce results only for exact matches, and are
therefore not a great fit for text fields.

Query example, where the `certification` field is of type `keyword`:
```
GET <index>/_search
{
    "query": {
        "term": {
            "certification": "R",
        }
    }
}
```

### `terms` query

Query multiple values with `terms` query (array can contain up to 65,536
elements, can be modified with index setting `max_terms_count`):
```
GET <index>/_search
{
    "query": {
        "terms": {
            "certification": ["R", "PG-13"]
        }
    }
}
```

Term lookup search (get search value from a specific document):
```
GET <index>/_search
{
    "query": {
        "terms": {
            <field-to-search>: {
                {
                    "index": <index-to-get-value-from>,
                    "id": <document-id>,
                    "path": <field-path>
                }
            }
        }
    }
}
```

### `ids` query

Fetch documents with the specified identifiers:
```
GET <index>/_search
{
    "query": {
        "ids": {
            "values": [...]
        }
    }
}
```

Equivalent to:
```
GET <index>/_search
{
    "query": {
        "terms": {
            "_id": [...]
        }
    }
}
```

### `exists` query

Return documents that have a specific field:
```
GET <index>/_search
{
    "query": {
        "exists": {
            "field": <field-name>
        }
    }
}
```

Can also be used as a negative filter (e.g. documents that do not contain a
specific field):
```
GET <index>/_search
{
    "query": {
        "bool": {
            "must_not": [
                {
                    "exists: {
                        "field": <field-name>
                    }
                }
            ]
        }
    }
}
```

### `range` query

Find documents where a specific field is between a lower bound `gte`
(inclusive) and an upper bound `lte` (inclusive):

```
GET <index>/_search
{
  "query": {
    "range": {
      "<field-name>": {
        "gte": 9.0,
        "lte": 9.5
      }
    }
  }
}
```

Exclusive operators `gt` and `lt`.

Can filter numerical fields, dates, etc.

Relative date filtering (date minus 2 days):
```
"range": {
    "release_date": {
        "lte": "22-05-2023||-2d"
    }
}
```

Relative date filtering (for the past year):
```
"range": {
    "release_date": {
        "gte": now-1y"
    }
}
```

### Wildcard queries

Types of wildcards:
* `*`: zero or more characters
* `?`: a single character

```
GET <index>/_search
{
  "query": {
    "wildcard": {
      "<field>": {
        "value": "<prefix>*"
      }
    }
  }
}
```

Wildcard queries are expensive, they put a higher load on nodes than other
types of queries. Range queries are expensive as well. Expensive queries can be
disabled with the cluster setting `search.allow_expensive_queries` set to
`false`.

### Prefix queries

```
GET <index>/_search
{
  "query": {
    "prefix": {
      <field-name>: {
        "value": <prefix>
      }
    }
  }
}
```

Prefix queries are expensive.

Prefix queries can be sped up by flagging fields that will be subject to such
queries in mappings. Elasticsearch will build prefixes when indexing documents.

```
{
  "mappings": {
    "properties": {
      "<field-name>":{
        "type": "text",
        "index_prefixes":{
            "min_chars": 4,
            "max_chars": 10
        }
      }
    }
  }
}
```

`min_chars` is 2 by default and `max_chars` is 5 by default.

### `fuzzy` queries

Deal with spelling mistakes. Fuzziness is defined by Levenshtein distance (aka
edit distance). A fuzziness of 1 will find words that differ by 1 character
from the query value.

```
GET <index>/_search
{
  "query": {
    "fuzzy": {
      "<field-name>": {
        "value": "...",
        "fuzziness": 1
      }
    }
  }
}
```

Fuzziness is applied by default, depending on word length:
* 0 to 2: fuzziness = 0
* 3 to 5:  fuzziness = 1
* greater than 5: fuzziness of 2

## Gotchas

When using the asynchronous client, the count of indexed documents may not be
updated immediately after a new index request is sent.

During dynamic field mapping (i.e. index mappings are not defined explicitly),
`keyword` fields will be added for all fields except if they are too long. This
is unnecessary, so explicit mappings should be defined.

After index mappings have been defined, fields cannot be deleted from the
mappings definition, they can only be added.

When a document is indexed, nested arrays are flattened and array elements lose
their relationship and can lead to bad search results. Use `nested` data type
instead of `object` in this case. For example, this document:
```
{
  "users" : [
    {
      "first" : "John",
      "last" :  "Smith"
    },
    {
      "first" : "Alice",
      "last" :  "White"
    }
  ]
}
```

Is transformed like this during indexing:
```
{
  "user.first" : [ "alice", "john" ],
  "user.last" :  [ "smith", "white" ]
}
```

There is no array type in Elasticsearch. Any field can contain an array with
elements all having the same type. During dynamic mapping, Elasticsearch infers
type from the first element.

Term-level queries and keyword fields are not analyzed, so be careful when
issuing term-level queries and when querying keyword fields.

## Docker setup

Run the Elasticsearch container:

```
docker run \
    -d \
    --name elasticsearch  \
    -p 9200:9200 -p 9300:9300 \
    -e "discovery.type=single-node" \
    -e "cluster.routing.allocation.disk.threshold_enabled=false" \
    -v ${PWD}/roles.yml:/usr/share/elasticsearch/config/roles.yml \
    elasticsearch:9.1.3
```

The setting `cluster.routing.allocation.disk.threshold_enabled=false` is useful
to keep the cluster status green when local disk is close to full.

Reset the `elastic` user (superuser) password by excuting the relevant script
in interactive mode inside the container :
```
docker exec -it elasticsearch bash
./bin/elasticsearch-reset-password -u elastic -i
```

Create an application user:
```
./bin/elasticsearch-users useradd <username> -p <password>
```

Create a role with limited privileges by modifying the file
`/usr/share/elasticsearch/config/roles`:
```
<role-name>:
    indices:
        names: [...]
        privileges: [...]
```

See the
[documentation](https://www.elastic.co/docs/reference/elasticsearch/security-privileges)
for the list of privileges.

Attach the role to the user:
```
./bin/elasticsearch-users roles <username> -a <role-name>
```

## Troubleshooting

### High-watermark exceeded

Requests failed with error:

```
  File "/home/jonathans/projects/data-engineering/elasticsearch/es.py", line 36, in count_documents
    resp = await es.count(index=index)
  File "/home/jonathans/projects/data-engineering/elasticsearch/.venv/lib/python3.9/site-packages/elasticsearch/_async/client/__init__.py", line 1011, in count
    return await self.perform_request(  # type: ignore[return-value]
  File "/home/jonathans/projects/data-engineering/elasticsearch/.venv/lib/python3.9/site-packages/elasticsearch/_async/client/_base.py", line 271, in perform_request
    response = await self._perform_request(
  File "/home/jonathans/projects/data-engineering/elasticsearch/.venv/lib/python3.9/site-packages/elasticsearch/_async/client/_base.py", line 351, in _perform_request
    raise HTTP_EXCEPTIONS.get(meta.status, ApiError)(
elasticsearch.ApiError: ApiError(503, 'search_phase_execution_exception', None)
```

The cluster health is red:

```
Cluster health: {'cluster_name': 'docker-cluster', 'status': 'red', 'timed_out': False, 'number_of_nodes': 1, 'number_of_data_nodes': 1, 'active_primary_shards': 0, 'active_shards': 0, 'relocating_shards': 0, 'initializing_shards': 0, 'unassigned_shards': 2, 'unassigned_primary_shards': 1, 'delayed_unassigned_shards': 0, 'number_of_pending_tasks': 0, 'number_of_in_flight_fetch': 0, 'task_max_waiting_in_queue_millis': 0, 'active_shards_percent_as_number': 0.0}
```

If the local disk is close to full, try disabling allocation thresholds with:

```
curl -XPUT "http://localhost:9200/_cluster/settings" \
 -H 'Content-Type: application/json' -d'
{
  "persistent": {
    "cluster": {
      "routing": {
        "allocation.disk.threshold_enabled": false
      }
    }
  }
}'
```

### SSL errors

Setting the environment variable `xpack.security.enabled` to `false` may
be used to bypass authentication and SSL, when testing things.
