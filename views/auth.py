from flask import jsonify, request, Blueprint
from model import db, User, TokenBlocklist
from app import oauth, app
from werkzeug.security import check_password_hash
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from authlib.integrations.flask_client import OAuth


auth_bp = Blueprint("auth_bp", __name__)

# app.config['GITHUB_CLIENT_ID'] = "Ov23liRe9UJhRA4BjO11"
# app.config['GITHUB_CLIENT_SECRET'] = "d3de645cc97f0e25080388028ef5385173f0ed93"

# google = oauth.register(
#     name = 'google',
#     client_id = app.config["GOOGLE_CLIENT_ID"],
#     client_secret = app.config["GOOGLE_CLIENT_SECRET"],
#     access_token_url = 'https://accounts.google.com/o/oauth2/token',
#     access_token_params = None,
#     authorize_url = 'https://accounts.google.com/o/oauth2/auth',
#     authorize_params = None,
#     api_base_url = 'https://www.googleapis.com/oauth2/v1/',
#     userinfo_endpoint = 'https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
#     client_kwargs = {'scope': 'openid email profile'},
# )


github = oauth.register (
  name = 'github',
    client_id = app.config["GITHUB_CLIENT_ID"],
    client_secret = app.config["GITHUB_CLIENT_SECRET"],
    access_token_url = 'https://github.com/login/oauth/access_token',
    access_token_params = None,
    authorize_url = 'https://github.com/login/oauth/authorize',
    authorize_params = None,
    api_base_url = 'https://api.github.com/',
    client_kwargs = {'scope': 'user:email'},
)



# # Google login routehttps://youtu.be/ZCDzwYaAKCI?si=_ysFdfjyZO04s-LA
# @auth_bp.route('/login/google')
# def google_login():
#     google = oauth.create_client('google')
#     redirect_uri = url_for('google_authorize', _external=True)
#     return google.authorize_redirect(redirect_uri)


# # Google authorize route
# @auth_bp.route('/login/google/authorize')
# def google_authorize():
#     google = oauth.create_client('google')
#     token = google.authorize_access_token()
#     resp = google.get('userinfo').json()
#     print(f"\n{resp}\n")
#     return "You are successfully signed in using google"


# Github login route
@auth_bp.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    redirect_uri = url_for('github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)


# Github authorize route
@auth_bp.route('/login/github/authorize')
def github_authorize():
    github = oauth.create_client('github')
    token = github.authorize_access_token()
    resp = github.get('user').json()
    print(f"\n{resp}\n")
    return "You are successfully signed in using github"





# Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password ) :
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200

    else:
        return jsonify({"error": "Either email/password is incorrect"}), 404



# current user
@auth_bp.route("/current_user", methods=["GET"])
@jwt_required()
def current_user():
    current_user_id  = get_jwt_identity()

    user =  User.query.get(current_user_id)
    user_data = {
            'id':user.id,
            'email':user.email,
            'username':user.username
        }

    return jsonify(user_data)



# Logout
@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify({"success":"Logged out successfully"})