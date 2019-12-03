from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import requests
import json
import csv

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from app import routes, models
db.create_all()

cinemas = ["Glicínias Plaza", "Fórum Coimbra", "Fórum Algarve"]#, "Norte Shopping", "Mar Shopping", "Palácio do Gelo"]
seatRows = ['A', 'B', 'C', 'D']
numberAssets = 0

if app.config["UPLOAD_TO_RECOMENDATION"]:
    file = open("final_metadata.tsv","r",encoding="utf-8")
            
    readCSV = csv.reader(file, delimiter='\t')
    index = 0
    for data in readCSV:
        if data[0] != "director_name":
            for cinema in cinemas:
                for seatRow in seatRows:
                    seatNumber = 0
                    while seatNumber < 3:
                        print(requests.post("https://es-booking-service.herokuapp.com/raimas1996/Booking_Service_test/1.0.0/asset", json = {'name': data[4], 'location': cinema, 'seat': seatRow + str(seatNumber + 1)}))
                        print(numberAssets, cinema, index, data[4], seatRow + str(seatNumber + 1))
                        seatNumber += 1
                        numberAssets += 1
        index += 1
