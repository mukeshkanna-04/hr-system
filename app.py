from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'hr-secret-key')
CORS(app)

# Initialize Firebase
try:
    # For Render deployment, use environment variable for credentials
    cred_dict = {
        "type": "service_account",
        "project_id": "hr-daily-reporting-system",
        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
        "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
        "client_id": os.getenv('FIREBASE_CLIENT_ID'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv('FIREBASE_CERT_URL')
    }
    
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase connected!")
except Exception as e:
    print(f"❌ Firebase error: {e}")
    db = None

def init_users():
    if db is None:
        return
    
    # Check if users already exist
    users_ref = db.collection('users')
    if len(list(users_ref.limit(1).stream())) > 0:
        return
    
    users = [
        {'username': 'hradmin', 'password': generate_password_hash('Admin@2024'), 'name': 'HR Administrator', 'role': 'admin', 'group': None},
        {'username': 'do.sharma', 'password': generate_password_hash('DO@2024'), 'name': 'Ms. Priya Sharma', 'role': 'do', 'group': None},
        {'username': 'hos.dl', 'password': generate_password_hash('HoS@2024'), 'name': 'Mr. Amit Verma', 'role': 'hos', 'group': 'D&L'},
        {'username': 'hos.admin', 'password': generate_password_hash('HoS@2024'), 'name': 'Ms. Sunita Patel', 'role': 'hos', 'group': 'Administration'},
        {'username': 'hos.training', 'password': generate_password_hash('HoS@2024'), 'name': 'Mr. Vijay Singh', 'role': 'hos', 'group': 'Training'},
        {'username': 'hos.rajbhasha', 'password': generate_password_hash('HoS@2024'), 'name': 'Ms. Rekha Joshi', 'role': 'hos', 'group': 'Rajbhasha'},
        {'username': 'hos.pension', 'password': generate_password_hash('HoS@2024'), 'name': 'Mr. Ramesh Gupta', 'role': 'hos', 'group': 'Pension'},
        {'username': 'hos.time', 'password': generate_password_hash('HoS@2024'), 'name': 'Ms. Pooja Sharma', 'role': 'hos', 'group': 'Time Office'},
        {'username': 'hos.leave', 'password': generate_password_hash('HoS@2024'), 'name': 'Mr. Sanjay Kumar', 'role': 'hos', 'group': 'Leave'},
        {'username': 'hos.bills', 'password': generate_password_hash('HoS@2024'), 'name': 'Ms. Neha Reddy', 'role': 'hos', 'group': 'Bills'},
        {'username': 'hos.dak', 'password': generate_password_hash('HoS@2024'), 'name': 'Mr. Arun Singh', 'role': 'hos', 'group': 'DAK'},
        {'username': 'go.kumar', 'password': generate_password_hash('GO@2024'), 'name': 'Mr. Rajesh Kumar', 'role': 'go', 'group': None},
        {'username': 'user.dl1', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Suresh Reddy', 'role': 'user', 'group': 'D&L'},
        {'username': 'user.dl2', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Kavita Rao', 'role': 'user', 'group': 'D&L'},
        {'username': 'user.admin1', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Anil Kumar', 'role': 'user', 'group': 'Administration'},
        {'username': 'user.admin2', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Deepa Mehta', 'role': 'user', 'group': 'Administration'},
        {'username': 'user.training1', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Ramesh Gupta', 'role': 'user', 'group': 'Training'},
        {'username': 'user.training2', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Priya Nair', 'role': 'user', 'group': 'Training'},
        {'username': 'user.rajbhasha1', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Anjali Devi', 'role': 'user', 'group': 'Rajbhasha'},
        {'username': 'user.rajbhasha2', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Vijay Sharma', 'role': 'user', 'group': 'Rajbhasha'},
        {'username': 'user.pension1', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Mohan Lal', 'role': 'user', 'group': 'Pension'},
        {'username': 'user.pension2', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Lakshmi Devi', 'role': 'user', 'group': 'Pension'},
        {'username': 'user.time1', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Rekha Nair', 'role': 'user', 'group': 'Time Office'},
        {'username': 'user.time2', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Krishna Das', 'role': 'user', 'group': 'Time Office'},
        {'username': 'user.leave1', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Sanjay Joshi', 'role': 'user', 'group': 'Leave'},
        {'username': 'user.leave2', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Sunita Roy', 'role': 'user', 'group': 'Leave'},
        {'username': 'user.bills1', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Pooja Sharma', 'role': 'user', 'group': 'Bills'},
        {'username': 'user.bills2', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Rahul Verma', 'role': 'user', 'group': 'Bills'},
        {'username': 'user.dak1', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Rahul Singh', 'role': 'user', 'group': 'DAK'},
        {'username': 'user.dak2', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Anita Patel', 'role': 'user', 'group': 'DAK'}
    ]
    
    for user in users:
        users_ref.add(user)
    
    print(f"✅ Created {len(users)} users in Firebase!")

@app.route('/')
def home():
    init_users()
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    if db is None:
        return jsonify({'success': False, 'users': [], 'reports': [], 'tasks': []})
    
    try:
        init_users()
        
        # Get users
        users = []
        for doc in db.collection('users').stream():
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            users.append(user_data)
        
        # Get reports
        reports = []
        for doc in db.collection('reports').stream():
            report_data = doc.to_dict()
            report_data['id'] = doc.id
            reports.append(report_data)
        
        # Get tasks
        tasks = []
        for doc in db.collection('tasks').stream():
            task_data = doc.to_dict()
            task_data['id'] = doc.id
            tasks.append(task_data)
        
        return jsonify({'success': True, 'users': users, 'reports': reports, 'tasks': tasks})
    except Exception as e:
        print(f"❌ Get error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/data', methods=['POST'])
def save_data():
    if db is None:
        return jsonify({'success': False, 'error': 'Database not connected'}), 500
    
    try:
        data = request.json
        
        # Save users
        for user in data.get('users', []):
            if 'id' in user and user['id']:
                # Update existing
                doc_id = user['id']
                user_data = {k: v for k, v in user.items() if k != 'id'}
                db.collection('users').document(doc_id).set(user_data)
            else:
                # Create new
                user_data = {k: v for k, v in user.items() if k != 'id'}
                db.collection('users').add(user_data)
        
        # Save reports
        for report in data.get('reports', []):
            if 'id' in report and report['id']:
                doc_id = report['id']
                report_data = {k: v for k, v in report.items() if k != 'id'}
                db.collection('reports').document(doc_id).set(report_data)
            else:
                report_data = {k: v for k, v in report.items() if k != 'id'}
                db.collection('reports').add(report_data)
        
        # Save tasks
        for task in data.get('tasks', []):
            if 'id' in task and task['id']:
                doc_id = task['id']
                task_data = {k: v for k, v in task.items() if k != 'id'}
                db.collection('tasks').document(doc_id).set(task_data)
            else:
                task_data = {k: v for k, v in task.items() if k != 'id'}
                db.collection('tasks').add(task_data)
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Save error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/init', methods=['POST'])
def initialize():
    if db is None:
        return jsonify({'success': False}), 500
    
    try:
        # Delete all users
        users_ref = db.collection('users')
        for doc in users_ref.stream():
            doc.reference.delete()
        
        # Delete all reports
        reports_ref = db.collection('reports')
        for doc in reports_ref.stream():
            doc.reference.delete()
        
        # Delete all tasks
        tasks_ref = db.collection('tasks')
        for doc in tasks_ref.stream():
            doc.reference.delete()
        
        # Recreate default users
        init_users()
        
        return jsonify({'success': True, 'message': '30 users created in Firebase!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    if db is not None:
        init_users()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
