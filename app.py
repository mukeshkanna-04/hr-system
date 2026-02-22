from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'hr-secret-key')
CORS(app)

MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://mukeshkanna10102004_db_user:Mukesh10102004@hr-cluster.glsbk8q.mongodb.net/HRSystem?retryWrites=true&w=majority')

try:
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    client.admin.command('ping')
    db = client.HRSystem
    print("✅ MongoDB connected!")
except Exception as e:
    print(f"❌ Error: {e}")
    db = None

def serialize(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

def init_users():
    if db is None or db.users.count_documents({}) > 0:
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
    db.users.insert_many(users)
    print(f"✅ Created {len(users)} users")

@app.route('/')
def home():
    init_users()
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    if db is None:
        return jsonify({'success': False, 'users': [], 'reports': [], 'tasks': []})
    init_users()
    users = [serialize(u) for u in db.users.find()]
    reports = [serialize(r) for r in db.reports.find()]
    tasks = [serialize(t) for t in db.tasks.find()]
    return jsonify({'success': True, 'users': users, 'reports': reports, 'tasks': tasks})

@app.route('/api/data', methods=['POST'])
def save_data():
    if db is None:
        return jsonify({'success': False, 'error': 'Database not connected'}), 500
    
    try:
        data = request.json
        
        # Save users - CRITICAL: Remove _id before updating!
        for u in data.get('users', []):
            if '_id' in u and u['_id']:
                user_id = ObjectId(u['_id']) if isinstance(u['_id'], str) else u['_id']
                # Create copy without _id for update
                update_data = {k: v for k, v in u.items() if k != '_id'}
                db.users.update_one({'_id': user_id}, {'$set': update_data}, upsert=True)
            else:
                # New user - insert directly
                db.users.insert_one(u)
        
        # Save reports
        for r in data.get('reports', []):
            if '_id' in r and r['_id']:
                report_id = ObjectId(r['_id']) if isinstance(r['_id'], str) else r['_id']
                update_data = {k: v for k, v in r.items() if k != '_id'}
                db.reports.update_one({'_id': report_id}, {'$set': update_data}, upsert=True)
            else:
                db.reports.insert_one(r)
        
        # Save tasks
        for t in data.get('tasks', []):
            if '_id' in t and t['_id']:
                task_id = ObjectId(t['_id']) if isinstance(t['_id'], str) else t['_id']
                update_data = {k: v for k, v in t.items() if k != '_id'}
                db.tasks.update_one({'_id': task_id}, {'$set': update_data}, upsert=True)
            else:
                db.tasks.insert_one(t)
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Save error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/init', methods=['POST'])
def initialize():
    if db is None:
        return jsonify({'success': False}), 500
    db.users.delete_many({})
    db.reports.delete_many({})
    db.tasks.delete_many({})
    init_users()
    return jsonify({'success': True, 'message': '30 users created!'})

if __name__ == '__main__':
    if db is not None:
        init_users()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
