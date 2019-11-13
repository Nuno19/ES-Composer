from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import requests

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


from app import routes,models
db.create_all()

if app.config["UPLOAD_TO_RECOMENDATION"]:
    print("Uploading to Recomendation Service")
    clear = requests.post(app.config["BASE_REC_URL"]+"ClearItems")
    print(clear.text)
    file = open("final_metadata.tsv")
    send = requests.post(app.config["BASE_REC_URL"]+"loadItem",{"itemList":file.read()})
    print(send.text)
    update = requests.post(app.config["BASE_REC_URL"]+"computeKMeans")
    print(update.text)