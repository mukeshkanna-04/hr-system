from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'hr-secret-key-change-in-production')
CORS(app)

# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://mukeshkanna10102004_db_user:Mukesh10102004@hr-cluster.glsbk8q.mongodb.net/hr_system?retryWrites=true&w=majority')

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client.hr_system
    print("✅ MongoDB connected successfully!")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")
    db = None

def serialize_doc(doc):
    """Convert MongoDB ObjectId to string"""
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

def initialize_default_users():
    """Create all default users in MongoDB"""
    if not db:
        return False
    
    # Check if users already exist
    if db.users.count_documents({}) > 0:
        print("✅ Users already exist in database")
        return True
    
    print("🔄 Creating default users...")
    
    default_users = [
        {'id': 1, 'username': 'hradmin', 'password': generate_password_hash('Admin@2024'), 'name': 'HR Administrator', 'role': 'admin', 'group': None},
        {'id': 2, 'username': 'do.sharma', 'password': generate_password_hash('DO@2024'), 'name': 'Ms. Priya Sharma', 'role': 'do', 'group': None},
        {'id': 3, 'username': 'hos.dl', 'password': generate_password_hash('HoS@2024'), 'name': 'Mr. Amit Verma', 'role': 'hos', 'group': 'D&L'},
        {'id': 4, 'username': 'hos.admin', 'password': generate_password_hash('HoS@2024'), 'name': 'Ms. Sunita Patel', 'role': 'hos', 'group': 'Administration'},
        {'id': 5, 'username': 'hos.training', 'password': generate_password_hash('HoS@2024'), 'name': 'Mr. Vijay Singh', 'role': 'hos', 'group': 'Training'},
        {'id': 6, 'username': 'hos.rajbhasha', 'password': generate_password_hash('HoS@2024'), 'name': 'Ms. Rekha Joshi', 'role': 'hos', 'group': 'Rajbhasha'},
        {'id': 7, 'username': 'hos.pension', 'password': generate_password_hash('HoS@2024'), 'name': 'Mr. Ramesh Gupta', 'role': 'hos', 'group': 'Pension'},
        {'id': 8, 'username': 'hos.time', 'password': generate_password_hash('HoS@2024'), 'name': 'Ms. Pooja Sharma', 'role': 'hos', 'group': 'Time Office'},
        {'id': 9, 'username': 'hos.leave', 'password': generate_password_hash('HoS@2024'), 'name': 'Mr. Sanjay Kumar', 'role': 'hos', 'group': 'Leave'},
        {'id': 10, 'username': 'hos.bills', 'password': generate_password_hash('HoS@2024'), 'name': 'Ms. Neha Reddy', 'role': 'hos', 'group': 'Bills'},
        {'id': 11, 'username': 'hos.dak', 'password': generate_password_hash('HoS@2024'), 'name': 'Mr. Arun Singh', 'role': 'hos', 'group': 'DAK'},
        {'id': 12, 'username': 'go.kumar', 'password': generate_password_hash('GO@2024'), 'name': 'Mr. Rajesh Kumar', 'role': 'go', 'group': None},
        {'id': 13, 'username': 'user.dl1', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Suresh Reddy', 'role': 'user', 'group': 'D&L'},
        {'id': 14, 'username': 'user.dl2', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Kavita Rao', 'role': 'user', 'group': 'D&L'},
        {'id': 15, 'username': 'user.admin1', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Anil Kumar', 'role': 'user', 'group': 'Administration'},
        {'id': 16, 'username': 'user.admin2', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Deepa Mehta', 'role': 'user', 'group': 'Administration'},
        {'id': 17, 'username': 'user.training1', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Ramesh Gupta', 'role': 'user', 'group': 'Training'},
        {'id': 18, 'username': 'user.training2', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Priya Nair', 'role': 'user', 'group': 'Training'},
        {'id': 19, 'username': 'user.rajbhasha1', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Anjali Devi', 'role': 'user', 'group': 'Rajbhasha'},
        {'id': 20, 'username': 'user.rajbhasha2', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Vijay Sharma', 'role': 'user', 'group': 'Rajbhasha'},
        {'id': 21, 'username': 'user.pension1', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Mohan Lal', 'role': 'user', 'group': 'Pension'},
        {'id': 22, 'username': 'user.pension2', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Lakshmi Devi', 'role': 'user', 'group': 'Pension'},
        {'id': 23, 'username': 'user.time1', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Rekha Nair', 'role': 'user', 'group': 'Time Office'},
        {'id': 24, 'username': 'user.time2', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Krishna Das', 'role': 'user', 'group': 'Time Office'},
        {'id': 25, 'username': 'user.leave1', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Sanjay Joshi', 'role': 'user', 'group': 'Leave'},
        {'id': 26, 'username': 'user.leave2', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Sunita Roy', 'role': 'user', 'group': 'Leave'},
        {'id': 27, 'username': 'user.bills1', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Pooja Sharma', 'role': 'user', 'group': 'Bills'},
        {'id': 28, 'username': 'user.bills2', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Rahul Verma', 'role': 'user', 'group': 'Bills'},
        {'id': 29, 'username': 'user.dak1', 'password': generate_password_hash('User@2024'), 'name': 'Mr. Rahul Singh', 'role': 'user', 'group': 'DAK'},
        {'id': 30, 'username': 'user.dak2', 'password': generate_password_hash('User@2024'), 'name': 'Ms. Anita Patel', 'role': 'user', 'group': 'DAK'}
    ]
    
    # Insert all default users
    db.users.insert_many(default_users)
    print(f"✅ Created {len(default_users)} default users!")
    return True

@app.route('/')
def home():
    """Serve the main frontend"""
    # Auto-initialize users on first request
    initialize_default_users()
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading template: {str(e)}<br>Make sure templates/index.html exists!", 500

@app.route('/health')
def health():
    """Health check endpoint"""
    user_count = db.users.count_documents({}) if db else 0
    return jsonify({
        'status': 'ok',
        'mongodb': 'connected' if db else 'disconnected',
        'users': user_count,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/data', methods=['GET'])
def get_all_data():
    """Get all users and tasks from MongoDB"""
    try:
        if not db:
            return jsonify({'users': [], 'tasks': []})
        
        # Ensure default users exist
        initialize_default_users()
        
        users = list(db.users.find())
        tasks = list(db.tasks.find())
        
        for user in users:
            serialize_doc(user)
        for task in tasks:
            serialize_doc(task)
        
        return jsonify({'users': users, 'tasks': tasks})
    except Exception as e:
        print(f"Error in get_all_data: {e}")
        return jsonify({'users': [], 'tasks': []})

@app.route('/api/data', methods=['POST'])
def save_all_data():
    """Save all users and tasks to MongoDB"""
    try:
        if not db:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        data = request.json
        users = data.get('users', [])
        tasks = data.get('tasks', [])
        
        # Save users
        for user in users:
            if '_id' in user and user['_id']:
                try:
                    user_id = ObjectId(user['_id']) if isinstance(user['_id'], str) else user['_id']
                    db.users.update_one({'_id': user_id}, {'$set': user}, upsert=True)
                except Exception as e:
                    print(f"Error saving user: {e}")
            else:
                try:
                    result = db.users.insert_one(user)
                    user['_id'] = str(result.inserted_id)
                except Exception as e:
                    print(f"Error inserting user: {e}")
        
        # Save tasks
        for task in tasks:
            if '_id' in task and task['_id']:
                try:
                    task_id = ObjectId(task['_id']) if isinstance(task['_id'], str) else task['_id']
                    db.tasks.update_one({'_id': task_id}, {'$set': task}, upsert=True)
                except Exception as e:
                    print(f"Error saving task: {e}")
            else:
                try:
                    result = db.tasks.insert_one(task)
                    task['_id'] = str(result.inserted_id)
                except Exception as e:
                    print(f"Error inserting task: {e}")
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error in save_all_data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/init', methods=['POST'])
def initialize():
    """Force initialize all default users"""
    try:
        if not db:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        # Clear existing users
        db.users.delete_many({})
        
        # Recreate all default users
        initialize_default_users()
        
        return jsonify({
            'success': True,
            'message': '30 default users created!',
            'users': db.users.count_documents({})
        })
    except Exception as e:
        print(f"Error in initialize: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    print(f"🚀 Starting HR System on port {port}")
    print(f"📊 MongoDB: {'Connected' if db else 'Disconnected'}")
    
    # Initialize users on startup
    if db:
        initialize_default_users()
    
    app.run(host='0.0.0.0', port=port, debug=False)
