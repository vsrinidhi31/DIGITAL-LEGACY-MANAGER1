from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Nominee, User, ActivityLog, AccessRequest
import datetime

nominee_bp = Blueprint('nominee', __name__)

@nominee_bp.route('/', methods=['GET'])
@jwt_required()
def get_nominees():
    current_user_id = get_jwt_identity()
    nominees = Nominee.query.filter_by(user_id=current_user_id).all()
    
    nominee_list = [{
        "id": n.id,
        "email": n.email,
        "full_name": n.full_name,
        "permission_level": n.permission_level,
        "status": n.status
    } for n in nominees]
    
    return jsonify(nominee_list), 200

@nominee_bp.route('/', methods=['POST'])
@jwt_required()
def add_nominee():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('full_name'):
        return jsonify({"message": "Missing required fields"}), 400
        
    new_nominee = Nominee(
        user_id=current_user_id,
        email=data['email'],
        full_name=data['full_name'],
        permission_level=data.get('permission_level', 'Full')
    )
    
    db.session.add(new_nominee)
    
    log = ActivityLog(user_id=current_user_id, action=f"Added nominee: {data['email']}")
    db.session.add(log)
    
    user = User.query.get(current_user_id)
    user.last_activity_date = datetime.datetime.utcnow()
    
    db.session.commit()
    return jsonify({"message": "Nominee added successfully"}), 201

# For nominees to request access (In reality, they would have their own login or specialized link)
@nominee_bp.route('/request-access', methods=['POST'])
def request_access():
    data = request.get_json()
    nominee_email = data.get('email')
    user_email = data.get('user_email') # The user they are requesting access to
    
    if not nominee_email or not user_email:
        return jsonify({"message": "Missing fields"}), 400
        
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"message": "Target user not found"}), 404
        
    nominee = Nominee.query.filter_by(user_id=user.id, email=nominee_email).first()
    if not nominee:
        return jsonify({"message": "You are not a registered nominee for this user"}), 403
        
    # Check if user is truly inactive
    inactive_days = (datetime.datetime.utcnow() - user.last_activity_date).days
    
    if inactive_days >= user.inactivity_threshold_days:
        # User is inactive, automatically approve (or trigger workflow)
        new_request = AccessRequest(nominee_id=nominee.id, status='Approved')
        db.session.add(new_request)
        db.session.commit()
        return jsonify({"message": "Access approved due to user inactivity."}), 200
    else:
        # User is still considered active
        new_request = AccessRequest(nominee_id=nominee.id, status='Denied')
        db.session.add(new_request)
        db.session.commit()
        return jsonify({
            "message": "Access denied. User is currently active.", 
            "days_since_active": inactive_days,
            "threshold": user.inactivity_threshold_days
        }), 403

