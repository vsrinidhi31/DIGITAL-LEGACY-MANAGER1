from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Asset, User, ActivityLog
import os
from werkzeug.utils import secure_filename
import datetime

vault_bp = Blueprint('vault', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@vault_bp.route('/assets', methods=['GET'])
@jwt_required()
def get_assets():
    current_user_id = get_jwt_identity()
    assets = Asset.query.filter_by(user_id=current_user_id).all()
    
    asset_list = [{
        "id": a.id,
        "filename": a.filename,
        "asset_type": a.asset_type,
        "created_at": a.created_at,
        "encrypted_content": a.encrypted_content if a.asset_type in ['note', 'password'] else None
    } for a in assets]
    
    # Update activity
    user = User.query.get(current_user_id)
    user.last_activity_date = datetime.datetime.utcnow()
    db.session.commit()
    
    return jsonify(asset_list), 200

@vault_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_asset():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    asset_type = request.form.get('asset_type')
    
    if asset_type in ['note', 'password']:
        content = request.form.get('content')
        filename = request.form.get('filename')
        
        new_asset = Asset(
            user_id=current_user_id,
            filename=filename,
            asset_type=asset_type,
            encrypted_content=content # In real app, this should be encrypted before saving
        )
        db.session.add(new_asset)
        
        log = ActivityLog(user_id=current_user_id, action=f"Created {asset_type}: {filename}")
        db.session.add(log)
        
    elif asset_type in ['document', 'media']:
        if 'file' not in request.files:
            return jsonify({"message": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "No selected file"}), 400
            
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, f"{current_user_id}_{filename}")
        file.save(file_path)
        
        new_asset = Asset(
            user_id=current_user_id,
            filename=filename,
            asset_type=asset_type,
            file_path=file_path
        )
        db.session.add(new_asset)
        
        log = ActivityLog(user_id=current_user_id, action=f"Uploaded file: {filename}")
        db.session.add(log)
    else:
        return jsonify({"message": "Invalid asset type"}), 400
        
    user.last_activity_date = datetime.datetime.utcnow()
    db.session.commit()
    
    return jsonify({"message": "Asset saved successfully"}), 201
