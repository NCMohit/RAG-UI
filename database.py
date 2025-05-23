from database_setup import db, app, User, Collection, Document
import time
import os

db_name = "mydatabase.db"

def create_new_user(username, password_hash):
    with app.app_context():
        user = User(
            username = username,
            password_hash = password_hash
        )
        db.session.add(user)
        db.session.commit()

def fetch_user(username):
    with app.app_context():
        user = db.session.execute(db.select(User).where(User.username == username),execution_options={"prebuffer_rows": True}).scalar()
    return user

def create_collection(username, collection_name, collection_description, sys_prompt):
    with app.app_context():
        collection = db.session.execute(db.select(Collection).where(Collection.collection_name == collection_name,Collection.username == username)).scalar()
        if(collection is not None):
            return False
        else:
            collection = Collection(
                username = username,
                collection_name = collection_name,
                collection_description = collection_description,
                sys_prompt = sys_prompt,
                created_time = time.time()
            )
            db.session.add(collection)
            db.session.commit()
            return True

def fetch_collections_by_username(username=None):
    with app.app_context():
        if(username is None):
            collections = db.session.execute(db.select(Collection),execution_options={"prebuffer_rows": True}).scalars()
        else:
            collections = db.session.execute(db.select(Collection).where(Collection.username == username),execution_options={"prebuffer_rows": True}).scalars()
    return collections

def fetch_collection_by_id(collection_id):
    with app.app_context():
        collection = db.session.execute(db.select(Collection).where(Collection.collection_id == collection_id),execution_options={"prebuffer_rows": True}).scalar()
    return collection

def fetch_documents(collection_id):
    with app.app_context():
        documents = db.session.execute(db.select(Document).where(Document.collection_id == collection_id),execution_options={"prebuffer_rows": True}).scalars()
    return documents

def delete_document_db(upload_folder, document_id):
    with app.app_context():
        document = db.session.execute(db.select(Document).where(Document.document_id == document_id),execution_options={"prebuffer_rows": True}).scalar()
        os.remove(os.path.join(upload_folder, document.filename))
        db.session.delete(document)
        db.session.commit()

def delete_collection_db(upload_folder, collection_id):
    with app.app_context():
        collection = db.session.execute(db.select(Collection).where(Collection.collection_id == collection_id),execution_options={"prebuffer_rows": True}).scalar()
        documents = fetch_documents(collection.collection_id)
        for doc in documents:
            delete_document_db(upload_folder, doc.document_id)
        db.session.delete(collection)
        db.session.commit()

def create_document(username, collection_id, title, doc_description, filename):
    with app.app_context():
        doc = db.session.execute(db.select(Document).where(Document.collection_id == collection_id, Document.doc_title == title)).scalar()
        if(doc is not None):
            return False
        else:
            doc = Document(
                username = username,
                collection_id = collection_id,
                doc_title = title,
                doc_description = doc_description,
                filename = filename,
                created_time = time.time()
            )
            db.session.add(doc)
            db.session.commit()
            return True

def fetch_document_by_id(document_id):
    with app.app_context():
        document = db.session.execute(db.select(Document).where(Document.document_id == document_id),execution_options={"prebuffer_rows": True}).scalar()
    return document