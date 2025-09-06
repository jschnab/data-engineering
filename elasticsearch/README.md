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

### Term indexing

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
