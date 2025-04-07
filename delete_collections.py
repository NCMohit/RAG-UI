from vectordb import delete_collection
from pymilvus import MilvusClient
import json

config = json.load(open("config.json","r"))

client = MilvusClient(
    uri=f"{config["db"]["host"]}:{config["db"]["port"]}",
    token=f"{config["db"]["username"]}:{config["db"]["password"]}",
    db_name=config["db"]["db_name"]
)

for collection in client.list_collections():
    delete_collection(config, collection)

print(client.list_databases())
print(client.list_collections())