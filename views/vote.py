from flask import jsonify, request, Blueprint
from model import db, Vote, Solution, Notification


vote_bp =Blueprint("vote_bp", __name__)


def create_notification(user_id, message, type, reference_id=None):
    """
    Helper function to create a notification.
    """
    new_notification = Notification(
        user_id=user_id,
        message=message,
        type=type,
        reference_id=reference_id
    )
    db.session.add(new_notification)
    db.session.commit()


@vote_bp.route('/solutions/<int:solution_id>/vote', methods=['POST'])
def create_or_update_vote(solution_id):
    """
    Allow a user to vote (like or dislike) on a solution.
    If the user already voted, update the vote type.
    """
    data = request.get_json()
    user_id = data.get('user_id')  # User submitting the vote
    vote_type = data.get('vote_type')  # 1 for like, -1 for dislike

    if vote_type not in [1, -1]:
        return jsonify({'message': 'Invalid vote type. Use 1 for like or -1 for dislike.'}), 400

    solution = Solution.query.get(solution_id)
    if not solution:
        return jsonify({'message': 'Solution not found'}), 404

    existing_vote = Vote.query.filter_by(user_id=user_id, solution_id=solution_id).first()

    if existing_vote:
        # If the user already voted, update the vote type
        existing_vote.vote_type = vote_type
    else:
        # Otherwise, create a new vote
        new_vote = Vote(user_id=user_id, solution_id=solution_id, vote_type=vote_type)
        db.session.add(new_vote)

    # **Send Notification Only If the Voter is Not the Owner**
    if user_id != solution.user_id:
        message = "Your solution received a like! 👍" if vote_type == 1 else "Your solution received a dislike! 👎"
        create_notification(
            user_id=solution.user_id,
            message=message,
            type="vote",
            reference_id=solution.id
        )

    db.session.commit()
    return jsonify({'message': 'Vote recorded successfully'}), 201


@vote_bp.route('/solutions/<int:vote_id>', methods=['DELETE'])
def remove_vote(vote_id):
    """
    Remove a user's vote from a solution.
    """
    data = request.get_json()
    user_id = data.get('user_id')

    vote = Vote.query.filter_by(user_id=user_id, id=vote_id).first()  
    if not vote:
        return jsonify({'message': 'Vote not found'}), 404

    db.session.delete(vote)
    db.session.commit()
    return jsonify({'message': 'Vote removed successfully'}), 200
