from flask import jsonify, request, Blueprint
from model import User,db
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp =Blueprint("user_bp", __name__)


# fetch users
@user_bp.route("/users", methods=["GET"])
def fetch_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email
        })
    return jsonify(user_list)

# Add user
@user_bp.route("/users", methods=["POST"])
def add_users():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = generate_password_hash(data['password']) 

    check_username = User.query.filter_by(username=username).first()
    check_email = User.query.filter_by(email=email).first()

    # print("Email", check_email)
    # print("Username", check_username)

    if check_username or check_email:
        return jsonify({"error":"Username/email exists"}), 404

    else:
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": "Added successfully"}), 201
    



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
        return jsonify({"error": "User you are trying to delete doesn't exist"}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"success": "Deleted successfully"}), 200