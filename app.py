from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'hr-secret-key-change-me')
CORS(app)

# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://mukeshkanna10102004_db_user:Mukesh10102004@hr-cluster.glsbk8q.mongodb.net/hr_system?retryWrites=true&w=majority')

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client.hr_system
    print("✅ MongoDB connected!")
except Exception as e:
    print(f"❌ MongoDB error: {e}")
    db = None

def serialize_doc(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading template: {str(e)}", 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'mongodb': 'connected' if db else 'disconnected'
    })

@app.route('/api/data', methods=['GET'])
def get_all_data():
    try:
        if not db:
            return jsonify({'users': [], 'tasks': [], 'error': 'Database not connected'})
        
        users = list(db.users.find())
        tasks = list(db.tasks.find())
        
        for user in users:
            serialize_doc(user)
        for task in tasks:
            serialize_doc(task)
        
        return jsonify({'users': users, 'tasks': tasks})
    except Exception as e:
        print(f"Error in get_all_data: {e}")
        return jsonify({'users': [], 'tasks': [], 'error': str(e)})

@app.route('/api/data', methods=['POST'])
def save_all_data():
    try:
        if not db:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
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
        print(f"Error in save_all_data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        if not db:
            return jsonify([])
        users = list(db.users.find())
        for user in users:
            serialize_doc(user)
        return jsonify(users)
    except Exception as e:
        print(f"Error in get_users: {e}")
        return jsonify([])

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        if not db:
            return jsonify([])
        tasks = list(db.tasks.find())
        for task in tasks:
            serialize_doc(task)
        return jsonify(tasks)
    except Exception as e:
        print(f"Error in get_tasks: {e}")
        return jsonify([])

@app.route('/api/init', methods=['POST'])
def initialize():
    try:
        if not db:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        if db.users.find_one({'username': 'admin'}):
            return jsonify({'success': True, 'message': 'Already initialized'})
        
        admin = {
            'username': 'admin',
            'password': generate_password_hash('admin123'),
            'name': 'Administrator',
            'role': 'admin',
            'createdAt': datetime.utcnow().isoformat()
        }
        db.users.insert_one(admin)
        
        return jsonify({'success': True, 'message': 'Admin created'})
    except Exception as e:
        print(f"Error in initialize: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
