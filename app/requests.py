from flask import render_template, flash, url_for, request, redirect, session
import datetime
import random
import sys

from . import app, facebook, models, db, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='Home')


@app.route('/login')
def login():
    redirect_uri = url_for('authorized', _external=True)
    params = {'redirect_uri': redirect_uri}
    return redirect(facebook.get_authorize_url(**params))


@app.route('/login/authorized')
def authorized():
    # check to make sure the user authorized the request
    if not 'code' in request.args:
        flash('You did not authorize the request')
        return redirect(url_for('index'))

    # make a request for the access token credentials using code
    redirect_uri = url_for('authorized', _external=True)
    data = dict(code=request.args['code'], redirect_uri=redirect_uri)

    fb = facebook.get_auth_session(data=data)

    session['access_token'] = fb.access_token

    me = fb.get('/me').json()

    user = models.User.query.filter_by(fb_id=me['id']).first()
    if user is None:
        user = models.User(fb_id=me['id'],
                           accepted=True,
                           creation=datetime.datetime.now(),
                           last_activity=datetime.datetime.now())

        db.session.add(user)
        db.session.commit()

    return redirect(url_for('match_list'))


@app.route('/matchlist')
def match_list():
    if 'access_token' not in session:
        return redirect('/')

    try:
        fb = facebook.get_session(session['access_token'])

        me = fb.get('/me').json()
        frd = fb.get('/me/friends?fields=id,name,picture').json()

        user = models.User.query.filter_by(fb_id=me['id']).first()

        active_matches = []
        history_matches = []

        active = [item for item in user.sended_matches if item.status == 1]
        active += [item for item in user.received_matches if item.status == 1]

        history = [item for item in user.sended_matches if item.status > 1]
        history += [item for item in user.received_matches if item.status > 1]

        active.sort(key=lambda x: x.last_activity, reverse=True)
        history.sort(key=lambda x: x.last_activity, reverse=True)

        if len(active) > 10:
            active = [x for x in active[:10]]

        if len(history) > 10:
            history = [x for x in history[:10]]

        for match in active:
            if match.sender.fb_id == me['id']:
                friend = match.receiver
                action = 1
            else:
                friend = match.sender
                action = 2

            friend_data = [item for item in frd['data'] if item['id'] == friend.fb_id][0]

            active_matches.append(
                {
                    'id': match.id,
                    'name': friend_data['name'],
                    'picture': friend_data['picture']['data']['url'],
                    'date': match.last_activity.strftime('%d %b %Y'),
                    'action': action,
                    'status': match.status
                }
            )

        for match in history:
            if match.sender.fb_id == me['id']:
                friend = match.receiver
                action = 1
            else:
                friend = match.sender
                action = 2

            friend_data = [item for item in frd['data'] if item['id'] == friend.fb_id][0]

            history_matches.append(
                {
                    'id': match.id,
                    'name': friend_data['name'],
                    'picture': friend_data['picture']['data']['url'],
                    'date': match.last_activity.strftime('%d %b %Y'),
                    'action': action,
                    'status': match.status
                }
            )

        return render_template('matchlist.html',
                               title='Match List',
                               active_matches=active_matches,
                               history_matches=history_matches)

    except:  # I know, this is bad
        return render_template('error.html',
                               title='Error',
                               strong='Oh no!',
                               message='Something bad happened when loading this page.')


@app.route('/view')
def view():
    if 'access_token' not in session:
        return redirect('/')

    try:
        fb = facebook.get_session(session['access_token'])

        me = fb.get('/me?fields=id,name,picture').json()
        frd = fb.get('/me/friends?fields=id,name,picture').json()

        match = models.Match.query.filter_by(id=request.args.get('id')).first()

        if match.sender.fb_id != me['id'] and match.receiver.fb_id != me['id']:
            render_template('error.html',
                            title='Error',
                            strong='Hmmm!',
                            message='You do not have permissions to access this page.')

        if match.sender.fb_id == me['id']:
            sender = me
            receiver = [item for item in frd['data'] if item['id'] == match.receiver.fb_id][0]
        else:
            sender = [item for item in frd['data'] if item['id'] == match.sender.fb_id][0]
            receiver = me

        return render_template('view.html',
                               title='View',
                               drawing=match.drawing.name,
                               data=match.data,
                               sender={'name': sender['name'], 'picture': sender['picture']['data']['url']},
                               receiver={'name': receiver['name'], 'picture': receiver['picture']['data']['url']},
                               date=match.last_activity.strftime('%d %b %Y'),
                               status=match.status)

    except:  # I know, this is bad
        return render_template('error.html',
                               title='Error',
                               strong='Oh no!',
                               message='Something bad happened when loading this page.')


