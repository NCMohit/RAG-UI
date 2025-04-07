from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"

db.init_app(app)

class User(db.Model):
    username: Mapped[str] = mapped_column(primary_key=True)
    password_hash: Mapped[str]

class Collection(db.Model):
    collection_id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    username: Mapped[str]
    collection_name: Mapped[str]
    collection_description: Mapped[str]
    sys_prompt: Mapped[str]
    created_time: Mapped[float]

class Document(db.Model):
    document_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str]
    collection_id: Mapped[int]
    doc_title: Mapped[str]
    doc_description: Mapped[str]
    filename: Mapped[str]
    created_time: Mapped[float]

if(__name__ == "__main__"):
    with app.app_context():
        db.create_all()