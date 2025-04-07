from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredHTMLLoader, csv_loader, PyPDFLoader
import json

def generate_documents(config, input_file):
    if((input_file.endswith(".txt")) or (input_file.endswith(".md"))):
        with open(input_file,"r") as file:
            txt = file.read()
    elif(input_file.endswith(".html")):
        loader = UnstructuredHTMLLoader(input_file)
        data = loader.load()
        txt = data[0].page_content
    elif(input_file.endswith(".csv")):
        loader = csv_loader.CSVLoader(file_path=input_file)
        data = loader.load()
        txt = data[0].page_content
    elif(input_file.endswith(".json")):
        txt = json.load(open(input_file,"r"))
    elif(input_file.endswith(".pdf")):
        txt = ""
        loader = PyPDFLoader(input_file)
        pages = loader.load_and_split()
        for page in pages:
            txt += page.page_content
    else:
        raise Exception("Document not supported!")

    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=config["chunks"]["chunk_size"],
        chunk_overlap=config["chunks"]["chunk_overlap"],
        length_function=len,
        is_separator_regex=False,
    )
    docs = text_splitter.create_documents([txt])
    print(f"Documents generated for file: {input_file}")
    for index in range(len(docs)):
        docs[index].metadata = {"document_name": input_file}
    return docs