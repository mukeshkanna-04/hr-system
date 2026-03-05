from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'hr-secret-key-2024')
CORS(app)

# PostgreSQL Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/hr_system')

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ PostgreSQL Connection Error: {e}")
        return None

def init_database():
    """Initialize database and create tables"""
    conn = get_db_connection()
    if not conn:
        print("❌ Cannot connect to PostgreSQL. Check your configuration!")
        return
    
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            user_group VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON users(username)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_role ON users(role)')
    
    # Create reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id SERIAL PRIMARY KEY,
            userId INTEGER NOT NULL,
            userName VARCHAR(255) NOT NULL,
            user_group VARCHAR(100),
            report_date DATE NOT NULL,
            report_time TIME NOT NULL,
            f1 TEXT,
            f2 TEXT,
            f3 TEXT,
            f4 TEXT,
            f5 TEXT,
            f6 TEXT,
            f7 TEXT,
            f8 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_reports ON reports(userId)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_report_date ON reports(report_date)')
    
    # Create tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            userId INTEGER NOT NULL,
            userName VARCHAR(255) NOT NULL,
            title VARCHAR(500) NOT NULL,
            description TEXT,
            dueDate DATE,
            priority VARCHAR(50),
            status VARCHAR(50) DEFAULT 'Pending',
            assignedBy VARCHAR(255),
            assignedDate TIMESTAMP,
            acceptedDate TIMESTAMP,
            completedDate TIMESTAMP,
            approvedDate TIMESTAMP,
            adminComment TEXT,
            uploadedFiles JSONB,
            extensionRequest JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_tasks ON tasks(userId)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status)')
    
    conn.commit()
    print("✅ Database tables created successfully!")
    
    # Check if default users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("📝 Creating 30 default users...")
        default_users = [
            ('hradmin', generate_password_hash('Admin@2024'), 'HR Administrator', 'admin', None),
            ('do.sharma', generate_password_hash('DO@2024'), 'Ms. Priya Sharma', 'do', None),
            ('hos.dl', generate_password_hash('HoS@2024'), 'Mr. Amit Verma', 'hos', 'D&L'),
            ('hos.admin', generate_password_hash('HoS@2024'), 'Ms. Sunita Patel', 'hos', 'Administration'),
            ('hos.training', generate_password_hash('HoS@2024'), 'Mr. Vijay Singh', 'hos', 'Training'),
            ('hos.rajbhasha', generate_password_hash('HoS@2024'), 'Ms. Rekha Joshi', 'hos', 'Rajbhasha'),
            ('hos.pension', generate_password_hash('HoS@2024'), 'Mr. Ramesh Gupta', 'hos', 'Pension'),
            ('hos.time', generate_password_hash('HoS@2024'), 'Ms. Pooja Sharma', 'hos', 'Time Office'),
            ('hos.leave', generate_password_hash('HoS@2024'), 'Mr. Sanjay Kumar', 'hos', 'Leave'),
            ('hos.bills', generate_password_hash('HoS@2024'), 'Ms. Neha Reddy', 'hos', 'Bills'),
            ('hos.dak', generate_password_hash('HoS@2024'), 'Mr. Arun Singh', 'hos', 'DAK'),
            ('go.kumar', generate_password_hash('GO@2024'), 'Mr. Rajesh Kumar', 'go', None),
            ('user.dl1', generate_password_hash('User@2024'), 'Mr. Suresh Reddy', 'user', 'D&L'),
            ('user.dl2', generate_password_hash('User@2024'), 'Ms. Kavita Rao', 'user', 'D&L'),
            ('user.admin1', generate_password_hash('User@2024'), 'Mr. Anil Kumar', 'user', 'Administration'),
            ('user.admin2', generate_password_hash('User@2024'), 'Ms. Deepa Mehta', 'user', 'Administration'),
            ('user.training1', generate_password_hash('User@2024'), 'Mr. Ramesh Gupta', 'user', 'Training'),
            ('user.training2', generate_password_hash('User@2024'), 'Ms. Priya Nair', 'user', 'Training'),
            ('user.rajbhasha1', generate_password_hash('User@2024'), 'Ms. Anjali Devi', 'user', 'Rajbhasha'),
            ('user.rajbhasha2', generate_password_hash('User@2024'), 'Mr. Vijay Sharma', 'user', 'Rajbhasha'),
            ('user.pension1', generate_password_hash('User@2024'), 'Mr. Mohan Lal', 'user', 'Pension'),
            ('user.pension2', generate_password_hash('User@2024'), 'Ms. Lakshmi Devi', 'user', 'Pension'),
            ('user.time1', generate_password_hash('User@2024'), 'Ms. Rekha Nair', 'user', 'Time Office'),
            ('user.time2', generate_password_hash('User@2024'), 'Mr. Krishna Das', 'user', 'Time Office'),
            ('user.leave1', generate_password_hash('User@2024'), 'Mr. Sanjay Joshi', 'user', 'Leave'),
            ('user.leave2', generate_password_hash('User@2024'), 'Ms. Sunita Roy', 'user', 'Leave'),
            ('user.bills1', generate_password_hash('User@2024'), 'Ms. Pooja Sharma', 'user', 'Bills'),
            ('user.bills2', generate_password_hash('User@2024'), 'Mr. Rahul Verma', 'user', 'Bills'),
            ('user.dak1', generate_password_hash('User@2024'), 'Mr. Rahul Singh', 'user', 'DAK'),
            ('user.dak2', generate_password_hash('User@2024'), 'Ms. Anita Patel', 'user', 'DAK')
        ]
        
        for user in default_users:
            cursor.execute(
                "INSERT INTO users (username, password, name, role, user_group) VALUES (%s, %s, %s, %s, %s)",
                user
            )
        
        conn.commit()
        print(f"✅ Created {len(default_users)} default users!")
    
    cursor.close()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, username, name, role, user_group FROM users ORDER BY id")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        print(f"❌ Error getting users: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
