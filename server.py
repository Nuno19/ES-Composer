import os
from flask import Flask, render_template,request
import requests
import json
from random import shuffle

app = Flask(__name__)

@app.route("/")
def index():
    
    return render_template("index.html", message="HEllO WORLD");   

@app.route('/uploader', methods = ['POST'])
def uploadFile():
    if request.method == 'POST':
        f = request.files['file']
        values = f.read()
        #print(values)

        text = requests.post("http://127.0.0.1:8080/Nuno19/Recomendation_Service/1.0.0/loadItem",data={"itemList":values})
    
        return render_template("admin.html", message=text.text)

    return render_template("admin.html", message="FAILED")

@app.route('/admin')
def getAdmin():
    return render_template("admin.html")


@app.route('/setk', methods = ['POST'])
def setKandUpdate():
    if request.method == 'POST':
        k = request.form['k']
        text = requests.post("http://127.0.0.1:8080/Nuno19/Recomendation_Service/1.0.0/setClusterNumber",data={"k":k})
        update = requests.post("http://127.0.0.1:8080/Nuno19/Recomendation_Service/1.0.0/loadItemList")
        print(text.text)
        print(update.text)
    return render_template("admin.html")


@app.route('/recomended',methods=['GET'])
def getRecomended():
    if request.method == 'GET':
       # centID = request.args.get("centID")
        text = requests.get("http://127.0.0.1:8080/Nuno19/Recomendation_Service/1.0.0/getRecommended",{"centID":0})
        files = json.loads(text.text)
        dataList = [json.loads(f["data"]) for f in files]
        shuffle(dataList)
        print(files[0])

        text = requests.get("http://127.0.0.1:8080/Nuno19/Recomendation_Service/1.0.0/getRecommended",{"centID":1})
        files = json.loads(text.text)
        dataList1 = [json.loads(f["data"]) for f in files]
        shuffle(dataList1)
        print(files[0])

        return render_template("index.html", list=[dataList[:5],dataList1[:5]])



if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)