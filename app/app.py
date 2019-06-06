from flask import Flask, render_template, redirect, url_for, session, request, jsonify, make_response
from flask_oauthlib.client import OAuth
from pygelf import GelfUdpHandler
import urllib.request

import datetime
import logging
import os

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

VERSION = "0.2.4"
ENVIRONMENT = "test"
RELEASE_TIME = datetime.datetime.now()

PAGE_INFO = {"version":VERSION,
            "environment":ENVIRONMENT,
            "release_time":str(RELEASE_TIME)}

LOG_PARAM = {"ip":os.environ["LOG_ENDPOINT_IP"],
            "port":int(os.environ["LOG_ENDPOINT_PORT"])}

OAUTH_PARAM = {"url":os.environ["OAUTH_GITLAB_URL"],
                "key":os.environ["OAUTH_GITLAB_KEY"],
                "secret":os.environ["OAUTH_GITLAB_SECRET"]}

logging.basicConfig(level=logging.INFO)
gelflogger = logging.getLogger()
gelflogger.addHandler(GelfUdpHandler(host=LOG_PARAM["ip"], port=LOG_PARAM["port"]))
gelflogger.info('Starting Hazliconnect {}'.format(VERSION))


gitlab = oauth.remote_app('gitlab',
    base_url='{}/api/v3/'.format(OAUTH_PARAM["url"]),
    request_token_url=None,
    access_token_url='{}/oauth/token'.format(OAUTH_PARAM["url"]),
    authorize_url='{}/oauth/authorize'.format(OAUTH_PARAM["url"]),
    access_token_method='POST',
    consumer_key='{}'.format(OAUTH_PARAM["key"]),
    consumer_secret='{}'.format(OAUTH_PARAM["secret"])
)

@app.route('/')
def index():
    if 'gitlab_token' in session:
        me = gitlab.get('user')
        PAGE_INFO["rightside_link"] = "logout"
        gelflogger.info('New client reaching the index page!')
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
