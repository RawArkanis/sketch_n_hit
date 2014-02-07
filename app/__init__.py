from flask import Flask, session
from flask.ext.assets import Environment
from flask.ext.sqlalchemy import SQLAlchemy
from flask_oauth import OAuth
import os

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'SECRET'
FACEBOOK_APP_ID = 'ID'
FACEBOOK_APP_SECRET = 'SECRET'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '../app.db')

app = Flask(__name__)
wa = Environment(app)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
app.secret_key = SECRET_KEY
oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email, publish_stream'}
)

from . import assets, requests, models


@app.before_first_request
def before_first_request():
    try:
        models.db.create_all()
    except Exception, e:
        app.logger.error(str(e))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')
