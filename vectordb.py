from pymilvus import MilvusClient
from langchain_milvus import Milvus
from uuid import uuid4

def initialize_vectordb(config):
    client = MilvusClient(
        uri=f"{config["db"]["host"]}:{config["db"]["port"]}",
        token=f"{config["db"]["username"]}:{config["db"]["password"]}"
    )
    databases = client.list_databases()
    if(config["db"]["db_name"] not in databases):
        print(f"Creating database: {config["db"]["db_name"]}")
        client.create_database(
            db_name= config["db"]["db_name"]
        )

def store_documents(config, embeddings, collection_name, list_of_documents):

    vector_store = Milvus(
        embedding_function=embeddings,
        collection_name=collection_name, 
        connection_args={
            "host": config["db"]["host"],
            "port": config["db"]["port"],
            "user": config["db"]["username"],
            "password": config["db"]["password"],
            "db_name": config["db"]["db_name"],
            "secure": False
        },
        index_params={"index_type": config["db"]["index_type"], "metric_type": config["db"]["metric_type"]},
        search_params={"index_type": config["db"]["index_type"], "metric_type": config["db"]["metric_type"]}
    )
    uuids = [str(uuid4()) for _ in range(len(list_of_documents))]

    vector_store.add_documents(documents=list_of_documents, ids=uuids)
    print(f"Stored documents in collection: {collection_name}")

def fetch_top_records(config, embeddings, collection_name, query, top_k):

    vector_store = Milvus(
        embedding_function=embeddings,
        collection_name=collection_name,
        connection_args={
            "host": config["db"]["host"],
            "port": config["db"]["port"],
            "user": config["db"]["username"],
            "password": config["db"]["password"],
            "db_name": config["db"]["db_name"],
            "secure": False
        },
        index_params={"index_type": config["db"]["index_type"], "metric_type": config["db"]["metric_type"]},
        search_params={"index_type": config["db"]["index_type"], "metric_type": config["db"]["metric_type"]}
    )
    print(f"Fetched top {top_k} records from collection {collection_name} for query: '{query}'")
    return vector_store.similarity_search_with_score(
        query, k=top_k
    )

def delete_collection(config, collection_name):
    client = MilvusClient(
        uri=f"{config["db"]["host"]}:{config["db"]["port"]}",
        token=f"{config["db"]["username"]}:{config["db"]["password"]}",
        db_name=config["db"]["db_name"]
    )

    client.drop_collection(
        collection_name=collection_name
    )
    print(f"Deleted collection {collection_name}")