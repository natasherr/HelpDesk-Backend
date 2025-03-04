from flask import jsonify, request,redirect,url_for,session
from model import User,db
from app import app, mail
from flask_mail import Message
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint

user_bp = Blueprint("user_bp", __name__)

# fetch users
@user_bp.route("/users", methods=["GET"])
def fetch_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'profile_picture': user.profile_picture
        })
    return jsonify(user_list)

# Add user
@user_bp.route("/users", methods=["POST"])
def add_users():
    data = request.get_json()

    # Validate input data
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    username = data['username']
    email = data['email']
    password = generate_password_hash(data['password'])
    profile_picture = data.get('profile_picture', "https://media.istockphoto.com/id/1337144146/vector/default-avatar-profile-icon-vector.jpg?s=612x612&w=0&k=20&c=BIbFwuv7FxTWvh5S3vB6bkT0Qv8Vn8N5Ffseq84ClGI=")

    check_username = User.query.filter_by(username=username).first()
    check_email = User.query.filter_by(email=email).first()

    if check_username or check_email:
        return jsonify({"error": "Username/email already exists"}), 409

    new_user = User(username=username, email=email, password=password, profile_picture=profile_picture)
    db.session.add(new_user)

    try:
        db.session.commit()
        
        msg = Message(
            subject=f'🎉 Welcome to HelpDesk, {username}! 🎉',
            sender=app.config["MAIL_DEFAULT_SENDER"], 
            recipients=[email],
            html=f"""
            <html>
                <body>
                    <h1 style="color: #4CAF50;">Hello {username}!</h1>
                    <p>🌟 Welcome to HelpDesk! 🌟</p>
                    <p>This is where all your queries will be solved. Feel free to ask any questions you have and don't hesitate to interact with our amazing community!</p>
                    <p>As always, keep it interesting, fun, fruitful, and respectful!</p>
                    <p>We're thrilled to have you on board! 🎊</p>
                    <p>Best Regards,<br>Your HelpDesk Team</p>
                </body>
            </html>
            """
        )
        mail.send(msg)
        return jsonify({"success": "User created successfully!"}), 201

    except Exception as e:
        db.session.rollback()  # Rollback the session in case of an error
        return jsonify({"error": f"Failed to create user: {str(e)}"}), 500


# Update User
@user_bp.route('/update_profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    # Check if new username/email already exists
    if "username" in data:
        existing_user = User.query.filter_by(username=data["username"]).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Username already taken'}), 400
        user.username = data["username"]

    if "email" in data:
        existing_email = User.query.filter_by(email=data["email"]).first()
        if existing_email and existing_email.id != user_id:
            return jsonify({'error': 'Email already in use'}), 400
        user.email = data["email"]

    if "password" in data and data["password"]:
        user.password = generate_password_hash(data["password"])

    if "profile_picture" in data:
        user.profile_picture = data["profile_picture"]

    db.session.commit()
    return jsonify({'success': 'Profile updated successfully'}), 200



# Delete
@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_users(user_id):
    current_user_id = get_jwt_identity()

    if user_id != current_user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "The user you are trying to delete doesn't exist"}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"success": "Deleted successfully"}), 200