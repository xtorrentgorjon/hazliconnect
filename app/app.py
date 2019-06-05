from flask import Flask, render_template, redirect, url_for, session, request, jsonify, make_response
from flask_oauthlib.client import OAuth
import urllib.request

import datetime

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

VERSION = "0.2.4"
ENVIRONMENT = "test"
RELEASE_TIME = datetime.datetime.now()

PAGE_INFO = {"version":VERSION, "environment":ENVIRONMENT, "release_time":RELEASE_TIME}

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
        PAGE_INFO["rightside_link"] = "logout"
        return render_template('index.html', data=me.data, page_info=PAGE_INFO)
        #return jsonify(me.data)
    PAGE_INFO["rightside_link"] = "index"
    return render_template('not_logged_in.html', page_info=PAGE_INFO)
    #return redirect(url_for('login'))


@app.route('/login')
def login():
    return gitlab.authorize(callback=url_for('authorized', _external=True, _scheme='https'))


@app.route('/logout')
def logout():
    session.pop('gitlab_token', None)
    PAGE_INFO["rightside_link"] = "index"
    return render_template('logout.html', page_info=PAGE_INFO)


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
