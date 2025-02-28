from flask import jsonify, request, Blueprint
from model import db, Solution, Problem, Notification, Subscription
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

subscription_bp =Blueprint("subscription_bp", __name__)




# Endpoint to subscribe to a problem
@subscription_bp.route('/subscribe', methods=['POST'])
@jwt_required()  # Protect this endpoint with JWT
def subscribe():
    data = request.get_json()
    problem_id = data.get('problem_id')

    # Get the current user's ID from the JWT token
    current_user_id = get_jwt_identity()

    # Check if the problem exists
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({"error": "Problem not found"}), 404

    # Check if the user is already subscribed
    existing_subscription = Subscription.query.filter_by(user_id=current_user_id, problem_id=problem_id).first()
    if existing_subscription:
        return jsonify({"error": "User is already subscribed to this problem"}), 400

    # Create a new subscription
    subscription = Subscription(user_id=current_user_id, problem_id=problem_id, created_at=datetime.utcnow())
    db.session.add(subscription)
    db.session.commit()

    return jsonify({
        "message": "Subscribed successfully",
        "subscription": {
            "id": subscription.id,
            "user_id": subscription.user_id,
            "problem_id": subscription.problem_id,
            "created_at": subscription.created_at.isoformat()
        }
    }), 201


# Endpoint to unsubscribe from a problem
@subscription_bp.route('/unsubscribe/<int:problem_id>', methods=['DELETE'])
@jwt_required()  # Protect this endpoint with JWT
def unsubscribe(problem_id):
    # Get the current user's ID from the JWT token
    current_user_id = get_jwt_identity()

    # Check if the problem exists
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({"error": "Problem not found"}), 404

    # Find the subscription
    subscription = Subscription.query.filter_by(user_id=current_user_id, problem_id=problem_id).first()
    if not subscription:
        return jsonify({"error": "You are not subscribed to this problem"}), 404

    # Delete the subscription
    db.session.delete(subscription)
    db.session.commit()

    return jsonify({"message": "Unsubscribed successfully"}), 200



# Endpoint to get all subscriptions for the current user
@subscription_bp.route('/subscriptions', methods=['GET'])
@jwt_required()  # Protect this endpoint with JWT
def get_subscriptions():
    # Get the current user's ID from the JWT token
    current_user_id = get_jwt_identity()

    # Get all subscriptions for the user
    subscriptions = Subscription.query.filter_by(user_id=current_user_id).all()
    if not subscriptions:
        return jsonify({"error": "No subscriptions found for this user"}), 404

    # Format the response
    subscriptions_data = []
    for sub in subscriptions:
        problem = Problem.query.get(sub.problem_id)
        subscriptions_data.append({
            "subscription_id": sub.id,
            "problem_id": sub.problem_id,
            "problem_description": problem.description,
            "created_at": sub.created_at.isoformat()
        })

    return jsonify(subscriptions_data), 200