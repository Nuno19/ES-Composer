"""from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker"""
import json
from flask_sqlalchemy import SQLAlchemy



#Base = declarative_base()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    fb_id = db.Column(db.String(120))

    def __init__(self, username, fb_id):
        self.username = username
        self.fb_id = fb_id

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def get_or_create(username, fb_id):
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User(username, fb_id)
            db.session.add(user)
            db.session.commit()
        return user



"""

class MovieLiked(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    imdbID = Column(String(10), nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship("User", back_populates="likes")

    def __repr__(self):
         return "<Like(Title='%s',imdbID='%s')>" % (self.title , self.imdbID)


    
    def __repr__(self):
         return "<Like(Title='%s',imdbID='%s')>" % (self.title , self.imdbID)


class User(Base):
    __tablename__ = 'user'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    fb_id = Column(String(50),nullable=False)
    name = Column(String(250), nullable=False)
    likes = relationship("MovieLiked", back_populates="user")

    def __repr__(self):
         return "<User(Name='%s',fbId='%s')>" % (self.name , self.fb_id)



class DataBase:
    def __init__(self):
        self.engine = create_engine('sqlite:///sqlalchemy_example.db')
        Base.metadata.create_all(self.engine)
        DBSession = sessionmaker(bind=self.engine)
        self.sess = DBSession()

    def addUser(self,name,fb_id):
        user = self.sess.query(User).filter(User.fb_id==fb_id).one()
        if user != None:
            return user

        new_user = User(name=name,fb_id=fb_id)
        self.sess.add(new_user)
        self.sess.commit()
        return new_user

    def getUser(self,fb_id):
        return self.sess.query(User).filter(User.fb_id==fb_id).one()
    
    def getUserLikes(self,fb_id):
        user = self.sess.query(User).filter(User.fb_id==fb_id).one()
        return user.likes
        

    def addUserLikes(self,fb_id,likes):
        user = self.sess.query(User).filter(User.fb_id==fb_id).one()
        if user == None:
            return False

        user.likes = [MovieLiked(title=title) for title in likes]
       
        self.sess.commit()
        return user
"""