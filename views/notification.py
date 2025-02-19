from flask import jsonify, request, Blueprint
from model import db, Notification

notification_bp =Blueprint("notification_bp", __name__)




@notification_bp.route('/users/<int:user_id>/notifications', methods=['GET'])
def get_notifications(user_id):
    # Get query parameters for pagination
    page = request.args.get('page', 1, type=int)  # Default to page 1
    per_page = request.args.get('per_page', 10, type=int)  # Default to 10 items per page

    # Query notifications with pagination
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).paginate(page=page, per_page=per_page)

    # Format the response
    notifications_data = [{
        'id': n.id,
        'message': n.message,
        'type': n.type,
        'is_read': n.is_read,
        'created_at': n.created_at
    } for n in notifications.items]

    return jsonify({
        'notifications': notifications_data,
        'total_pages': notifications.pages,
        'current_page': notifications.page,
        'total_records': notifications.total
    }), 200


# mark as read
@notification_bp.route('/notifications/<int:notification_id>/marks', methods=['PUT'])
def mark_notification_read(notification_id):
    notification = Notification.query.get(notification_id)
    if not notification:
        return jsonify({'message': 'Notification not found'}), 404

    notification.is_read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read'}), 200