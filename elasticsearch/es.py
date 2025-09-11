import asyncio
import json
import os
from contextlib import asynccontextmanager

from elasticsearch import (
    AsyncElasticsearch,
    BadRequestError,
)

HOST = "https://localhost:9200"

SUPERUSER_CREDS = (
    os.getenv("ELASTICSEARCH_SU_USER"),
    os.getenv("ELASTICSEARCH_SU_PASSWORD"),
)

APP_USER_CREDS = (
    os.getenv("ELASTICSEARCH_USER"),
    os.getenv("ELASTICSEARCH_PASSWORD"),
)

INDEX_TEXTS = "pastebin-texts-000001"
ALIAS_INDEX_TEXTS = "pastebin-texts"

SETTINGS_INDEX_TEXTS = {
    "analysis": {
        "analyzer": {
            "standard_with_stopwords_enabled": {
                "type": "standard",
                "stopwords": "_english_",
                "char_filter": ["html_strip"],
            }
        }
    },
}

ALIASES_INDEX_TEXTS = {ALIAS_INDEX_TEXTS: {}}

MAPPINGS_INDEX_TEXTS = {
    "properties": {
        "title": {
            "type": "text",
        },
        "body": {
            "type": "text",
        },
    }
}

TEXT_PATHS = [
    {
        "title": "Documents: the architect's programming language",
        "path": "texts/architect.txt",
    },
    {
        "title": "Functional data engineering",
        "path": "texts/functional_data_engineering.txt",
    },
    {
        "title": "Iceberg model",
        "path": "texts/iceberg_model.txt",
    },
]

ROLE_NAME_PASTEBIN = "pastebin"
PRIVILEGES_PASTEBIN = {
    "indices": [
        {
            "names": ["pastebin-texts"],
            "privileges": ["read", "write"],
        },
    ],
}


@asynccontextmanager
async def get_client(superuser=False):
    if superuser:
        creds = SUPERUSER_CREDS
    else:
        creds = APP_USER_CREDS

    client = AsyncElasticsearch(
        HOST,
        basic_auth=creds,
        verify_certs=False,
        connections_per_node=10,  # is this how we create a connection pool?
    )
    try:
        yield client
    finally:
        await client.close()


async def index_exists(name):
    async with get_client(superuser=True) as es:
        resp = await es.indices.exists(index=name)
        print(f"Response: {resp}")


async def index_get_mapping(name):
    async with get_client(superuser=True) as es:
        resp = await es.indices.get_mapping(index=name)
        print(f"Response: {resp}")


async def create_index(name, settings=None, mappings=None, aliases=None):
    async with get_client(superuser=True) as es:
        if await es.indices.exists(index=name):
            print(f"Index '{name}' already exists")
        else:
            resp = await es.indices.create(
                index=name,
                settings=settings,
                mappings=mappings,
                aliases=aliases,
            )
            print(f"Response: {resp}")


async def delete_index(name):
    async with get_client(superuser=True) as es:
        resp = await es.indices.delete(index=name)
        print(f"Response: {resp}")


async def index_bulk(index, doc_list):
    async with get_client() as es:
        resp = await es.bulk(index=index, operations=doc_list)
        print(f"Response: {resp}")


async def index_doc(document, index):
    async with get_client() as es:
        resp = await es.index(index=index, document=document)
        print(f"Response: {resp}")


async def index_texts():
    for text in TEXT_PATHS:
        with open(text["path"]) as fi:
            body = fi.read()
            document = {
                "title": text["title"],
                "body": body,
            }
            await index_doc(index=ALIAS_INDEX_TEXTS, document=document)


async def count_documents(index):
    async with get_client() as es:
        resp = await es.count(index=index)
        print(f"Number of documents: {resp}")


async def cluster_health():
    async with get_client(superuser=True) as es:
        resp = await es.cluster.health()
        print(f"Cluster health: {resp}")


async def get_document_by_id(
    index,
    doc_id,
    source_includes=None,
):
    async with get_client() as es:
        resp = await es.get(
            index=index,
            id=doc_id,
            source_includes=source_includes,
        )
        print(f"Response: {resp}")


async def search(
    index,
    q=None,
    query=None,
    source=None,
    highlight=None,
    fields=None,
    explain=False,
):
    """
    Example:

    await search(
        INDEX_TEXTS,
        q='body:"great influence"~5',
        source=["title"],
        highlight={"fields": {"body": {}}},
    )
    """
    async with get_client(superuser=True) as es:
        try:
            resp = await es.search(
                index=index,
                fields=fields,
                highlight=highlight,
                q=q,
                query=query,
                source=source,
                explain=explain,
            )
        except BadRequestError as err:
            resp = err.info["error"]["root_cause"][0]["reason"]
        except Exception as err:
            resp = str(err)
        print(f"Response: {resp}")


async def get_index_settings(index):
    async with get_client(superuser=True) as es:
        resp = await es.indices.get_settings(index=index)
        print(f"Response: {resp}")


async def enable_stop_word_filtering(index):
    async with get_client(superuser=True) as es:
        resp = await es.indices.put_settings(
            index=index,
            settings=SETTINGS_INDEX_TEXTS,
            reopen=True,
        )
        print("Response: {resp}")


async def get_index_mapping(index):
    async with get_client(superuser=True) as es:
        resp = await es.indices.get_mapping(index=index)
        print(f"Response: {resp}")


async def put_index_mapping(index, properties):
    async with get_client(superuser=True) as es:
        resp = await es.indices.put_mapping(index=index, properties=properties)
        print(f"Response: {resp}")


async def analyze(index, text):
    async with get_client(superuser=True) as es:
        resp = await es.indices.analyze(index=index, text=text)
        print(f"Response: {resp}")


async def get_alias():
    async with get_client(superuser=True) as es:
        resp = await es.indices.get_alias()
        print(f"Response: {resp}")


async def node_stats():
    async with get_client(superuser=True) as es:
        resp = await es.nodes.stats()
        print(resp["nodes"]["DVsvtgOLQ1WafmO3QiS4WQ"]["http"]["current_open"])
        print(resp["nodes"]["DVsvtgOLQ1WafmO3QiS4WQ"]["http"]["total_opened"])


async def concurrent():
    tasks = [count_documents(INDEX_TEXTS) for _ in range(10)]
    await asyncio.gather(*tasks)


async def main():
    await search(
        "products",
        query={
            "function_score": {
                "query": {
                    "term": {
                        "product.keyword": {
                            "value": "TV",
                        },
                    },
                },
                "random_score": {},
            },
        },
        source=False,
        #highlight={"fields": {"product": {}, "price": {}}},
    )


if __name__ == "__main__":
    asyncio.run(main())
