from flask import jsonify, request, Blueprint
from model import db, Problem, User
from flask_jwt_extended import jwt_required, get_jwt_identity

problem_bp =Blueprint("problem_bp", __name__)


@problem_bp.route("/problems", methods=["POST"])
@jwt_required()
def add_problem():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    description = data['description']
    tag_id = data['tag_id']

    if not description:
        return jsonify({"error": "description is required"}), 400

    check_description =Problem.query.filter_by(description=description).first()
   
    if check_description:
        return jsonify({"error":"Problem exists"}),406

    else:
        new_problem = Problem(description=description, user_id=current_user_id, tag_id=tag_id )
        db.session.add(new_problem)
        db.session.commit()
        return jsonify({"success":"Problem added successfully"}), 201





@problem_bp.route('/problems/<int:problem_id>', methods=['PUT'])
@jwt_required()
def update_problem(problem_id):
    current_user_id = get_jwt_identity()
    problem = Problem.query.get_or_404(problem_id)

    # Restrict update to the problem owner
    if problem.user_id != current_user_id:
        return jsonify({"error": "You are not authorized to edit this problem"}), 403

    data = request.get_json()

    # Extracting values from data
    description = data.get('description', problem.description)
    tag_id = data.get('tag_id', problem.tag_id)

    # Check if the new description already exists in another problem
    check_description = Problem.query.filter_by(description=description).first()

    if check_description and check_description.id != problem.id:
        return jsonify({"error": "Problem exists"}), 406

    # Update problem details
    problem.description = description
    problem.tag_id = tag_id

    db.session.commit()
    return jsonify({"success": "Updated successfully"}), 200



# DELETE
@problem_bp.route("/problems/<int:problem_id>", methods=["DELETE"])
@jwt_required()
def delete_problem(problem_id):
    current_user_id = get_jwt_identity()
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({"error": "Problem not found"}), 406

    # Restrict deletion to the problem owner
    if problem.user_id != current_user_id:
        return jsonify({"error": "You are not authorized to delete this problem"}), 403



    db.session.delete(problem)
    db.session.commit()
    return jsonify({"success": "Problem deleted successfully"}), 200




@problem_bp.route('/problems', methods=['GET'])
def get_problems():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    
    problems = Problem.query.join(User).add_columns(
        Problem.id, Problem.description, Problem.tag_id, Problem.user_id,
        User.username.label("username")
    ).paginate(page=page, per_page=per_page)

    
    problems_data = [{
        'id': p.id,
        'description': p.description,
        'tag_id': p.tag_id,
        'user': {
            "id": p.user_id,
            "username": p.username,  
        }
    } for p in problems.items]

    return jsonify({
        'problems': problems_data,
        'total_pages': problems.pages,
        'current_page': problems.page,
        'total_problems': problems.total
    }), 200



# Get a single problem
@problem_bp.route('/problems/<int:problem_id>', methods=['GET'])
def get_problem(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    return jsonify({
        'id': problem.id,
        'description': problem.description,
        'user_id': problem.user_id,
        'tag_id': problem.tag_id,
    }), 200

    