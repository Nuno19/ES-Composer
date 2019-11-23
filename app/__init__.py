from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import requests
<<<<<<< HEAD
import json
=======
import csv
>>>>>>> 72b65fad65122f4a50ced1d3c96803912302242b

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


from app import routes,models
db.create_all()

if app.config["UPLOAD_TO_RECOMENDATION"]:
    print("Uploading to Recomendation Service")
    clear = requests.post("https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"+"ClearItems")
    print(clear.text)
<<<<<<< HEAD
    k = requests.post("https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"+"setClusterNumber",{"k":10})
    print(k.text)
    
    file = open("random250.tsv","r",encoding="utf-8")
=======
    file = open("final_metadata.tsv","r",encoding="utf-8")
    readCSV = csv.reader(file, delimiter='\t')

    for data in readCSV:
        if data[0] != "director_name":
            seat = 0
            while seat < 3:
                requests.post("http://localhost:8080/raimas1996/Booking_Service_test/1.0.0/asset", json = {'name': data[4], 'location': "Glicínias Aveiro", 'seat': seat + 1})
                seat += 1

>>>>>>> 72b65fad65122f4a50ced1d3c96803912302242b
    send = requests.post("https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"+"loadItem",{"itemList":file.read()})
    print(send.text)
    update = requests.post("https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"+"computeKMeans")
    app.config["K"] = int(json.loads(update.text)["K"])
    print(update.text)