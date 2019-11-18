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

    @staticmethod
    def getById(fb_id):
        user = User.query.filter_by(fb_id=fb_id).first()
        return user

    

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
    title = db.Column(db.String(200), unique=True)
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


class MovieWatched(db.Model):
    __tablename__ = 'moviewatched'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), unique=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User")



    imdbID = db.Column(db.String(12), unique=True)

    genres = db.relationship('MovieGenre', backref='movieGen', lazy='dynamic')

    actors = db.relationship('MovieActor', backref='movieAct', lazy='dynamic')


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
    name = db.Column(db.String(300), unique=True)
    movie = db.relationship("MovieWatched")
    movie_id = db.Column(db.Integer, db.ForeignKey('moviewatched.id'), nullable=False)

    def __repr__(self):
        return '<Genre %r>' % self.actor