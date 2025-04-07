from vectordb import initialize_vectordb, store_documents, fetch_top_records, delte_collection
from embeddings import generate_documents
from langchain_community.embeddings import HuggingFaceEmbeddings
from llm import construct_prompt, llm_call
import json
import torch
import os
import time
from flask import Flask, render_template, request, session, url_for, redirect, flash
from authentication import validate_login_credentials, validate_register_credentials
from database import create_collection, fetch_collections_by_username, fetch_collection_by_id, create_document, fetch_documents
from werkzeug.utils import secure_filename

config = json.load(open("config.json","r"))

embedding_model = HuggingFaceEmbeddings(
    model_name=config["embd"]["model_name"],
    model_kwargs = {'device': 'cuda' if torch.cuda.is_available() else "cpu"}
)

initialize_vectordb(config)

def load_document(input_file, collection_name, doc_title, doc_description):
    docs = generate_documents(config, input_file, doc_title, doc_description)
    store_documents(config, embedding_model, collection_name, docs)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'md', 'html', 'csv', 'json'}

app = Flask(__name__)
app.secret_key = "$up3rS3cr3tK3y"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_collection_name(collection_name):
    check = True
    for char in collection_name:
        if(char.isalnum()):
            pass
        elif(char == "_"):
            pass
        else:
            check = False
            break
    return check

@app.route("/", methods=["GET","POST"])
def index_page():
    if(request.method == "POST"):
        result = request.form
        validity = validate_login_credentials(result["username"],result["password"])
        if(validity[0]):
            session['username'] = result["username"].lower()
            return redirect(url_for("main_page"))
        else:
            flash(validity[1])
            return redirect(url_for("index_page"))
    else:
        if("username" in session):
            return redirect(url_for("main_page"))
        else:
            return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register_page():
    if(request.method == "POST"):
        result = request.form
        validity = validate_register_credentials(result["username"],result["password"])
        if(validity[0]):
            return render_template('alert.html', title="Alert", alert="Account Created")
        else:
            flash(validity[1])
            return redirect(url_for("register_page"))
    else:
        return render_template("register.html")

@app.route("/logout", methods=["GET"])
def logout_page():
    if("username" in session):
        del session["username"]
    return redirect(url_for("index_page"))

@app.route("/main")
def main_page():
    if("username" in session):
        collections = fetch_collections_by_username(session['username'])
        return render_template('main.html', collections=collections, time=time)
    else:
        return redirect(url_for("index_page"))

@app.route("/create_collection", methods=["GET","POST"])
def collection_creation_page():
    if("username" in session):
        if(request.method == "POST"):
            if("username" in session):
                result = request.form
                if(not check_collection_name(result['collection_name'])):
                    return render_template('alert.html', title="Error", alert="Collection Name should only have letters, numbers and underscore !")
                if(create_collection(session['username'],result['collection_name'],result['collection_description'], result["sys_prompt"])):
                    return redirect(url_for("main_page"))
                else:
                    return render_template('alert.html', title="Error", alert="Collection Name already exists")
        else:
            return render_template('create_collection.html')
    else:
        return redirect(url_for("index_page"))

@app.route("/collection/<collection_id>")
def collection_page(collection_id):
    if("username" in session):
        documents = fetch_documents(collection_id)
        collection = fetch_collection_by_id(collection_id)
        return render_template('collection.html', collection=collection, documents=documents, time=time, username=session['username'])
    else:
        return redirect(url_for("index_page"))

@app.route("/query_collection/<collection_id>", methods=["GET","POST"])
def query_collection(collection_id):
    if("username" in session):
        if(request.method == "POST"):
            result = request.form
            collection = fetch_collection_by_id(collection_id)
            if(session['username']==collection.username):
                query = result["query"]
                docs = fetch_top_records(config, embedding_model, session["username"] + "_" + collection.collection_name, query, top_k=config["embd"]["query_top_k"])
                return render_template('query_collection.html', collection_id=collection_id, docs=docs)
            else:
                return render_template('alert.html', title="Error", alert="This is not your Collection!")
        else:
            return render_template('query_collection.html', collection_id=collection_id)
    else:
        return redirect(url_for("index_page"))

@app.route("/query_llm/<collection_id>", methods=["GET","POST"])
def query_llm(collection_id):
    if("username" in session):
        if(request.method == "POST"):
            result = request.form
            collection = fetch_collection_by_id(collection_id)
            if(session['username']==collection.username):
                query = result["query"]
                docs = fetch_top_records(config, embedding_model, session["username"] + "_" + collection.collection_name, query, top_k=config["embd"]["query_top_k"])
                prompt = construct_prompt(docs, query)
                sys_prompt = collection.sys_prompt
                llm_response = llm_call(config, sys_prompt, prompt)
                output = llm_response.json()["choices"][0]["message"]["content"]
                return render_template('query_llm.html', collection_id=collection_id, output=output)
            else:
                return render_template('alert.html', title="Error", alert="This is not your Collection!")
        else:
            return render_template('query_llm.html', collection_id=collection_id)
    else:
        return redirect(url_for("index_page"))

@app.route("/upload_doc/<collection_id>", methods=["GET","POST"])
def upload_doc(collection_id):
    if("username" in session):
        if(request.method == "POST"):
            result = request.form
            
            collection = fetch_collection_by_id(collection_id)
            if(session['username']==collection.username):
                if 'file' not in request.files:
                    return render_template('alert.html', title="Error", alert="No file part")
                file = request.files['file']
                if file.filename == '':
                    return render_template('alert.html', title="Error", alert="No file selected")
                if file and allowed_file(file.filename):
                    filename = session["username"] + "_" + collection.collection_name + "_" + secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    return render_template('alert.html', title="Error", alert="Unsupported file type !")
                
                if(create_document(session['username'],collection_id,result['doc_title'],result['doc_description'],filename)):
                    load_document(os.path.join(app.config['UPLOAD_FOLDER'], filename), session["username"] + "_" + collection.collection_name, result['doc_title'],result['doc_description'])
                    return redirect(url_for("collection_page",collection_id=collection_id))
                else:
                    return render_template('alert.html', title="Error", alert="Document title already exists")
            else:
                return render_template('alert.html', title="Error", alert="This is not your Collection!")
        else:
            return render_template('upload_document.html', collection_id=collection_id)
    else:
        return redirect(url_for("index_page"))

if(__name__=="__main__"):
    app.run(host="0.0.0.0", port=8080, debug=False)