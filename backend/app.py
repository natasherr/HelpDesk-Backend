from flask import Flask, jsonify, request
from flask_migrate import Migrate
from model import db, TokenBlocklist
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_cors import CORS
from flask_mail import Mail
import os




app = Flask(__name__)

CORS(app)
# migration initialization
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///help.db'
migrate = Migrate(app, db)
db.init_app(app)

app.config["SECRET_KEY"] = os.getenv('SECRET_KEY', 'afdgerettyiyuofdbnghj45456')

# Jwt
app.config["JWT_SECRET_KEY"] = "wtfghgdfghfhb" 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] =  timedelta(hours=1)

jwt = JWTManager(app)
jwt.init_app(app)




# Flask mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'ashley.testingmoringa@gmail.com'  
app.config['MAIL_PASSWORD'] ='wksb hzbp lyqu wyxo'  
app.config['MAIL_DEFAULT_SENDER'] = "ashley.testingmoringa@gmail.com"

mail = Mail(app)

from views import *

app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(faq_bp)
app.register_blueprint(notification_bp)
app.register_blueprint(problem_bp)
app.register_blueprint(solution_bp)
app.register_blueprint(tag_bp)
app.register_blueprint(vote_bp)
app.register_blueprint(subscription_bp)


# Callback function to check if a JWT exists in the database blocklist
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None






if __name__ == '__main__':
    app.run(debug=True)
