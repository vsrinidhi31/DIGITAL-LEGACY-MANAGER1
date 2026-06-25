from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, ActivityLog
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('full_name'):
        return jsonify({"message": "Missing required fields"}), 400
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "User already exists"}), 400
        
    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        email=data['email'],
        password_hash=hashed_password,
        full_name=data['full_name']
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Log activity
    log = ActivityLog(user_id=new_user.id, action="User Registration")
    db.session.add(log)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing required fields"}), 400
        
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"message": "Invalid email or password"}), 401
        
    # Update last activity
    user.last_activity_date = datetime.datetime.utcnow()
    
    # Log activity
    log = ActivityLog(user_id=user.id, action="User Login")
    db.session.add(log)
    db.session.commit()
    
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "access_token": access_token, 
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "status": user.status
        }
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
        
    # Update activity on profile fetch (optional heartbeat)
    user.last_activity_date = datetime.datetime.utcnow()
    db.session.commit()
        
    return jsonify({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "last_activity_date": user.last_activity_date,
        "status": user.status
    }), 200

