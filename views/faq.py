from flask import jsonify, request, Blueprint
from model import db, Faq
faq_bp =Blueprint("faq_bp", __name__)



#  Add FAQ
@faq_bp.route("/faqs", methods=["POST"])
def add_faqs():
    data = request.get_json()
    question = data['question']
    answer = data['answer']

    check_question = Faq.query.filter_by(question=question).first()

    if check_question:
        return jsonify({"error":"question already exists"}), 406

    else:
        new_faq = Faq(question=question, answer=answer)
        db.session.add(new_faq)
        db.session.commit()
        return jsonify({"success":"Faq added successfully"})



# Fetch FAQ
@faq_bp.route("/faqs", methods=["GET"])
def get_faqs():
    faqs = Faq.query.all()
    faqs_list = [{"id": faq.id, "question": faq.question, "answer": faq.answer} for faq in faqs]
    return jsonify(faqs_list), 200




# Update FAQ
@faq_bp.route("/faqs/<int:faq_id>", methods=["PUT"])
def update_faqs(faq_id):
    data = request.get_json()
    question = data['question']
    answer = data['answer']

   

    faq = Faq.query.get(faq_id)
    if not faq:
        return jsonify({"error": "Faq not found"}), 406

    existing_faq = Faq.query.filter_by(question=question).first()
    if existing_faq and existing_faq.id != faq_id:
        return jsonify({"error": "This type of question exist"}), 406

    existing_faq = Faq.query.filter_by(answer=answer).first()
    if existing_faq and existing_faq.id != faq_id:
        return jsonify({"error": "This answer exist"}), 406

    faq.question = question
    faq.answer = answer
    db.session.commit()
    return jsonify({"success": "Faq updated successfully"}), 200




# DELETE FAQ
@faq_bp.route("/faqs/<int:faq_id>", methods=["DELETE"])
def delete_faq(faq_id):
    faq = Faq.query.get(faq_id)
    if not faq:
        return jsonify({"error": "Faq not found"}), 406


    db.session.delete(faq)
    db.session.commit()
    return jsonify({"success": "Faq deleted successfully"}), 200


    db.session.commit()
    return jsonify({"success": "Faq updated successfully"}), 200