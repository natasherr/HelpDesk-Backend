from flask import jsonify, request, Blueprint
from model import db, Problem, Solution, User, Tag  
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

    # Fetch problems with user and tag details
    problems = Problem.query.join(User).outerjoin(Tag).add_columns(
        Problem.id, Problem.description, Problem.tag_id, Problem.user_id,
        User.username.label("username"), Tag.id.label("tag_id"), Tag.name.label("tag_name")
    ).paginate(page=page, per_page=per_page)

    # Fetch all solutions for the problems, including user details
    problem_ids = [p.id for p in problems.items]
    solutions = (
        Solution.query
        .filter(Solution.problem_id.in_(problem_ids))
        .join(User)  # Join User to get solution author
        .outerjoin(Tag)  # Keep outerjoin for optional tags
        .add_columns(
            Solution.id, Solution.description, Solution.problem_id, Solution.user_id,
            User.username.label("solution_author"),  # Get username of solution owner
            Tag.id.label("tag_id"), Tag.name.label("tag_name")
        )
        .all()
    )

    # Group solutions by problem_id to prevent duplication
    solutions_by_problem = {}
    seen_solution_ids = set()  # Track seen solutions to prevent duplicates

    for s in solutions:
        if s.id not in seen_solution_ids:  # Ensure uniqueness
            if s.problem_id not in solutions_by_problem:
                solutions_by_problem[s.problem_id] = []

            solutions_by_problem[s.problem_id].append({
                "id": s.id,
                "description": s.description,
                "user": {  # Include user who posted the solution
                    "id": s.user_id,
                    "username": s.solution_author
                },
                "tag": {
                    "id": s.tag_id,
                    "name": s.tag_name
                } if s.tag_id else None
            })

            seen_solution_ids.add(s.id)  # Mark this solution as added

    # Format the problems data
    problems_data = [{
        'id': p.id,
        'description': p.description,
        'tag': {
            "id": p.tag_id,
            "name": p.tag_name
        } if p.tag_id else None,
        'user': {
            "id": p.user_id,
            "username": p.username,
        },
        'solutions': solutions_by_problem.get(p.id, [])  # Attach solutions
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

