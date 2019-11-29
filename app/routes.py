from app import app
from app.models import User, MovieLike
import os
from flask import Flask, render_template,request,flash,url_for,redirect,session
import requests
import json
from random import shuffle
from rauth.service import OAuth2Service
from urllib.parse import unquote
import urllib.request



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
        text = requests.get(REC_URL+"getRecommended",{"centID":0})
        files = json.loads(text.text)
        dataList = [json.loads(f["data"]) for f in files]
        shuffle(dataList)
       
        text = requests.get(REC_URL+"getRecommended",{"centID":1})
        files = json.loads(text.text)
        dataList1 = [json.loads(f["data"]) for f in files]
        login = "me" not in session
        return render_template("index.html", list=[dataList[:5],dataList1[:5]],login=login)

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
            result = requests.get(REC_URL+"GetTextRecommended",{"query":l})
            list = json.loads(result.text)
            pack = [json.loads(f["data"]) for f in list ]
            toDict["movies"] = pack[:5]
            toDict["packName"] = l
            toRet.append(toDict)

        print(toRet)
        login = "me" not in session
    return render_template("searchFacebook.html", list=toRet,login=login)


@app.route('/movie/<movie_title>',methods=['GET', 'POST'])
def movie(movie_title):
    if request.method == 'POST':
        if request.form != None:
            print(request.form)
            seat = unquote(request.form.get("seat_select"))
            date = unquote(request.form.get("day"))
            cinema = unquote(request.form.get("cinema"))
            name = unquote(request.form.get("movie_title"))
            print(seat)
            print(date)
            print(cinema)
            return {'date': date, 'asset': {'location': cinema, 'seat': seat, 'name': name} }
            
    if request.method == 'GET':
        movie_details = {}
        movie_details["title"] = "PayON"
        movie_details["description"] = "PayOn is a payment service for xxx.."

        movies = requests.get("https://es-booking-service.herokuapp.com/raimas1996/Booking_Service_test/1.0.0/asset?assetKey=name")
        movies = json.loads(movies.text)

        cinemas = requests.get("https://es-booking-service.herokuapp.com/raimas1996/Booking_Service_test/1.0.0/asset?assetId={\"name\":\"" + movie_title + "\"}&assetKey=location")
        cinemas = json.loads(cinemas.text)

        select = request.args.get("cinema")
        #print(select)

        seats = []

        if select != None:
            
            seats = requests.get("https://es-booking-service.herokuapp.com/raimas1996/Booking_Service_test/1.0.0/asset?assetId={\"name\":\"" + "2012" + "\", \"location\":\"" + select + "\"}&assetKey=seat")
            seats = json.loads(seats.text)

            seats_taken = requests.get("https://es-booking-service.herokuapp.com/raimas1996/Booking_Service_test/1.0.0/booking?bookingId={\"name\":\"" + "2012" + "\", \"location\":\"" + select + "\"}&bookingKey=seat")
            seats_taken = json.loads(seats_taken.text)
            print(seats_taken)

            for seat in seats_taken:
                if seat in seats:
                    seats.remove(seat)
            d = dict()
            d["list"] = seats
            return d
            
        return render_template('movie.html', movie=movie_details, movie_title=movie_title, cinemas=cinemas)


@app.route('/movie',methods=['GET'])
def movie2():
    if request.method == 'GET':
        movie_details = {}
        movie_details["title"] = "PayON"
        movie_details["description"] = "PayON"
    return render_template("movie.html", movie=movie_details)

@app.route('/search',methods=['GET'])
def searchPack():
    if request.method == 'GET':
        query = request.args.get("query")
        if query == "":
            return render_template("index.html", list=[])
        result = requests.get(REC_URL+"GetTextRecommended",{"query":query})
        
        #print(result.text)
        list = json.loads(result.text)
        pack = [json.loads(f["data"]) for f in list ]
    return render_template("index.html", list=[pack[:20]])
        


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


@app.route('/payment',methods=['GET','POST'])
def payment():
    if request.method == 'POST':
        # url = "http://localhost:8040/payment"
        url = "http://localhost:8040/api/payment"
        data = {
            #         "amount": request.form['amount'],
            # "MOVIETITLE": request.form['MOVIETITLE'],
            # "MOVIEPRICE": request.form['MOVIEPRICE']
            # "amount": request.form['amount'],
            "amount":"50",
            "MOVIETITLE": "movtit",
            "MOVIEPRICE": "30",
            "CALLER": "https://127.0.0.1:8000",
        }

        data = requests.post(url,json=data)
        print(data.text)
        print(data)
        return redirect("http://localhost:8040")
    else:
        data = requests.get("http://localhost:8040/api/payment")
        print(data.text)
        return render_template("payment.html")
