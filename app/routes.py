from app import app
from app.models import User, MovieLike,MovieWatched,MovieGenre,MovieActor,Movie,Actor,Genre
import os
from flask import Flask, render_template,request,flash,url_for,redirect,session
import requests
import json
from random import shuffle,randint
from rauth.service import OAuth2Service
from urllib.parse import unquote

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

@app.route("/logout",methods=['GET'])
def logout():
    if "id" in session:
        del session["id"]
    if "me" in session:
        del session["me"]
    return redirect(url_for("getRecomended"))

def setWatch(title):
    if "id" not in session:
        return render_template("index.html")
    print("SET WATCH")
    
    m = Movie.getMovieFromTitle(title)
    
    mov = MovieWatched(title=m.title,imdbID=m.imdbID)
    
    mov.addGenres(m.getGenres())
    mov.addActors(m.getActors())
    
    us = User.getById(session["id"])
    
    if not us.isWatched(mov.imdbID):

        us.addWatched(mov)
    
    return redirect(url_for('getRecomended'))


@app.route('/watched',methods=['GET'])
def watched():
    if request.method == 'GET':
        if "id" not in session:
            flash("Not Logged in!")
            return render_template("watched.html")

        user = User.getById(session["id"])
        login = "id" not in session
        return render_template("watched.html",movies = user.getWatched(),login=login)

@app.route('/watchedRecomend',methods=['GET'])
def watchedRecomend():
    if request.method == 'GET':
        if "id" not in session:
            flash("Not Logged in!")
            return render_template("searchFacebook.html")

        watched = MovieWatched.getAllUserWatches(session["id"])

        genList = [gen for gen in [gen.getGenres() for gen in watched]]
        print(genList)
        counts = dict()

        for genres in genList:
            for g in genres:
                if g not in counts.keys():
                    counts[g] = 0
                counts[g] = counts[g] + 1

        counts = sorted(counts.items(), key=lambda x: x[1],reverse=True)

        actList = [act for act in [act.getActors() for act in watched]]
        print(counts)
        countsAct = dict()

        for actors in actList:
            for a in actors:
                if a not in countsAct.keys():
                    countsAct[a] = 0
                countsAct[a] = countsAct[a] + 1

        countsAct = sorted(countsAct.items(), key=lambda x: x[1],reverse=True)

        
        print(countsAct)

        result = requests.get(REC_URL+"GetTextRecommended",{"query":counts[0][0] + " " + counts[1][0]})

        print("TXT"+result.text)
        login = "me" not in session
    return render_template("searchFacebook.html",list=[],login=login)




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
        for d in dataList:
            d["genres"] = d["genres"].split(" ")

        shuffle(dataList)

        login = "me" not in session
        return render_template("index.html",releventMovies=dataList[:3] ,movies=dataList[:24],login=login)


@app.route('/facebookRecomended',methods=['GET'])
def getFromFacebookLikes():
    if request.method == 'GET':
        if "id" not in session:
            flash("Not Logged in!")
            return render_template("searchFacebook.html")

        likes = MovieLike.getAllUserLikes(session["id"])
        shuffle(likes)
        likes = likes[:3]
        titles = [l.title for l in likes]
        toRet = []
        for l in titles:
            toDict = {}
            result = requests.get(REC_URL+"GetTextRecommended",{"query":l})
            list = json.loads(result.text)
            pack = [json.loads(f["data"]) for f in list ]
            toDict["movies"] = pack[:6]
            toDict["packName"] = l
            toRet.append(toDict)

        print(toRet)
        login = "me" not in session
    return render_template("searchFacebook.html",list=toRet,login=login)


@app.route('/booking_confirmation', methods=["GET", "POST"])
def booking_confirmation():
    if request.method == "GET":
        print(request.args)
        print(request.args.get("status"))
        if "status" not in request.args:
            return redirect(url_for('movie',movie_title=session["name"],success=False))
        if request.args.get("status") == "200":
            message = {"200": 'ok'}
            setWatch(session["name"])
            return redirect(url_for('movie',movie_title=session["name"],success="True"))
        else:
            for seat in session['seat']:
                requests.delete("https://es-booking-service.herokuapp.com/raimas1996/Booking_Service_test/1.0.0/booking",
                json = {'userId': session["id"],
                        'bookingDate': session['date'] + "T21:00:00Z",
                        'asset': {'name': session['name'],
                            'location': session['location'], 
                            'seat': seat
                        }
                })
            message = {"500": 'not ok'}
        print(message)
        
        return redirect(url_for('movie',movie_title=session["name"],success="False"))
    return "None"


