from flask import Flask, render_template, redirect, url_for, session, request, jsonify, make_response
from flask_oauthlib.client import OAuth
import urllib.request

import datetime

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

VERSION = "0.1.1"
ENVIRONMENT = "test"
RELEASE_TIME = datetime.datetime.now()

gitlab = oauth.remote_app('gitlab',
    base_url='https://gitlab.home.sendotux.net/api/v3/',
    request_token_url=None,
    access_token_url='https://gitlab.home.sendotux.net/oauth/token',
    authorize_url='https://gitlab.home.sendotux.net/oauth/authorize',
    access_token_method='POST',
    consumer_key='9e55b76ff6dc10f29c1d57c9e1ce3faa54ad256149c110e47a16eb81cea9b1ce',
    consumer_secret='8b8ea773b2c6e61ac8a539510ba6e75d4c024c97b922a363f1408c3808007288'
)

@app.route('/')
def index():
    if 'gitlab_token' in session:
        me = gitlab.get('user')
        return render_template('index.html', data=me.data, release_time=RELEASE_TIME, environment=ENVIRONMENT, version=VERSION)
        #return jsonify(me.data)
    return render_template('not_logged_in.html', version=VERSION)
    #return redirect(url_for('login'))


@app.route('/login')
def login():
    return gitlab.authorize(callback=url_for('authorized', _external=True, _scheme='https'))


@app.route('/logout')
def logout():
    session.pop('gitlab_token', None)
    return render_template('logout.html', version=VERSION)


@app.route('/login/authorized')
def authorized():
    resp = gitlab.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['gitlab_token'] = (resp['access_token'], '')
    return redirect(url_for('index'))

@gitlab.tokengetter
def get_gitlab_oauth_token():
    return session.get('gitlab_token')

if __name__ == "__main__":
    app.run(host="0.0.0.0")
