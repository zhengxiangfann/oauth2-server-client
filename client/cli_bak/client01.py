from flask import Flask, url_for, session
from flask import render_template, redirect
from authlib.integrations.flask_client import OAuth


app = Flask(__name__)
app.secret_key = '!secret'
# app.config.from_object('config')

# CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='hi',
    client_id='iR2hOZ5mtox9sV9wA7Mf32HK',
    client_secret='v2UHC8ixsthtQcxODys9K3Gvvx3zd23jWjM47PhkMUr8HYb1',
    access_token_url='http://127.0.0.1:5000/oauth/token',
    access_token_params=None,
    authorize_url='http://127.0.0.1:5000/oauth/authorize',
    authorize_params=None,
    api_base_url='http://127.0.0.1:5000/api/me',
    client_kwargs={'scope': 'profile'},
)


@app.route('/')
def homepage():
    user = session.get('user')
    return render_template('home.html', user=user)


@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.hi.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():

    token = oauth.hi.authorize_access_token()
    print(token)
    user = oauth.hi.parse_id_token(token)
    session['user'] = user
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


app.run(port=7070,debug=True)