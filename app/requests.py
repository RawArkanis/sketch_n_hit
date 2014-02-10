from flask import render_template, url_for, session, request, redirect
import datetime
import random

from . import app, facebook, models, db


@app.route('/')
@app.route('/home')
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
    if 'oauth_token' not in session:
        return redirect('/')

    try:
        me = facebook.get('/me')
        frd = facebook.get('/me/friends?fields=id,name,picture')

        user = models.User.query.filter_by(fb_id=me.data['id']).first()

        active_matches = []
        history_matches = []

        active = [item for item in user.sended_matches if item.status == 1]
        active += [item for item in user.received_matches if item.status == 1]

        history = [item for item in user.sended_matches if item.status > 1]
        history += [item for item in user.received_matches if item.status > 1]

        active.sort(key=lambda x: x.last_activity, reverse=True)
        history.sort(key=lambda x: x.last_activity, reverse=True)

        if len(active) > 10:
            active = [x for x in active[:5]]

        if len(history) > 10:
            history = [x for x in history[:5]]

        for match in active:
            if match.sender.fb_id == me.data['id']:
                friend = match.receiver
                action = 1
            else:
                friend = match.sender
                action = 2

            friend_data = [item for item in frd.data['data'] if item['id'] == friend.fb_id][0]

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
            if match.sender.fb_id == me.data['id']:
                friend = match.receiver
                action = 1
            else:
                friend = match.sender
                action = 2

            friend_data = (item for item in frd.data.data if item['id'] == friend.fb_id)

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
    if 'oauth_token' not in session:
        return redirect('/')

    try:
        me = facebook.get('/me?fields=id,name,picture')
        frd = facebook.get('/me/friends?fields=id,name,picture')

        match = models.Match.query.filter_by(id=request.args.get('id')).first()

        if match.sender.fb_id != me.data['id'] and match.receiver.fb_id != me.data['id']:
            render_template('error.html',
                            title='Error',
                            strong='Hmmm!',
                            message='You do not have permissions to access this page.')

        if match.sender.fb_id == me.data['id']:
            sender = me.data
            receiver = [item for item in frd.data['data'] if item['id'] == match.receiver.fb_id][0]
        else:
            sender = [item for item in frd.data['data'] if item['id'] == match.sender.fb_id][0]
            receiver = me.data

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
    if 'oauth_token' not in session:
        return redirect('/')

    try:
        me = facebook.get('/me')
        frd = facebook.get('/me/friends?fields=id,name,picture,installed')

        friends = []
        for friend in frd.data['data']:
            if 'installed' in friend:
                friends.append(friend)

        drawings = models.Drawing.query.all()
        random.shuffle(drawings)

        _3_drawings = [drawings[0], drawings[1], drawings[2]]

        return render_template('draw.html',
                               title='Draw',
                               user_id=me.data['id'],
                               friends=friends,
                               drawings=_3_drawings)

    except:  # I know, this is bad
        return render_template('error.html',
                               title='Error',
                               strong='Oh no!',
                               message='Something bad happened when loading this page.')


@app.route('/hit')
def hit():
    if 'oauth_token' not in session:
        return redirect('/')

    frd = facebook.get('/me/friends')
    return 'done'


@app.route('/create', methods=['POST'])
def create():
    try:
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

        msg = facebook.get('/%s/notifications?access_token=%s&template=%s&href=%s' % (receiver.fb_id,
                           session['oauth_token'], '@{%s} started a match with you, play now!' % receiver.fb_id,
                           'home'))

        return redirect('/matchlist')

    except:  # I know, this is bad
        return render_template('error.html',
                               title='Error',
                               strong='Oh no!',
                               message='Something bad happened when loading this page.')

