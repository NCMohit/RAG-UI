# RAG Application

## Setup Milvus DB

Get latest version of compose file from [here](https://milvus.io/docs/install_standalone-docker-compose.md)

Create Milvus database in docker using the command:
```
docker-compose up -d
```

## Install requirements

```
pip install -r requirements.txt
```

## Setup DB for Flask
```
python database_setup.py
```

## Start Flask Server
```
python main.py
```