from flask import jsonify, request, Blueprint
from model import db, Vote, Solution, Notification
from flask_jwt_extended import jwt_required, get_jwt_identity

vote_bp = Blueprint("vote_bp", __name__)


def create_notification(user_id, actor_id, message, type, reference_id=None, solution_description=None):
    """
    Helper function to create a notification.
    """
    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        message=message,
        type=type,
        reference_id=reference_id,
        solution_description=solution_description  # Include solution description
    )
    db.session.add(notification)

# vote(Add)
@vote_bp.route('/solutions/<int:solution_id>/vote', methods=['POST'])
@jwt_required()
def create_or_update_vote(solution_id):
    """
    Allow a user to vote (like or dislike) on a solution.
    If the user already voted, update the vote type.
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    vote_type = data.get('vote_type')  # 1 for like, -1 for dislike

    # Validate vote type
    if vote_type not in [1, -1]:
        return jsonify({'message': 'Invalid vote type. Use 1 for like or -1 for dislike.'}), 400

    # Check if the solution exists
    # Fetch the solution
    solution = Solution.query.get(solution_id)
    if not solution:
        return jsonify({'message': 'Solution not found'}), 404

    # Check if the user has already voted
    existing_vote = Vote.query.filter_by(user_id=current_user_id, solution_id=solution_id).first()

    if existing_vote:
        # If the user already voted, update the vote type
        existing_vote.vote_type = vote_type
        message = f"Updated vote on your solution to the problem '{solution.problem.description}'."
    else:
        # Otherwise, create a new vote
        new_vote = Vote(user_id=current_user_id, solution_id=solution_id, vote_type=vote_type)
        db.session.add(new_vote)
        if vote_type == 1:
            message = f"Your solution to the problem '{solution.problem.description}' received a like: {solution.description}"
        else:
            message = f"Your solution to the problem '{solution.problem.description}' received a dislike: {solution.description}"

    # Send notification only if the voter is not the owner
    if current_user_id != solution.user_id and message:
        create_notification(
            user_id=solution.user_id,  # Notify the solution owner
            actor_id=current_user_id,  # The user who voted
            message=message,
            type="vote",
            reference_id=solution.id,
            solution_description=solution.description  # Include the solution description
        )

    db.session.commit()
    return jsonify({'message': 'Vote recorded successfully'}), 201



# delete vote
@vote_bp.route('/vote/<int:vote_id>', methods=['DELETE'])
@jwt_required()
def remove_vote(vote_id):
    """
    Allow a user to remove their vote from a solution.
    """
    current_user_id = get_jwt_identity()

    # Find the vote
    vote = Vote.query.get(vote_id)
    if not vote:
        return jsonify({"error": "Vote not found"}), 404

    # Check if the current user is the owner of the vote
    if vote.user_id != current_user_id:
        return jsonify({"error": "You are not authorized to remove this vote"}), 403

    # Delete the vote
    db.session.delete(vote)
    db.session.commit()

    return jsonify({"message": "Vote removed successfully"}), 200



# fetch total number of votes
@vote_bp.route('/solutions/<int:solution_id>/votes', methods=['GET'])
def get_vote_counts(solution_id):
    """
    Get the total number of likes and dislikes for a solution.
    """
    # Check if the solution exists
    solution = Solution.query.get(solution_id)
    if not solution:
        return jsonify({"error": "Solution not found"}), 404

    # Get vote counts
    vote_counts = solution.get_vote_counts()

    return jsonify({
        "solution_id": solution_id,
        "likes": vote_counts["likes"],
        "dislikes": vote_counts["dislikes"]
    }), 200