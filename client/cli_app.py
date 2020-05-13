# -*- coding:utf-8 -*-
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import time
from flask import Flask, url_for, session, jsonify
from flask import render_template, redirect
from authlib.integrations.flask_client import OAuth
# from authlib.flask.client import OAuth
from authlib.integrations.flask_client import token_update
from flask_sqlalchemy import SQLAlchemy
from models import OAuth2Token,fetch_token,update_token
from authlib.client import OAuth2Session

from sqlalchemy import create_engine
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = '!secret'
app.config.from_object('config')
db = SQLAlchemy(app)
# oauth = OAuth(app)
# oauth = OAuth(app,fetch_token=fetch_token, update_token=update_token)
oauth = OAuth(app, update_token=update_token)

oauth.register(
    name='o2',
    client_id='1whrxAbdQdVuuX6YpXbXydtY',
    client_secret='9vmVJnuK9mueSpObFiFAPzmyJqCTvpyFb6zFBb4rk2OkYY49',
    request_token_url=None,
    # request_token_params={'expires_in':3600},
    request_token_params=None,
    access_token_url='http://127.0.0.1:5000/oauth/token',
    access_token_params={'include_refresh_token':True},
    authorize_url='http://127.0.0.1:5000/oauth/authorize',
    authorize_params=None,
# authorize_params={'grant_type':'authorization_code refresh_token'},
    api_base_url='http://127.0.0.1:5000',
    # client_kwargs=None,
    client_kwargs={'scope': 'profile'},  # 必须的参数{'scope': ''}
)

@app.route('/')
def homepage():
    user = session.get('user')
    token = session.get('token')
    if token and user:
        exp_at = token.get('expires_at')
        if exp_at < time.time():
            return 'token-过期<a href="/login">重新登录</a>'
    return render_template('home.html', user=user,token=token)


@app.route('/login')
def login():
    user = session.get('user')
    token  = session.get('token')
    tnow = time.time()
    if user and token:
        exp_at  = token.get('expires_at')
        if tnow < exp_at:
            return redirect('/')
        else:
            return redirect('/logout')
            # redirect_uri = url_for('authorize', _external=True)
            # return oauth.o2.authorize_redirect(redirect_uri)
    else:
        redirect_uri = url_for('authorize', _external=True)
        return oauth.o2.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    token = oauth.o2.authorize_access_token()
    print(token)
    # user = oauth.o2.parse_id_token(token)
    # 根据拿到的 token 获取资源
    profile = oauth.o2.get('api/me')
    email = oauth.o2.get('api/email')
    other = oauth.o2.get('api/other')
    other1 = oauth.o2.get('api/scope_email')
    other2 = oauth.o2.get('api/no_scope')
    print('profile',profile.status_code)
    print('email', email.status_code)
    print('other', other.status_code)
    print('other1', other1.status_code)
    print('other2', other2.status_code)


    if other1 and other1.status_code == 200:
        print(other1.json())
    if other2 and other2.status_code == 200:
        print('other2.......',other2.json())

    if other:
        print('other', other.json())

    if email:
        print('email', email.json())
    # print('profile',profile.json())
    # print('profile', profile.text)
    if profile:
        user = profile.json()
    else:
        user = {}
    print('user', user)
    session['user'] = user
    session['token'] = token
    return redirect('/')

@app.route('/api/email')
def get_email():
    # token = oauth.o2.authorize_access_token()
    # token = session.get('token')
    email  = oauth.o2.get('api/me')
    if email:
        return jsonify(email)
    else:
        return '没有资源权限'

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.errorhandler(404)
def error_404():
    return '404'


@app.errorhandler(404)
def miss(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error(e):
    return render_template('500.html'), 500


"""
# 过期后，刷新token。需重建session对象：
session = OAuth2Session(
    client_id='Your Client ID', client_secret='Your Client Secret',
    scope='user:email', state=state, redirect_uri='https://MyWebsite.com/callback'
)
new_tokens = session.refresh_token(
    access_token_url, refresh_token=tokens['refresh_token']
)
print('[Refreshed tokens]:', new_tokens)
"""


@app.route('/refresh_token')
def fresh_token():
    token = session.get('token')
    s = OAuth2Session(
        client_id='1whrxAbdQdVuuX6YpXbXydtY',
        client_secret='9vmVJnuK9mueSpObFiFAPzmyJqCTvpyFb6zFBb4rk2OkYY49',
        scope='profile',
        state="123",
        redirect_uri='http://auth2:7070/authorize'
    )
    new_tokens = s.refresh_token(
        'http://127.0.0.1:5000/oauth/token',
        refresh_token=token['refresh_token']
    )

    return new_tokens


# app.run(port=7070,debug=True,ssl_context=('ca/server.crt','ca/server.key'))
# app.run(port=7070,debug=True,ssl_context='adhoc')
app.run(port=7070,debug=True)