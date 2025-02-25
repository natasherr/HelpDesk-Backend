from flask import jsonify, request, Blueprint
from model import db, Vote, Solution, Notification
from flask_jwt_extended import jwt_required, get_jwt_identity


vote_bp =Blueprint("vote_bp", __name__)


def create_notification(user_id, actor_id, message, type, reference_id=None):
    """
    Helper function to create a notification.
    """
    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        message=message,
        type=type,
        reference_id=reference_id
    )
    db.session.add(notification)
    db.session.commit()


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

    if vote_type not in [1, -1]:
        return jsonify({'message': 'Invalid vote type. Use 1 for like or -1 for dislike.'}), 400

    solution = Solution.query.get(solution_id)
    if not solution:
        return jsonify({'message': 'Solution not found'}), 404

    existing_vote = Vote.query.filter_by(user_id=current_user_id, solution_id=solution_id).first()

    if existing_vote:
        # If the user already voted, update the vote type
        existing_vote.vote_type = vote_type
    else:
        # Otherwise, create a new vote
        new_vote = Vote(user_id=current_user_id, solution_id=solution_id, vote_type=vote_type)
        db.session.add(new_vote)

    # **Send Notification Only If the Voter is Not the Owner**
    if current_user_id != solution.user_id:
        message = "Liked your solution!" if vote_type == 1 else "Disliked your solution!"
        create_notification(
            user_id=solution.user_id,
            actor_id=current_user_id,
            message=message,
            type="vote",
            reference_id=solution.id
        )

    db.session.commit()
    return jsonify({'message': 'Vote recorded successfully'}), 201



# DELETE
@vote_bp.route("/solutions/<int:vote_id>/vote", methods=["DELETE"])
@jwt_required()
def delete_vote(vote_id):
    current_user_id = get_jwt_identity()
    vote = Vote.query.get(vote_id)
    if not vote:
        return jsonify({"error": "Vote not found"}), 406

    # Restrict deletion to the problem owner
    if vote.user_id != current_user_id:
        return jsonify({"error": "You are not authorized to delete this vote"}), 403



    db.session.delete(vote)
    db.session.commit()
    return jsonify({"success": "Vote deleted successfully"}), 200



    


