from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'hr-secret-key')
CORS(app)

# CORRECT MongoDB URI - Replace <password> with actual password
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://mukeshkanna10102004_db_user:Mukesh10102004@hr-cluster.glsbk8q.mongodb.net/?retryWrites=true&w=majority&appName=HR-Cluster')

try:
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    client.admin.command('ping')
    db = client.hr_system
    print("✅ Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"❌ MongoDB error: {e}")
    db = None

def serialize_doc(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

def initialize_default_users():
    if db is None:
        return False
    
    if db.users.count_documents({}) > 0:
        return True
    
    users = [
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
    
    db.users.insert_many(users)
    print(f"✅ Created {len(users)} users!")
    return True

@app.route('/')
def home():
    initialize_default_users()
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/health')
def health():
    user_count = db.users.count_documents({}) if db is not None else 0
    return jsonify({'status': 'ok', 'mongodb': 'connected' if db is not None else 'disconnected', 'users': user_count})

@app.route('/api/data', methods=['GET'])
def get_all_data():
    try:
        if db is None:
            return jsonify({'users': [], 'tasks': []})
        
        initialize_default_users()
        users = list(db.users.find())
        tasks = list(db.tasks.find())
        
        for user in users:
            serialize_doc(user)
        for task in tasks:
            serialize_doc(task)
        
        return jsonify({'users': users, 'tasks': tasks})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'users': [], 'tasks': []})

@app.route('/api/data', methods=['POST'])
def save_all_data():
    try:
        if db is None:
            return jsonify({'success': False}), 500
        
        data = request.json
        users = data.get('users', [])
        tasks = data.get('tasks', [])
        
        for user in users:
            if '_id' in user and user['_id']:
                try:
                    user_id = ObjectId(user['_id']) if isinstance(user['_id'], str) else user['_id']
                    db.users.update_one({'_id': user_id}, {'$set': user}, upsert=True)
                except:
                    pass
        
        for task in tasks:
            if '_id' in task and task['_id']:
                try:
                    task_id = ObjectId(task['_id']) if isinstance(task['_id'], str) else task['_id']
                    db.tasks.update_one({'_id': task_id}, {'$set': task}, upsert=True)
                except:
                    pass
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False}), 500

@app.route('/api/init', methods=['POST'])
def initialize():
    try:
        if db is None:
            return jsonify({'success': False}), 500
        
        db.users.delete_many({})
        initialize_default_users()
        
        return jsonify({'success': True, 'message': '30 users created!', 'users': db.users.count_documents({})})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    if db is not None:
        initialize_default_users()
    app.run(host='0.0.0.0', port=port, debug=False)
