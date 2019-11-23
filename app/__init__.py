from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import requests
import json

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


from app import routes,models
db.create_all()

if app.config["UPLOAD_TO_RECOMENDATION"]:
    print("Uploading to Recomendation Service")
    clear = requests.post("https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"+"ClearItems")
    print(clear.text)
    k = requests.post("https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"+"setClusterNumber",{"k":10})
    print(k.text)
    
    file = open("random250.tsv","r",encoding="utf-8")
    send = requests.post("https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"+"loadItem",{"itemList":file.read()})
    print(send.text)
    update = requests.post("https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"+"computeKMeans")
    app.config["K"] = int(json.loads(update.text)["K"])
    print(update.text)