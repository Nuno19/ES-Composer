import os
from flask import Flask, render_template,request,flash,url_for,redirect,session
import requests
import json
from random import shuffle
from rauth.service import OAuth2Service
from flask_sqlalchemy import SQLAlchemy

SQLALCHEMY_DATABASE_URI = 'sqlite:///facebook.db'
BASE_REC_URL = "http://127.0.0.1:8080/Nuno19/Recomendation_Service/1.0.0/"
FACEBOOK_APP_ID = '410201056336364'
FACEBOOK_APP_SECRET = '87ab5869395b2593750e87743d1048cd'
TMDB_SECRET = 'e01f3f11c30c294d74c63e3f889bf19f'

app = Flask(__name__)
app.secret_key = 'development'
app.config.from_object(__name__)
db = SQLAlchemy(app)

graph_url = 'https://graph.facebook.com/'
facebook = OAuth2Service(name='facebook',
                         authorize_url='https://www.facebook.com/dialog/oauth',
                         access_token_url=graph_url + 'oauth/access_token',
                         client_id=FACEBOOK_APP_ID,
                         client_secret=FACEBOOK_APP_SECRET,
                         base_url=graph_url
                         )

# models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    fb_id = db.Column(db.String(30))
    likes = db.relationship('MovieLike', backref='user')


    def __repr__(self):
        return '<User %r,id=%r>' % (self.name,self.id)

    @staticmethod
    def get_or_create(name, fb_id):
        user = User.query.filter_by(fb_id=fb_id).first()
        if user is None:
            user = User(name=name, fb_id=fb_id)
            db.session.add(user)
            db.session.commit()
        return user


class MovieLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<MovieLike %r>' % self.title

    @staticmethod
    def addToUser(title, user):
        like = MovieLike.query.filter_by(title=title).filter_by(user_id=user.id).first()
        if like is None:
            like = MovieLike(title=title,user=user)
            
            db.session.add(like)
            db.session.commit()
        return like

    @staticmethod
    def getAllUserLikes(fb_id):
        user = User.query.filter_by(fb_id=fb_id).first()
        if user is None:
            return None
        return MovieLike.query.filter_by(user_id=user.id).all()


def uploadFile():
    f = open("final_metadata.tsv","r",encoding="utf-8")
    values = f.read().replace("\"","")

    text = requests.post(BASE_REC_URL+"loadItem",data={"itemList":values})
    update = requests.post(BASE_REC_URL+"loadItemList")
   # print(text.text)


@app.route('/')
def index():
    return redirect(url_for('getRecomended'))


@app.route('/facebook/login')
def login():
    redirect_uri = url_for('authorized', _external=True)
    params = {'redirect_uri': redirect_uri,'scope':'user_likes '}
   # print(facebook.get_authorize_url(**params))
    return redirect(facebook.get_authorize_url(**params))

@app.route('/facebook/authorized')
def authorized():
    # check to make sure the user authorized the request
    if not 'code' in request.args:
        flash('You did not authorize the request')
        return redirect(url_for('index'))

    # make a request for the access token credentials using code
    redirect_uri = url_for('authorized', _external=True)
    data = dict(code=request.args['code'], redirect_uri=redirect_uri)
    
    auth = facebook.get_auth_session(data=data,decoder=json.loads)
    print(auth)
    
    session["code"] = json.dumps(data)
    # the "me" response
    me = auth.get('me').json()
    session["me"] = me["name"]
    session["id"] = me["id"]
    #likes = sessions.get('me?fields=likes.summary(true)').json()
    likes = auth.get('me?fields=movies').json()
    
    movies = [data["name"] for data in likes["movies"]["data"]]
    
    print(movies)
    us = User.get_or_create(me["name"],me["id"])
    for l in movies:
        MovieLike.addToUser(l,us)    
    print(us.likes)
    flash('Logged in as ' + me['name'])

    return redirect(url_for('getRecomended'))


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
        fbId = session["id"]
        print("FBID:" + fbId )
        print(MovieLike.getAllUserLikes(fbId))
        
        return render_template("index.html", list=[dataList[:5],dataList1[:5]])



@app.route('/facebookRecomended',methods=['GET'])
def getFromFacebookLikes():
    if request.method == 'GET':
        if "id" not in session:
            flash("Not Logged in!")
            return render_template("index.html")

        likes = MovieLike.getAllUserLikes(session["id"])
        shuffle(likes)
        likes = likes[:5]
        titles = [l.title for l in likes]
        toRet = []
        for l in titles:
            toDict = {}
            result = requests.get(BASE_REC_URL+"GetTextRecommended",{"query":l})
            list = json.loads(result.text)
            pack = [json.loads(f["data"]) for f in list ]
            toDict["movies"] = pack[:5]
            toDict["packName"] = l
            toRet.append(toDict)

        print(toRet)
    return render_template("searchFacebook.html", list=toRet)

@app.route('/search',methods=['GET'])
def searchPack():
    if request.method == 'GET':
        query = request.args.get("query")
        if query == "":
            return render_template("index.html", list=[])
        result = requests.get(BASE_REC_URL+"GetTextRecommended",{"query":query})
        
        #print(result.text)
        list = json.loads(result.text)
        pack = [json.loads(f["data"]) for f in list ]
    return render_template("index.html", list=[pack[:20]])
        


@app.route('/payment',methods=['GET','POST'])
def payment():
    if request.method == 'POST':
        # url = "http://localhost:8040/payment"
        url = "http://localhost:8040/api/payment"
        params = {
            # "amount": request.form['amount'],
            "client": "client data",
            "amount": "50e"
        }
        # data = {"eventType": "AAS_PORTAL_START", "data": {"uid": "hfe3hf45huf33545", "aid": "1", "vid": "1"}}
        # requests.post(url, params=params)
        # requests.post(url, params=params)
        requests.get(url, params=params)
    else:
        data = requests.get("http://localhost:8040/api/payment")
        print(data.text)
        return render_template("payment.html")



@app.route('/getPoster',methods=['GET'])
def getPoster():
    imdbID = request.args.get("imdbID")
    size = request.args.get("size")
    if imdbID == None:
        return None 
    url = "https://api.themoviedb.org/3/find/{imdbID}?api_key={TMDB_SECRET}&language=en-US&external_source=imdb_id".format(imdbID=imdbID,TMDB_SECRET=TMDB_SECRET)
   
    data = requests.get(url).text
    data = json.loads(data)
    if "movie_results" not in data:
        return "https://critics.io/img/movies/poster-placeholder.png"
        
    data = data["movie_results"]
    if len(data) == 0:
        return "https://critics.io/img/movies/poster-placeholder.png"
    data = data[0]

    if size == "small":
       # print("https://image.tmdb.org/t/p/w85"+ data["poster_path"])
        return "https://image.tmdb.org/t/p/w185"+ data["poster_path"]
    
  #  print("https://image.tmdb.org/t/p/w300"+ data["poster_path"])
    return "https://image.tmdb.org/t/p/w300"+ data["poster_path"]




if __name__ == "__main__":
    app.secret_key = 'super secret key'
    context = ('localhost.crt', 'localhost.key')
    db.create_all()
    #uploadFile()
    app.run(host='127.0.0.1', port=8000, debug=True,ssl_context=context, use_reloader=False)

