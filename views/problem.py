from flask import jsonify, request, Blueprint
from model import db, Problem

problem_bp =Blueprint("problem_bp", __name__)


@problem_bp.route("/problems", methods=["POST"])
def add_problem():
    data = request.get_json()
    description = data['description']
    user_id = data['user_id']
    tag_id = data['tag_id']

    if not description:
        return jsonify({"error": "description is required"}), 400

    check_description =Problem.query.filter_by(description=description).first()
   
    if check_description:
        return jsonify({"error":"Problem exists"}),406

    else:
        new_problem = Problem(description=description, user_id=user_id, tag_id=tag_id )
        db.session.add(new_problem)
        db.session.commit()
        return jsonify({"success":"Problem added successfully"}), 201





@problem_bp.route('/problems/<int:problem_id>', methods=['PUT'])
def update_problem(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    data = request.get_json()

    # Extracting values from data
    user_id = data.get('user_id', problem.user_id)
    description = data.get('description', problem.description)
    tag_id = data.get('tag_id', problem.tag_id)

    # Check if the new description already exists in another problem
    check_description = Problem.query.filter_by(description=description).first()

    if check_description and check_description.id != problem.id:
        return jsonify({"error": "Problem exists"}), 406

    # Update problem details
    problem.description = description
    problem.user_id = user_id
    problem.tag_id = tag_id

    db.session.commit()
    return jsonify({"success": "Updated successfully"}), 200



# DELETE
@problem_bp.route("/problems/<int:problem_id>", methods=["DELETE"])
def delete_problem(problem_id):
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({"error": "Problem not found"}), 406


    db.session.delete(problem)
    db.session.commit()
    return jsonify({"success": "Problem deleted successfully"}), 200




# Get all problems (with pagination)
@problem_bp.route('/problems', methods=['GET'])
def get_problems():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    problems = Problem.query.paginate(page=page, per_page=per_page)
    problems_data = [{
        'id': p.id,
        'description': p.description,
        'user_id': p.user_id,
        'tag_id': p.tag_id,
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

    