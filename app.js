const API_URL = 'http://127.0.0.1:5000/api';

// --- Auth Handling logic ---
function showForm(type) {
    if(type === 'login') {
        document.getElementById('login-form').style.display = 'block';
        document.getElementById('register-form').style.display = 'none';
        document.getElementById('tab-login').classList.add('active');
        document.getElementById('tab-register').classList.remove('active');
    } else {
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('register-form').style.display = 'block';
        document.getElementById('tab-login').classList.remove('active');
        document.getElementById('tab-register').classList.add('active');
    }
}

if(document.getElementById('login-form')) {
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        try {
            const res = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, password})
            });
            const data = await res.json();
            
            if(res.ok) {
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('user', JSON.stringify(data.user));
                window.location.href = 'dashboard.html';
            } else {
                document.getElementById('login-error').innerText = data.message;
            }
        } catch(err) {
            document.getElementById('login-error').innerText = "Server connection failed.";
        }
    });

    document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('reg-name').value;
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;
        
        try {
            const res = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({full_name: name, email, password})
            });
            const data = await res.json();
            
            if(res.ok) {
                alert("Registration successful! Please login.");
                showForm('login');
            } else {
                document.getElementById('reg-error').innerText = data.message;
            }
        } catch(err) {
            document.getElementById('reg-error').innerText = "Server connection failed.";
        }
    });
}

// --- Dashboard Logic ---

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

async function loadDashboardData() {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    if(!token || !userStr) return;
    
    const user = JSON.parse(userStr);
    
    // Update Header
    document.getElementById('user-greeting').innerText = `Welcome, ${user.full_name}`;
    
    // Fetch Profile
    const profileRes = await fetch(`${API_URL}/auth/profile`, {
        headers: {'Authorization': `Bearer ${token}`}
    });
    if(profileRes.ok) {
        const profileInfo = await profileRes.json();
        document.getElementById('activity-status').innerText = `Status: ${profileInfo.status} (Last Activity updated just now)`;
    }

    // Load Vault and Nominees
    loadAssets(token);
    loadNominees(token);
}

async function loadAssets(token) {
    const res = await fetch(`${API_URL}/vault/assets`, {
        headers: {'Authorization': `Bearer ${token}`}
    });
    if(res.ok) {
        const assets = await res.json();
        const list = document.getElementById('assets-list');
        list.innerHTML = '';
        if(assets.length === 0) list.innerHTML = '<li style="color:var(--text-muted);">No assets stored yet.</li>';
        
        assets.forEach(a => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div>
                    <strong>${a.filename}</strong> <span style="font-size:12px;color:var(--text-muted); border: 1px solid #334155; padding: 2px 5px; border-radius: 4px; margin-left: 5px;">${a.asset_type}</span>
                </div>
            `;
            list.appendChild(li);
        });
    }
}

async function loadNominees(token) {
    const res = await fetch(`${API_URL}/nominees/`, {
        headers: {'Authorization': `Bearer ${token}`}
    });
    if(res.ok) {
        const nominees = await res.json();
        const list = document.getElementById('nominees-list');
        list.innerHTML = '';
        if(nominees.length === 0) list.innerHTML = '<li style="color:var(--text-muted);">No nominees added yet.</li>';
        
        nominees.forEach(n => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div>
                    <strong>${n.full_name}</strong><br>
                    <span style="font-size:13px;color:var(--text-muted);">${n.email}</span>
                </div>
                <span style="font-size:12px;background:#334155;padding:4px 8px;border-radius:12px;">${n.permission_level}</span>
            `;
            list.appendChild(li);
        });
    }
}

if(document.getElementById('upload-form')) {
    document.getElementById('upload-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const type = document.getElementById('asset-type').value;
        const title = document.getElementById('asset-title').value;
        const content = document.getElementById('asset-content').value;
        const token = localStorage.getItem('token');
        
        const fd = new FormData();
        fd.append('asset_type', type);
        fd.append('filename', title);
        fd.append('content', content);
        
        const res = await fetch(`${API_URL}/vault/upload`, {
            method: 'POST',
            headers: {'Authorization': `Bearer ${token}`},
            body: fd
        });
        
        if(res.ok) {
            document.getElementById('asset-title').value = '';
            document.getElementById('asset-content').value = '';
            loadAssets(token);
        }
    });

    document.getElementById('add-nominee-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('nominee-name').value;
        const email = document.getElementById('nominee-email').value;
        const token = localStorage.getItem('token');
        
        const res = await fetch(`${API_URL}/nominees/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({full_name: name, email})
        });
        
        if(res.ok) {
            document.getElementById('nominee-name').value = '';
            document.getElementById('nominee-email').value = '';
            loadNominees(token);
        }
    });
    
    // Simulate Request
    document.getElementById('simulate-access-form').addEventListener('submit', async(e) => {
       e.preventDefault();
       const nomEmail = document.getElementById('sim-nominee-email').value;
       const userStr = localStorage.getItem('user');
       const user = JSON.parse(userStr);
       
       const res = await fetch(`${API_URL}/nominees/request-access`, {
           method: 'POST',
           headers: {'Content-Type': 'application/json'},
           body: JSON.stringify({email: nomEmail, user_email: user.email})
       });
       
       const data = await res.json();
       const resultEl = document.getElementById('sim-result');
       
       if(res.ok) {
           resultEl.style.color = "var(--success)";
           resultEl.innerText = data.message;
       } else {
           resultEl.style.color = "var(--error)";
           resultEl.innerText = data.message + (data.days_since_active ? ` (Days inactive: ${data.days_since_active}/${data.threshold})` : '');
       }
    });
}

Seed.py
from app import create_app
from models import db, User, Nominee, Asset, ActivityLog
from werkzeug.security import generate_password_hash
import datetime

app = create_app()

def seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create users
        # 1. Active User
        user1 = User(
            email="active@example.com",
            password_hash=generate_password_hash("password123"),
            full_name="Active Alice",
            last_activity_date=datetime.datetime.utcnow(),
            inactivity_threshold_days=60
        )
        
        # 2. Inactive User
        user2_inactive_date = datetime.datetime.utcnow() - datetime.timedelta(days=70)
        user2 = User(
            email="inactive@example.com",
            password_hash=generate_password_hash("password123"),
            full_name="Inactive Bob",
            last_activity_date=user2_inactive_date,
            inactivity_threshold_days=60
        )
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        # Add Nominees
        n1 = Nominee(user_id=user1.id, email="nominee1@test.com", full_name="Nominee One")
        n2 = Nominee(user_id=user2.id, email="nominee2@test.com", full_name="Nominee Two")
        
        db.session.add(n1)
        db.session.add(n2)
        
        # Add some sample assets (notes)
        a1 = Asset(user_id=user1.id, filename="My Will", asset_type="note", encrypted_content="This is my will.")
        a2 = Asset(user_id=user2.id, filename="Bank Details", asset_type="password", encrypted_content="Secret Bank Info")
        
        db.session.add(a1)
        db.session.add(a2)
        
        db.session.commit()
        print("Database seeded successfully with sample data!")

if __name__ == "__main__":
    seed_data()

app.py
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from routes.auth import auth_bp
from routes.vault import vault_bp
from routes.nominees import nominee_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app) # Allow frontend to communicate with backend
    db.init_app(app)
    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(vault_bp, url_prefix='/api/vault')
    app.register_blueprint(nominee_bp, url_prefix='/api/nominees')

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"}), 200

    # Ensure tables are created
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
