from pymilvus import MilvusClient
import json

config = json.load(open("config.json","r"))

client = MilvusClient(
    uri=f"{config["db"]["host"]}:{config["db"]["port"]}",
    token=f"{config["db"]["username"]}:{config["db"]["password"]}",
    db_name=config["db"]["db_name"]
)

print(client.list_databases())
print(client.list_collections())