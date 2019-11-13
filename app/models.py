from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    fb_id = db.Column(db.String(30))
    likes = db.relationship('MovieLike', backref='user', lazy='dynamic')


    def __repr__(self):
        return '<User %r,id=%r>' % (self.name,self.fb_id)

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
