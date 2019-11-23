from app import app
from app.models import User, MovieLike,MovieWatched,MovieGenre,MovieActor
import os
from flask import Flask, render_template,request,flash,url_for,redirect,session
import requests
import json
from random import shuffle,randint
from rauth.service import OAuth2Service


REC_URL = app.config["BASE_REC_URL"]

graph_url = 'https://graph.facebook.com/'
facebook = OAuth2Service(name='facebook',
                         authorize_url='https://www.facebook.com/dialog/oauth',
                         access_token_url=graph_url + 'oauth/access_token',
                         client_id=app.config["FACEBOOK_APP_ID"],
                         client_secret=app.config["FACEBOOK_APP_SECRET"],
                         base_url=graph_url
                         )


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
    us = User.get_or_create(me["name"],me["id"])
    

    movies = [data["name"] for data in likes["movies"]["data"]]
    
    print(movies)
    for l in movies:
         us.addLike(MovieLike(title=l))
    print(us.likes)
    flash('Logged in as ' + me['name'])

    return redirect(url_for('getRecomended'))

@app.route('/setWatch',methods=['GET'])
def setWatch():
    if "id" not in session:
            flash("Not Logged in!")
            return render_template("index.html")

    
    mov = MovieWatched(title="Tit",imdbID="tsa323a")
    
    mov.addGenres(["Gen1","gen2"])
    mov.addActors(["ACT1","Act2"])
    us = User.getById(session["id"])
    
    us.addWatched(mov)
    
    return redirect(url_for('getRecomended'))


@app.route('/recomended',methods=['GET'])
def getRecomended():
    if request.method == 'GET':
       # centID = request.args.get("centID")
        text = requests.get(REC_URL+"getRecommended",{"centID":randint(0,app.config["K"]-1)})
        print(text.text)
        toLoad = text.text
        if toLoad is None:
            return render_template("index.html", movies=[],login=login)

        files = json.loads(toLoad)
        dataList = [json.loads(f["data"]) for f in files]
        shuffle(dataList)

        login = "me" not in session
        return render_template("index.html",relevent=dataList[0] ,movies=dataList[1:16],login=login)

@app.route('/facebookRecomended',methods=['GET'])
def getFromFacebookLikes():
    if request.method == 'GET':
        if "id" not in session:
            flash("Not Logged in!")
            return render_template("index.html")

        likes = MovieLike.getAllUserLikes(session["id"])
        shuffle(likes)
        likes = likes[:2]
        titles = [l.title for l in likes]
        toRet = []
        for l in titles:
            toDict = {}
            result = requests.get(REC_URL+"GetTextRecommended",{"query":l})
            list = json.loads(result.text)
            pack = [json.loads(f["data"]) for f in list ]
            toDict["movies"] = pack[:5]
            toDict["packName"] = l
            toRet.append(toDict)

        print(toRet)
        login = "me" not in session
    return render_template("searchFacebook.html", list=toRet,login=login)

@app.route('/search',methods=['GET'])
def searchPack():
    if request.method == 'GET':
        query = request.args.get("query")
        if query == "":
            return render_template("index.html", movies=[])
        result = requests.get(REC_URL+"GetTextRecommended",{"query":query})
        
        print(result.text)
        list = json.loads(result.text)
        pack = [json.loads(f["data"]) for f in list ]
    return render_template("index.html",relevent=[], movies=pack[:20])
        


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


@app.route('/getBackDrop',methods=['GET'])
def getBackDrop():
    imdbID = request.args.get("imdbID")
    if imdbID == None:
        return None 
    url = "https://api.themoviedb.org/3/find/{imdbID}?api_key={TMDB_SECRET}&language=en-US&external_source=imdb_id".format(imdbID=imdbID,TMDB_SECRET=app.config["TMDB_SECRET"])
   
    data = requests.get(url).text
    data = json.loads(data)
    if "movie_results" not in data:
        return "https://d32qys9a6wm9no.cloudfront.net/images/movies/poster/500x735.png"

    data = data["movie_results"]
    if len(data) == 0:
        return "https://d32qys9a6wm9no.cloudfront.net/images/movies/poster/500x735.png"
    data = data[0]

    print("https://image.tmdb.org/t/p/original"+ data["backdrop_path"])
    return "https://image.tmdb.org/t/p/original"+ data["backdrop_path"]
    

@app.route('/getPoster',methods=['GET'])
def getPoster():
    imdbID = request.args.get("imdbID")
    size = request.args.get("size")
    if imdbID == None:
        return None 
    url = "https://api.themoviedb.org/3/find/{imdbID}?api_key={TMDB_SECRET}&language=en-US&external_source=imdb_id".format(imdbID=imdbID,TMDB_SECRET=app.config["TMDB_SECRET"])
   
    data = requests.get(url).text
    data = json.loads(data)
    if "movie_results" not in data:
        return "https://d32qys9a6wm9no.cloudfront.net/images/movies/poster/500x735.png"

    data = data["movie_results"]
    if len(data) == 0:
        return "https://d32qys9a6wm9no.cloudfront.net/images/movies/poster/500x735.png"
    data = data[0]
    if size == "small":
       # print("https://image.tmdb.org/t/p/w85"+ data["poster_path"])
        return "https://image.tmdb.org/t/p/w185"+ data["poster_path"]
    
  #  print("https://image.tmdb.org/t/p/w300"+ data["poster_path"])
    return "https://image.tmdb.org/t/p/w185"+ data["poster_path"]
