from flask import Flask
from flask.ext.assets import Environment
from flask.ext.sqlalchemy import SQLAlchemy
from rauth.service import OAuth2Service
import os

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'MY_SECRET'
FACEBOOK_APP_ID = '595127900566216'
FACEBOOK_APP_SECRET = 'APP_SECRET'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '../app.db')

app = Flask(__name__)
wa = Environment(app)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
app.secret_key = SECRET_KEY

facebook = OAuth2Service(
    name='facebook',
    base_url='https://graph.facebook.com/',
    access_token_url='https://graph.facebook.com/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    client_id=FACEBOOK_APP_ID,
    client_secret=FACEBOOK_APP_SECRET
)

from . import assets, requests, models
