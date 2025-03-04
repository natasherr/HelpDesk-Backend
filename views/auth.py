from flask import jsonify, request, Blueprint,url_for,session
from model import db, User, TokenBlocklist
from werkzeug.security import check_password_hash
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_mail import  Message
from app import mail
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash
from sqlalchemy_serializer import SerializerMixin

serializer = URLSafeTimedSerializer("SECRET_KEY")

auth_bp = Blueprint("auth_bp", __name__)

# Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password are required"}), 400

    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200

    return jsonify({"error": "Either email or password is incorrect"})


# Login with google
@auth_bp.route("/login_with_google", methods=["POST"])
def login_with_google():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    email = data["email"]

    user = User.query.filter_by(email=email).first()

    if user :
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200

    return jsonify({"error": "Email is incorrect"})


# current user
@auth_bp.route("/current_user", methods=["GET"])
@jwt_required()
def current_user():
    current_user_id  = get_jwt_identity()

    user =  User.query.get(current_user_id)
    user_data = {
            'id':user.id,
            'email':user.email,
            'username':user.username,
            'profile_picture':user.profile_picture
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


@auth_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Generate a password reset token
    token = serializer.dumps(email, salt="password-reset")

    # Create the reset link pointing to the frontend
    reset_link = f"http://localhost:5173/reset-password/{token}"

    # Send the email with the reset link
    msg = Message("Password Reset Request", sender="ashley.testingmoringa@gmail.com", recipients=[email])
    msg.html = f"Click <a href='{reset_link}'>here</a> to reset your password."
    mail.send(msg)

    return jsonify({"message": "Password reset email sent"}), 200



@auth_bp.route('/auth/reset-password/<token>', methods=['POST'])
def reset_password(token):
    data = request.get_json()
    new_password = data.get('password')

    if not new_password:
        return jsonify({"error": "Password is required"}), 400

    try:
        # Verify the token and get the email
        email = serializer.loads(token, salt="password-reset", max_age=1800)  # 30 min expiry
    except:
        return jsonify({"error": "Invalid or expired token"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update the user's password
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Password reset successful"}), 200