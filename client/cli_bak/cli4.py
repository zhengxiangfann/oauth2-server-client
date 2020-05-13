from flask import Flask, session, render_template, url_for, redirect
from authlib.integrations.flask_client import OAuth

from authlib.client import OAuth2Session


app = Flask(__name__)
app.secret_key = '!secret'

oauth = OAuth(app)


app.config["GITHUB_CLIENT_ID"] = 'kB8xkspealiJhSaMFcMTEoRe'
app.config["GITHUB_CLIENT_SECRET"] = '5orywR4dQs9qXYX7gBabrisJUXT0R1bph3rwDRUxolOG2DW2'
app.config["GITHUB_AUTHORIZE_URL"] = 'http://127.0.0.1:5000/oauth/authorize'
app.config["GITHUB_ACCESS_TOKEN_URL"] = 'http://127.0.0.1:5000/oauth/access_token'
app.config["GITHUB_API_BASE_URL"] = 'http://127.0.0.1:5000/api/me'
app.config["GITHUB_AUTHORIZE_PARAMS"] = {
    'scope': 'profile'
}
oauth.register('GITHUB')

github = oauth.GITHUB

@app.route('/')
def homepage():
    user = session.get('user')
    print('auth user:', user)
    return render_template('home.html', user=user)


@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return github.authorize_redirect(redirect_uri)

@app.route('/auth/redirect')
def auth():
    # print('github',github)
    # print(dir(github))
    # token = github.authorize_access_token()

    o2 = oauth.create_client('GITHUB')
    # session['user'] = 'zxf'
    # return redirect('/')


    github  = oauth.create_client('GITHUB')
    resp = github.authorize_access_token()
    print(resp)
    token=dict(a=1)

    # token = github.authorize_access_token()
    print('auth token:', token)
    user = github.get('user').json()
    print('auth user:', user)
    session['user'] = user
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(port=7070)