from app import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    fb_id = db.Column(db.String(30))
    likes = db.relationship('MovieLike', backref='userLike', lazy='dynamic')
    watched = db.relationship('MovieWatched', backref='userWatch', lazy='dynamic')

    def __repr__(self):
        return '<User %r,id=%r>' % (self.name,self.fb_id)

    def addWatched(self,movie):
        mov = MovieWatched.query.filter_by(imdbID=movie.imdbID).filter_by(user_id=self.id).first()
        if mov is None:
            self.watched.append(movie)
            db.session.add(movie)
            db.session.commit()

    def addLike(self,movie):
        mov = MovieLike.query.filter_by(title=movie.title).filter_by(user_id=self.id).first()
        if mov is None:
            self.likes.append(movie)
            db.session.add(movie)
            db.session.commit()

    def isWatched(self,imdbID):
        return MovieWatched.query.filter_by(imdbID=imdbID).filter_by(user_id=self.id).first() != None

    @staticmethod
    def getById(fb_id):
        user = User.query.filter_by(fb_id=fb_id).first()
        return user

    def getWatched(self):
        return [mov.__dict__ for mov in MovieWatched.query.filter_by(user_id=self.id).all()]

    @staticmethod
    def get_or_create(name, fb_id):
        user = User.query.filter_by(fb_id=fb_id).first()
        if user is None:
            user = User(name=name, fb_id=fb_id)
            db.session.add(user)
            db.session.commit()
        return user


class MovieLike(db.Model):
    __tablename__ = 'movieliked'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User")

    def __repr__(self):
        return '<MovieLike %r>' % self.title


    @staticmethod
    def getAllUserLikes(fb_id):
        user = User.query.filter_by(fb_id=fb_id).first()
        if user is None:
            return None
        return MovieLike.query.filter_by(user_id=user.id).all()

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), unique=False)
    
    imdbID = db.Column(db.String(12), unique=True)

    director = db.Column(db.String(300), unique=False)

    year = db.Column(db.String(5), unique=False)

    genres = db.relationship('Genre', backref='genreMov', lazy='dynamic')

    actors = db.relationship('Actor', backref='actorMov', lazy='dynamic')


    def getGenres(self):
        return [gen.genre for gen in self.genres]
    
    def getActors(self):
        return [act.name for act in self.actors]

    def __repr__(self):
        return '<Movie %r, Id: %s , Year: %s>' % (self.title,self.imdbID,self.year)

    def addGenres(self,genres):
        genresList = []
        
        for gen in genres:
            genresList.append(Genre(genre=gen))
        
        self.genres.extend(genresList)

    def addActors(self,actors):
        actorsList = []
       
        for act in actors:
            actorsList.append(Actor(name=act))
        
        self.actors.extend(actorsList)

    @staticmethod
    def getMovieFromTitle(title):
        return Movie.query.filter_by(title=title).first()
    
    @staticmethod
    def getMovieFromImdbID(imdbID):
        return Movie.query.filter_by(imdbID=imdbID).first()



class MovieWatched(db.Model):
    __tablename__ = 'moviewatched'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), unique=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User")

    imdbID = db.Column(db.String(12), unique=True)

    date = db.Column(db.String(20), unique=False)
    time = db.Column(db.String(10), unique=False)
    cinema = db.Column(db.String(300), unique=False)

    genres = db.relationship('MovieGenre', backref='movieGen', lazy='dynamic')

    actors = db.relationship('MovieActor', backref='movieAct', lazy='dynamic')


    def getGenres(self):
        return [gen.genre for gen in self.genres]
    
    def getActors(self):
        return [act.name for act in self.actors]

    def __repr__(self):
        return '<MovieWatched %r>' % self.title

    def addGenres(self,genres):
        genresList = []
        
        for gen in genres:
            genresList.append(MovieGenre(genre=gen))
        
        self.genres.extend(genresList)

    def addActors(self,actors):
        actorsList = []
       
        for act in actors:
            actorsList.append(MovieActor(name=act))
        
        self.actors.extend(actorsList)

    @staticmethod
    def getAllUserWatches(fb_id):
        user = User.query.filter_by(fb_id=fb_id).first()
        if user is None:
            return None
        return MovieWatched.query.filter_by(user_id=user.id).all()



class MovieGenre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(50), unique=False)
    movie = db.relationship("MovieWatched")
    movie_id = db.Column(db.Integer, db.ForeignKey('moviewatched.id'), nullable=False)

    def __repr__(self):
        return '<Genre %r>' % self.genre


class MovieActor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), unique=False)
    movie = db.relationship("MovieWatched")
    movie_id = db.Column(db.Integer, db.ForeignKey('moviewatched.id'), nullable=False)

    def __repr__(self):
        return '<Genre %r>' % self.actor




class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(50), unique=False)
    movie = db.relationship("Movie")
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

    def __repr__(self):
        return '<Genre %r>' % self.genre


class Actor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), unique=False)
    movie = db.relationship("Movie")
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

    def __repr__(self):
        return '<Genre %r>' % self.actor