def add_user():
    """Add new user"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        data = request.json
        cursor = conn.cursor()
        
        # Check if username exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (data['username'],))
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Username already exists'}), 400
        
        cursor.execute(
            "INSERT INTO users (username, password, name, role, user_group) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (data['username'], generate_password_hash(data['password']), data['name'], data['role'], data.get('group'))
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ User created: {data['username']}")
        return jsonify({'success': True, 'id': user_id})
    except Exception as e:
        print(f"❌ Error adding user: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        data = request.json
        cursor = conn.cursor()
        
        # Check if new username conflicts
        cursor.execute("SELECT id FROM users WHERE username = %s AND id != %s", (data['username'], user_id))
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Username already exists'}), 400
        
        if data.get('password'):
            cursor.execute(
                "UPDATE users SET username=%s, password=%s, name=%s WHERE id=%s",
                (data['username'], generate_password_hash(data['password']), data['name'], user_id)
            )
        else:
            cursor.execute(
                "UPDATE users SET username=%s, name=%s WHERE id=%s",
                (data['username'], data['name'], user_id)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ User updated: ID {user_id}")
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Error updating user: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ User deleted: ID {user_id}")
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Get all reports"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM reports ORDER BY report_date DESC, report_time DESC")
        reports = cursor.fetchall()
        
        # Convert date and time to strings
        for report in reports:
            if report.get('report_date'):
                report['date'] = report['report_date'].strftime('%Y-%m-%d')
            if report.get('report_time'):
                report['time'] = str(report['report_time'])
        
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'reports': reports})
    except Exception as e:
        print(f"❌ Error getting reports: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports', methods=['POST'])
def add_report():
    """Add new report"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        data = request.json
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO reports (userId, userName, user_group, report_date, report_time, 
               f1, f2, f3, f4, f5, f6, f7, f8) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (data['userId'], data['userName'], data.get('group'), data['date'], data['time'],
             data.get('f1'), data.get('f2'), data.get('f3'), data.get('f4'),
             data.get('f5'), data.get('f6'), data.get('f7'), data.get('f8'))
        )
        report_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Report created: ID {report_id}")
        return jsonify({'success': True, 'id': report_id})
    except Exception as e:
        print(f"❌ Error adding report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks - FIXED VERSION"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        tasks = cursor.fetchall()
        
        # FIX: Map database column names to frontend expected names
        for task in tasks:
            # Handle both camelCase and lowercase column names
            if 'userid' in task and 'userId' not in task:
                task['userId'] = task['userid']
            if 'username' in task and 'userName' not in task:
                task['userName'] = task['username']
            if 'duedate' in task and 'dueDate' not in task:
                task['dueDate'] = task['duedate']
            if 'assignedby' in task and 'assignedBy' not in task:
                task['assignedBy'] = task['assignedby']
            if 'assigneddate' in task and 'assignedDate' not in task:
                task['assignedDate'] = task['assigneddate']
                
            # Convert dates to strings
            if task.get('dueDate') and hasattr(task['dueDate'], 'strftime'):
                task['dueDate'] = task['dueDate'].strftime('%Y-%m-%d')
            elif task.get('duedate') and hasattr(task['duedate'], 'strftime'):
                task['dueDate'] = task['duedate'].strftime('%Y-%m-%d')
        
        cursor.close()
        conn.close()
        print(f"✅ Loaded {len(tasks)} tasks from PostgreSQL")
        return jsonify({'success': True, 'tasks': tasks})
    except Exception as e:
        print(f"❌ Error getting tasks: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Add new task - FIXED VERSION"""
    print("🔵 Received task creation request")
    conn = get_db_connection()
    if not conn:
        print("❌ Database connection failed")
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        data = request.json
        print(f"📝 Task data received: {data}")
        
        cursor = conn.cursor()
        
        # Handle both camelCase and lowercase field names
        user_id = data.get('userId') or data.get('userid')
        user_name = data.get('userName') or data.get('username')
        title = data.get('title')
        description = data.get('description', '')
        due_date = data.get('dueDate') or data.get('duedate')
        priority = data.get('priority', 'Medium')
        assigned_by = data.get('assignedBy') or data.get('assignedby', 'Admin')
        
        if not user_id or not user_name or not title:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        print(f"Creating task: {title} for user {user_name} (ID: {user_id})")
        
        cursor.execute(
            """INSERT INTO tasks (userId, userName, title, description, dueDate, priority, 
               status, assignedBy, assignedDate) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (user_id, user_name, title, description, due_date, priority, 'Pending', assigned_by, datetime.now())
        )
        task_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Task created with ID: {task_id}")
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'id': task_id})
    except Exception as e:
        print(f"❌ Error creating task: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update task"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        data = request.json
        cursor = conn.cursor()
        
        # Build update query
        update_fields = []
        values = []
        
        if 'status' in data:
            update_fields.append("status = %s")
            values.append(data['status'])
        if 'adminComment' in data:
            update_fields.append("adminComment = %s")
            values.append(data['adminComment'])
        if 'uploadedFiles' in data:
            update_fields.append("uploadedFiles = %s")
            values.append(json.dumps(data['uploadedFiles']))
        if 'extensionRequest' in data:
            update_fields.append("extensionRequest = %s")
            values.append(json.dumps(data['extensionRequest']))
        
        values.append(task_id)
        
        if update_fields:
            query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(query, values)
            conn.commit()
        
        cursor.close()
        conn.close()
        print(f"✅ Task updated: ID {task_id}")
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Error updating task: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete task"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Task deleted: ID {task_id}")
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Error deleting task: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Initializing HR System with PostgreSQL...")
    init_database()
    print("✅ Server starting on port 10000...")
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)), debug=False)
