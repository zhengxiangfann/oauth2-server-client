import time
from flask import Blueprint, request, session, url_for
from flask import render_template, redirect, jsonify
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2 import current_token
from authlib.oauth2 import OAuth2Error
from .models import db, User, OAuth2Client
from .oauth2 import authorization, require_oauth


bp = Blueprint(__name__,
               'home',
               static_folder='static',
               static_url_path='static',
               template_folder='templates',
               url_prefix='',
               subdomain=None,
               url_defaults='',
               root_path='')
               # cli_group=object())
# bp = Blueprint(__name__,'home', static_folder='static', static_url_path='/auth/static')
def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


def split_by_crlf(s):
    return [v for v in s.splitlines() if v]


@bp.route('/grant_protocol')
def grant_protocol():
    return render_template("grant_protocol.html")

@bp.route('/', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        session['id'] = user.id
        # if user is not just to log in, but need to head back to the auth page, then go for it
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect('/')
    user = current_user()
    if user:
        clients = OAuth2Client.query.filter_by(user_id=user.id).all()
    else:
        clients = []
    return render_template('home1.html', user=user, clients=clients)


@bp.route('/logout')
def logout():
    del session['id']
    return redirect('/')


@bp.route('/create_client', methods=('GET', 'POST'))
def create_client():
    user = current_user()
    if not user:
        return redirect('/')
    if request.method == 'GET':
        return render_template('create_client.html')
    client_id = gen_salt(24)
    client_id_issued_at = int(time.time())
    client = OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        user_id=user.id,
    )
    if client.token_endpoint_auth_method == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)

    form = request.form
    client_metadata = {
        "client_name": form["client_name"],
        "client_uri": form["client_uri"],
        "grant_types": split_by_crlf(form["grant_type"]),
        "redirect_uris": split_by_crlf(form["redirect_uri"]),
        "response_types": split_by_crlf(form["response_type"]),
        "scope": form["scope"],
        "token_endpoint_auth_method": form["token_endpoint_auth_method"]
    }
    client.set_client_metadata(client_metadata)
    db.session.add(client)
    db.session.commit()
    return redirect('/')


@bp.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
    user = current_user()
    # if user log status is not true (Auth server), then to log it in
    if not user:
        return redirect(url_for('website.routes.home', next=request.url))
    if request.method == 'GET':
        try:
            grant = authorization.validate_consent_request(end_user=user)
        except OAuth2Error as error:
            return error.error
        return render_template('authorize1.html', user=user, grant=grant)
    if not user and 'username' in request.form:
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
    if request.form['confirm']:
        # 确认后，可以授权所属的资源了
        grant_user = user
        return authorization.create_authorization_response(grant_user=grant_user)
    else:
        # 拒绝授权,返回原页面
        grant_user = None
        return redirect('/')


@bp.route('/oauth/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()


@bp.route('/oauth/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')


@bp.route('/api/me')
@require_oauth('profile')
def api_me():
    user = current_token.user
    return jsonify(id=user.id, username=user.username)


@bp.route('/api/email')
@require_oauth('profile')
def api_email():
    email  = {'email':'xfzheng@hillinsight.com'}
    return jsonify(email=email)


#受资源保护，
@bp.route('/api/other')
@require_oauth()
def api_other():
    other = {'other':'...other information'}
    return jsonify(other=other)


#受资源保护，但是未授权的，不能访问
@bp.route('/api/scope_email')
@require_oauth('email')
def api_scope_email():
    other = {'other':'...scope_email'}
    return jsonify(other=other)



#未受资源保护的，可以访问
@bp.route('/api/no_scope')
def api_no_limitscope():
    other = {'other':'...no limit no_scope'}
    return jsonify(other=other)



#
# @bp.errorhandler(404)
# def bad_method(error=None):
#     jsonData = request.get_json(cache=False)
#     id = jsonData['id']
#     message = {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": id}
#     resp = jsonify(message)
#     return resp