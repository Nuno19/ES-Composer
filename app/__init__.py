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
    clear = requests.post("https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"+"ClearItems")
    print(clear.text)
    file = open("final_metadata.tsv","r",encoding="utf-8")
    send = requests.post("https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"+"loadItem",{"itemList":file.read()})
    print(send.text)
    update = requests.post("https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"+"computeKMeans")
    print(update.text)