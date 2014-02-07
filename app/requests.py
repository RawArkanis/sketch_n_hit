from flask import render_template, url_for, session, request, redirect
import datetime

from . import app, facebook, models, db

@app.route('/')
def index():
    return render_template('index.html', title='Home')


@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
                              next=request.args.get('next') or request.referrer or None,
                              _external=True))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    session['oauth_token'] = (resp['access_token'], '')

    me = facebook.get('/me')

    user = models.User.query.filter_by(fb_id=me.data['id']).first()
    if user is None:
            user = models.User(fb_id=me.data['id'],
                               accepted=True,
                               creation=datetime.datetime.now(),
                               last_activity=datetime.datetime.now())
            db.session.add(user)
            db.session.commit()

    return redirect('matchlist')


@app.route('/matchlist')
def match_list():
    frd = facebook.get('/me/friends')
    return render_template('matchlist.html', title='Match List')


@app.route('/creatematch')
def create_match():
    frd = facebook.get('/me/friends')
    return 'done'


@app.route('/viewmatch')
def view_match():
    frd = facebook.get('/me/friends')
    return 'done'


@app.route('/playmatch')
def play_match():
    frd = facebook.get('/me/friends')
    return 'done'
