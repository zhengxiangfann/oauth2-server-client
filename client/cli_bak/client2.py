from flask import Flask, url_for
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hi there hi'

oauth = OAuth(app)

# the following local.aquiferre.com is something in /etc/hosts
# that redirect traffic to 127.0.0.1, it helps when there might
# be session storage conflict between several flask web project
# working on same machine/browser, e.g. oAuth server and client
oauth.register(
    name='o2',
    client_id='KPO60jah9Y9eXMX6JNNaQDqk',
    client_secret='OhlxEo9mBVqeNQhYu84QTmgD9nIgF2K56MoFFdEpAhFp7ouy',
    access_token_url='http://auth2:5000/oauth/token',
    access_token_params={'grant_type':'authorization_code'},
    authorize_url='http://auth2:5000/oauth/authorize',
    authorize_params=None,
    api_base_url='http://auth2:5000/api/me',
    client_kwargs={'scope': 'profile'},
    code_challenge_method='S256',
)

# o2 = oauth.create_client('o2')

@app.route('/')
def index():
    return 'hi there'

@app.route('/login')
def login():
    o2 = oauth.create_client('o2')
    redirect_uri = url_for('authorize', _external=True)
    return o2.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    o2 = oauth.create_client('o2')
    token = o2.authorize_access_token()
    resp = o2.get('me')
    profile = resp
    # do something with the token and profile
    # print(token)
    return 'the user is {} </br>And its token from auth server is {}'.format(profile.text, token)

app.run(port=7070, debug=True)