from flask import jsonify, request, Blueprint
from model import  db, Tag

tag_bp =Blueprint("tag_bp", __name__)



@tag_bp.route("/tags", methods=["POST"])
def add_tag():
    data = request.get_json()
    name = data['name']

    if not name:
        return jsonify({"error": "Name is required"}), 400

    check_name =Tag.query.filter_by(name=name).first()
   
    if check_name:
        return jsonify({"error":"Tag exists"}),406

    else:
        new_tag = Tag(name=name)
        db.session.add(new_tag)
        db.session.commit()
        return jsonify({"success":"Tag added successfully"}), 201




# READ - Get All Tags
@tag_bp.route("/tags", methods=["GET"])
def get_tags():
    tags = Tag.query.all()
    tags_list = [{"id": tag.id, "name": tag.name} for tag in tags]
    return jsonify(tags_list), 200


# Read - Get tad solution
@tag_bp.route("/tags/<int:tag_id>/solutions", methods=["GET"])
def get_solutions_by_tag(tag_id):
    tag = Tag.query.get(tag_id)
    
    if not tag:
        return jsonify({"error": "Tag not found"}), 404

    solutions_list = [
        {
            "id": solution.id,
            "description": solution.description,
            "problem": {
                "id": solution.problem.id,
                "description": solution.problem.description
            } if solution.problem else None
        }
        for solution in tag.solutions  # Fetching only solutions related to this tag
    ]

    return jsonify(solutions_list), 200



# Read - Get Tag by ID
@tag_bp.route("/tags/<int:tag_id>", methods=["GET"])
def get_tag(tag_id):
    tag = Tag.query.get(tag_id)
    if not tag:
        return jsonify({"error": "Tag not found"}), 406
    return jsonify({"id": tag.id, "name": tag.name}), 200




# UPDATE
@tag_bp.route("/tags/<int:tag_id>", methods=["PUT"])
def update_tag(tag_id):
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({"error": "Name is required"}), 400

    tag = Tag.query.get(tag_id)
    if not tag:
        return jsonify({"error": "Tag not found"}), 406

    existing_tag = Tag.query.filter_by(name=name).first()
    if existing_tag and existing_tag.id != tag_id:
        return jsonify({"error": "Another tag with this name already exists"}), 406

    tag.name = name
    db.session.commit()
    return jsonify({"success": "Tag updated successfully"}), 200


# DELETE
@tag_bp.route("/tags/<int:tag_id>", methods=["DELETE"])
def delete_tag(tag_id):
    tag = Tag.query.get(tag_id)
    if not tag:
        return jsonify({"error": "Tag not found"}), 406


    db.session.delete(tag)
    db.session.commit()
    return jsonify({"success": "Tag deleted successfully"}), 200


    db.session.commit()
    return jsonify({"success": "Tag updated successfully"}), 200
