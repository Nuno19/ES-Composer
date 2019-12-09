from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import requests
import json
import csv 

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


from app import routes,models
db.create_all()

from app.models import Movie,Actor,Genre
file = open("final.csv","r",encoding="utf-8")

if False:
    i=0
    spamreader = csv.reader(file, delimiter='	', quotechar='',quoting=csv.QUOTE_NONE,)
    for row in spamreader:
        if i == 0:
            i+=1
            continue
        mov = Movie(title=row[4],imdbID=row[7],director=row[0],year=row[8])
        mov.addGenres(row[2].split(" "))
        mov.addActors([row[1],row[3],row[5]])
        print(mov)
        db.session.add(mov)
        db.session.commit()

if app.config["UPLOAD_TO_RECOMENDATION"]:
    print("Uploading to Recomendation Service")
    clear = requests.post("https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"+"ClearItems")
    print(clear.text)
    k = requests.post("https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"+"setClusterNumber",{"k":14})
    print(k.text)
    
   
    send = requests.post("https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"+"loadItem",{"itemList":file.read()})
    print(send.text)
    update = requests.post("https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"+"computeKMeans")
    print(update.text)
    app.config["K"] = int(json.loads(update.text)["K"])
    print(update.text)
