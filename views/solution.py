from flask import jsonify, request, Blueprint
from model import db, Solution, Problem, Notification
from flask_jwt_extended import jwt_required, get_jwt_identity

solution_bp =Blueprint("solution_bp", __name__)



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


# Create a Solution
@solution_bp.route('/solutions', methods=['POST'])
@jwt_required()
def create_solution():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    description = data['description']
    tag_id = data['tag_id']
    problem_id = data['problem_id']
    
    # Check if the problem exists
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({'message': 'Problem not found'}), 404
    
    # Create Solution
    new_solution = Solution(
        description=description,
        user_id=current_user_id,
        tag_id=tag_id,
        problem_id=problem_id
    )
    db.session.add(new_solution)
    db.session.commit()  # ✅ Commit first to get the ID

    # Send Notification only if another user posts the solution
    if current_user_id != problem.user_id:
        create_notification(
            user_id=problem.user_id,
            actor_id=current_user_id,
            message="Someone provided a solution to your problem!",
            type="reply",
            reference_id=new_solution.id  # ✅ Now the ID exists
        )

    return jsonify({'message': 'Solution created successfully'}), 201





# Updating
@solution_bp.route('/solutions/<int:solution_id>', methods=['PUT'])
@jwt_required()
def update_solution(solution_id):
    current_user_id = get_jwt_identity()
    solution = Solution.query.get_or_404(solution_id)
    data = request.get_json()

    # Extracting values from data
    description = data.get('description', solution.description)
    tag_id = data.get('tag_id', solution.tag_id)
    problem_id = data.get('problem_id', solution.problem_id)

    check_description = Solution.query.filter_by(description=description).first()

    if check_description:
        return jsonify({"error": "Solution exists"}), 406



    # Update problem details
    solution.description = description
    solution.tag_id = tag_id
    solution.problem_id = problem_id

    db.session.commit()
    return jsonify({"success": "Updated successfully"}), 200




# fetch all
@solution_bp.route('/solutions', methods=['GET'])
def get_solutions():
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    problem_id = request.args.get('problem_id', type=int)
    user_id = request.args.get('user_id', type=int)
    tag_id = request.args.get('tag_id', type=int)
    description = request.args.get('description')



    # Build the query
    query = Solution.query

    # Apply filters
    if problem_id:
        query = query.filter_by(problem_id=problem_id)
    if user_id:
        query = query.filter_by(user_id=user_id)

    # Paginate the results
    solutions = query.paginate(page=page, per_page=per_page)

    # Format the response
    solutions_data = [{
        'id': s.id,
        'user_id': s.user_id,
        'problem_id': s.problem_id,
        'description': s.description,
        'tag_id': s.tag_id
    } for s in solutions.items]

    return jsonify({
        'solutions': solutions_data,
        'total_pages': solutions.pages,
        'current_page': solutions.page,
        'total_solutions': solutions.total
    }), 200




# Get a single solution
@solution_bp.route('/solutions/<int:solution_id>', methods=['GET'])
def get_solution(solution_id):
    solution = Solution.query.get_or_404(solution_id)
    return jsonify({
        'id': solution.id,
        'description': solution.description,
        'user_id': solution.user_id,
        'tag_id': solution.tag_id,
        'problem_id': solution.problem_id,
    }), 200



@solution_bp.route('/solutions/<int:solution_id>/vote', methods=['GET'])
def get_votes_for_solution(solution_id):
    solution = Solution.query.get(solution_id)
    if not solution:
        return jsonify({'message': 'Solution not found'}), 404

    return jsonify(solution.get_vote_counts()), 200


# DELETE
@solution_bp.route("/solutions/<int:solution_id>", methods=["DELETE"])
@jwt_required()
def delete_problem(solution_id):
    current_user_id = get_jwt_identity()
    solution = Solution.query.get(solution_id)
    if not solution:
        return jsonify({"error": "Solution not found"}), 406

    # Restrict deletion to the problem owner
    if solution.user_id != current_user_id:
        return jsonify({"error": "You are not authorized to delete this problem"}), 403



    db.session.delete(solution)
    db.session.commit()
    return jsonify({"success": "Solution deleted successfully"}), 200

