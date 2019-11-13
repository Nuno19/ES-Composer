import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_REC_URL = "https://recomendation-service-es.azurewebsites.net/Nuno19/Recomendation_Service/1.0.0/"
    FACEBOOK_APP_ID = '410201056336364'
    FACEBOOK_APP_SECRET = '87ab5869395b2593750e87743d1048cd'
    TMDB_SECRET = 'e01f3f11c30c294d74c63e3f889bf19f'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    UPLOAD_TO_RECOMENDATION=False