@app.route('/draw')
def draw():
    if 'access_token' not in session:
        return redirect('/')

    try:
        fb = facebook.get_session(session['access_token'])

        me = fb.get('/me').json()
        frd = fb.get('/me/friends?fields=id,name,picture,installed').json()

        friends = []
        for friend in frd['data']:
            if 'installed' in friend:
                friends.append(friend)

        drawings = models.Drawing.query.all()
        random.shuffle(drawings)

        _3_drawings = [drawings[0], drawings[1], drawings[2]]

        return render_template('draw.html',
                               title='Draw',
                               user_id=me['id'],
                               friends=friends,
                               drawings=_3_drawings)

    except:  # I know, this is bad
        return render_template('error.html',
                               title='Error',
                               strong='Oh no!',
                               message='Something bad happened when loading this page.')


@app.route('/hit')
def hit():
    if 'access_token' not in session:
        return redirect('/')

    try:
        fb = facebook.get_session(session['access_token'])

        frd = fb.get('/me/friends?fields=id,name,picture').json()

        match = models.Match.query.filter_by(id=request.args.get('id')).first()

        sender = [item for item in frd['data'] if item['id'] == match.sender.fb_id][0]

        return render_template('hit.html',
                               title='Hit',
                               id=match.id,
                               sender={'name': sender['name'], 'picture': sender['picture']['data']['url']},
                               data=match.data,
                               word=match.drawing.name)

    except:
        return render_template('error.html',
                               title='Error',
                               strong='Oh no!',
                               message='Something bad happened when loading this page.')


@app.route('/create', methods=['POST'])
def create():
    if 'access_token' not in session:
        return redirect('/')

    try:
        fb = facebook.get_session(session['access_token'])

        sender = models.User.query.filter_by(fb_id=request.form['user_id']).first()
        receiver = models.User.query.filter_by(fb_id=request.form['friend_id']).first()

        match = models.Match(
            sender_id=sender.id,
            receiver_id=receiver.id,
            drawing_id=int(request.form['drawing_id']),
            data=request.form['data'],
            status=1,
            last_activity=datetime.datetime.now()
        )

        db.session.add(match)
        db.session.commit()

        auth = fb.get('oauth/access_token?grant_type=client_credentials' +
                      '&client_id=%s&client_secret=%s' % (FACEBOOK_APP_ID, FACEBOOK_APP_SECRET))

        trash, token = auth.text.split('=')

        msg = fb.post('/%s/notifications' % receiver.fb_id,
                      data={
                          'access_token': token,
                          'template': '@[%s] started a match with you, play now!' % sender.fb_id,
                          'href': 'home'
                      }).json()

        return redirect('/matchlist')

    except:  # I know, this is bad
        return render_template('error.html',
                               title='Error',
                               strong='Oh no!',
                               message='Something bad happened when loading this page.')


@app.route('/save', methods=['GET'])
def save():
    if 'access_token' not in session:
        return redirect('/')

    try:
        fb = facebook.get_session(session['access_token'])

        match = models.Match.query.filter_by(id=request.args.get('id')).first()

        message = ''

        if int(request.args.get('result')) == 1:
            message = 'hit'
            match.status = 2
        else:
            message = 'missed'
            match.status = 3

        match.last_activity = datetime.datetime.now()

        db.session.add(match)
        db.session.commit()

        auth = fb.get('oauth/access_token?grant_type=client_credentials' +
                      '&client_id=%s&client_secret=%s' % (FACEBOOK_APP_ID, FACEBOOK_APP_SECRET))

        trash, token = auth.text.split('=')

        msg = fb.post('/%s/notifications' % match.sender.fb_id,
                      data={
                          'access_token': token,
                          'template': ('@[%s] ' % match.receiver.fb_id) + message + ' your ' +
                                      match.drawing.name + ' drawing!',
                          'href': 'home'
                      }).json()

        return redirect('/matchlist')

    except:  # I know, this is bad
        return render_template('error.html',
                               title='Error',
                               strong='Oh no!',
                               message='Something bad happened when loading this page.')
