import os
from flask import Flask, render_template,request,flash,url_for,redirect,session
import requests
import json
from random import shuffle
from flask_oauth import OAuth,OAuthException

BASE_REC_URL = "http://127.0.0.1:8080/Nuno19/Recomendation_Service/1.0.0/"
FACEBOOK_APP_ID = '410201056336364'
FACEBOOK_APP_SECRET = '87ab5869395b2593750e87743d1048cd'

app = Flask(__name__)
oauth = OAuth()


@app.route("/")
def index():
    return render_template("index.html", message="HEllO WORLD");   

facebook = oauth.remote_app(
    'facebook',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    access_token_method='GET',
    authorize_url='https://www.facebook.com/v5.0/dialog/oauth'
)

@app.route('/login')
def login():
    return redirect("https://www.facebook.com/v5.0/dialog/oauth?client_id=410201056336364&redirect_uri=http://localhost:8000/login/authorized&state={st=state123abc,ds=123456789}&display=popup&response_type=token")

@app.route("/ses")
def ses():
    return render_template("index.html", message=session['facebook_token']);   

@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    print(request.args)

    session['logged_in'] = True
   # session['facebook_token'] = (resp['access_token'], '')
    print("Authorized" )

    return request.data


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

@app.route('/uploader', methods = ['POST'])
def uploadFile():
    if request.method == 'POST':
        f = request.files['file']
        values = f.read()
        #print(values)
        flash("File Uploaded!")

        text = requests.post(BASE_REC_URL+"loadItem",data={"itemList":values})
        k = 20
        if "k" in session.keys():
            k = session["k"]
        return render_template("admin.html",k=k, message=text.text)

    return render_template("admin.html", message="FAILED")

@app.route('/admin')
def getAdmin():
    if "k" in session.keys():
        return render_template("admin.html",k=session["k"])
    return render_template("admin.html",k=20)
    


@app.route('/setk', methods = ['POST'])
def setKandUpdate():
    if request.method == 'POST':
        k = request.form['k']
        text = requests.post(BASE_REC_URL+"setClusterNumber",data={"k":k})
        update = requests.post(BASE_REC_URL+"loadItemList")
        print(text.text)
        session["k"] = k
        print(update.text)
    return render_template("admin.html",k=k)


@app.route('/recomended',methods=['GET'])
def getRecomended():
    if request.method == 'GET':
       # centID = request.args.get("centID")
        text = requests.get(BASE_REC_URL+"getRecommended",{"centID":0})
        files = json.loads(text.text)
        dataList = [json.loads(f["data"]) for f in files]
        shuffle(dataList)
        
        text = requests.get(BASE_REC_URL+"getRecommended",{"centID":1})
        files = json.loads(text.text)
        dataList1 = [json.loads(f["data"]) for f in files]
        shuffle(dataList1)

        return render_template("index.html", list=[dataList[:5],dataList1[:5]])

@app.route('/search',methods=['GET'])
def searchPack():
    if request.method == 'GET':
        query = request.args.get("query")
        if query == "":
            return render_template("index.html", list=[])
        result = requests.get(BASE_REC_URL+"GetTextRecommended",{"query":query})
        
        print(result.text)
        list = json.loads(result.text)
        pack = [json.loads(f["data"]) for f in list ]
    return render_template("index.html", list=[pack[:5]])
        

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run(host='127.0.0.1', port=8000, debug=True)