@app.route('/movie/<movie_title>',methods=['GET', 'POST'])
def movie(movie_title,success=False):
    
    session['name'] = movie_title
    if request.method == 'POST':
        if request.form != None:
            if "id" not in session:
                flash("Not Logged in!")
                return render_template("index.html")
                
            print(request.form)
            date = unquote(request.form.get("day"))
            cinema = unquote(request.form.get("cinema"))
            name = unquote(request.form.get("movie_title"))
            session['seat'] = []

            for seat in request.form:
                if "seat_select" in seat:
                    if requests.get("https://es-booking-service.herokuapp.com/raimas1996/Booking_Service_test/1.0.0/booking?bookingId={\"location\":\"" + cinema + "\", \"name\":\"" + name + "\", \"seat\":\"" + unquote(request.form.get(seat)) + "\"}").content == b'[]\n':
                        requests.post("https://es-booking-service.herokuapp.com/raimas1996/Booking_Service_test/1.0.0/booking",
                        json = {'userId': session["id"],
                                'bookingDate': date + ":00Z",
                                'asset': {'name': name,
                                    'location': cinema, 
                                    'seat': unquote(request.form.get(seat))
                                }
                        })
                        session['seat'].append(unquote(request.form.get(seat)))
            
            session['date'] = date + ":00Z"
            session['name'] = name
            session['location'] = cinema
            
            return redirect(url_for("booking_confirmation", status=200))
            #return redirect(url_for("payment", json={'name': name, 'seat': len(session['seat'])}), code=307)
            
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
        mov = Movie.getMovieFromTitle(movie_title)
        print(mov.__dict__)
        movDict = mov.__dict__
        movDict["actors"] = mov.getActors()
        movDict["genres"] = mov.getGenres()
        imdbID = mov.imdbID
        
        success = request.args.get("success")
        if success == "True":
           flash("Movie {} bougth successfully!".format(mov.title))

        return render_template('movie.html', movie=movDict, movie_title=movie_title, cinemas=cinemas)


@app.route('/seats',methods=['GET', 'POST'])
def seats():
    if request.method == "GET":
        seats = []

        cinema = unquote(request.args.get("cinema"))
        movie_title = unquote(request.args.get("movie_title"))

        seats = requests.get("https://es-booking-service.herokuapp.com/raimas1996/Booking_Service_test/1.0.0/asset?assetId={\"name\":\"" + movie_title + "\", \"location\":\"" + cinema + "\"}&assetKey=seat")
        seats = json.loads(seats.text)

        seats_taken = requests.get("https://es-booking-service.herokuapp.com/raimas1996/Booking_Service_test/1.0.0/booking?bookingId={\"name\":\"" + movie_title + "\", \"location\":\"" + cinema + "\"}&bookingKey=seat")
        seats_taken = json.loads(seats_taken.text)
        print(seats_taken)

        for seat in seats_taken:
            if seat in seats:
                seats.remove(seat)
        d = dict()
        d["list"] = seats
        return d


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
            return render_template("index.html", movies=[])
        result = requests.get(REC_URL+"GetTextRecommended",{"query":query})
        
        print(result.text)
        listM = json.loads(result.text)
        print(listM)
        print(len(listM))
        pack = [json.loads(f["data"]) for f in listM ]
    return render_template("search.html",query=query, movies=pack)
        


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
            "amount":"7",
            "MOVIETITLE": session['name'],
            "MOVIEPRICE": len(session['seat'])*6,
            "CALLER": "https://127.0.0.1:8000/booking_confirmation",
        }

        data = requests.post(url,json=data)
        print(data.text)
        print(data.status_code)
        return redirect('http://localhost:8040')

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

    if size == "medium":
       # print("https://image.tmdb.org/t/p/w85"+ data["poster_path"])
        return "https://image.tmdb.org/t/p/w342"+ data["poster_path"]
    
  #  print("https://image.tmdb.org/t/p/w300"+ data["poster_path"])
    return "https://image.tmdb.org/t/p/w500"+ data["poster_path"]
