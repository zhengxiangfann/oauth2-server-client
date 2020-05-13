#coding:utf-8

from flask import Flask, url_for,session,redirect
from authlib.integrations.flask_client import OAuth
# from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hi there hi'

oauth = OAuth(app)

# the following local.aquiferre.com is something in /etc/hosts
# that redirect traffic to 127.0.0.1, it helps when there might
# be session storage conflict between several flask web project
# working on same machine/browser, e.g. oAuth server and client
auth0 = oauth.register(
    name='o2',
    client_id='yChDe7D3OAi6yPWD1kRJgysd',
    client_secret='urE6gU9RkggKNxXmn53aJjJAYvNX7vCDFPTIAyNy0PErrqTe',
    access_token_url='http://127.0.0.1:5000/oauth/token',
    access_token_params=None,
    authorize_url='http://127.0.0.1:5000/oauth/authorize',
    authorize_params=None,
    api_base_url='http://127.0.0.1:5000/api/me',
    client_kwargs={'scope': 'profile'},
)

# o2 = oauth.create_client('o2')

@app.route('/')
def index():
    user = session.get('user')
    if user:
        return """
        <h2>用户:{}</h2>
        <br>
        <a href='/logout'>退出登录</a>
        """.format(user)
    return '<a href="/login">请登录</a>'


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



@app.route('/login')
def login():
    o2 = oauth.create_client('o2')
    redirect_uri = url_for('authorize', _external=True)
    return o2.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    # resp = auth0.authorize_access_token()
    # print(resp)
    #
    # resp = auth0.authorized_response()
    # print(resp)
    # return "success"
    o2 = oauth.create_client('o2')
    print(dir(o2))
    print('o2.token', o2.token)
    print('o2.client_auth_methods', o2.client_auth_methods)
    print('o2.fetch_access_token', o2.fetch_access_token)


    token = o2.authorize_access_token()
    print('o2.parse_id_token', o2.parse_id_token(token))
    # response = auth0.authorize_access_token()
    # print(response)
    # token = response['access_token']
    # print(token)
    # return token
    # print(o2)
    # resp = o2.get('me')
    # profile = resp
    # do something with the token and profile
    print(token)

    # session['user'] = profile.json()
    session['user']= 'zxf'
    return redirect('/')
    # return 'the user is {} </br>And its token from auth server is {}'.format(profile.text, token)

app.run(port=7070, debug=True)
