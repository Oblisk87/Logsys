
import jwt
import datetime
from functools import wraps
from flask import Flask, send_from_directory, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
import sqlite3
import sys

# Controleer of SQLite draait
try:
    conn = sqlite3.connect('Logsys/users.db')
    conn.execute('SELECT 1')
    conn.close()
except sqlite3.Error as e:
    print(f"SQLite fout: {e}")
    sys.exit(1)

# Controleer of Flask-CORS is geïnstalleerd
try:
    import flask_cors
except ImportError:
    print("Flask-CORS is niet geïnstalleerd.")
    sys.exit(1)

# Controleer of Werkzeug is geïnstalleerd
try:
    import werkzeug
except ImportError:
    print("Werkzeug is niet geïnstalleerd.")
    sys.exit(1)

# Controleer of PyJWT is geïnstalleerd
try:
    import jwt
except ImportError:
    print("PyJWT is niet geïnstalleerd.")
    sys.exit(1)
from flask_cors import CORS, cross_origin
import datetime
import sqlite3

app = Flask(__name__, static_folder='frontend')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
CORS(app, resources={r"/*": {"origins": "*"}})

def log_action(resource, category, message, level):
    conn = sqlite3.connect('Logsys/users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (date, resource, category, message, level) VALUES (?, ?, ?, ?, ?)",
                   (datetime.datetime.now(), resource, category, message, level))
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'webp', 'mp4'}

@app.route('/upload', methods=['POST'])
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]
        app.logger.debug(f"Authorization Header: {request.headers.get('Authorization')}")
        app.logger.debug(f"Extracted Token: {token}")
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

@token_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        resource = 'file'
        category = 'upload'
        message = f'File {filename} uploaded'
        level = 'info'
        conn = sqlite3.connect('Logsys/users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (date, resource, category, message, level) VALUES (?, ?, ?, ?, ?)",
                       (datetime.datetime.now(), resource, category, message, level))
        conn.commit()
        conn.close()
        return jsonify({'message': 'File uploaded successfully', 'location': f"/media/{filename}"}), 201
    return jsonify({'message': 'File type not allowed'}), 400

def create_user(username, password):
    conn = sqlite3.connect('Logsys/users.db')
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('Logsys/users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user[0], password):
        return True
    return False

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    try:
        create_user(username, password)
        return jsonify({'message': 'User created successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username already exists'}), 409

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    if authenticate_user(username, password):
        token = jwt.encode({'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'])
        return jsonify({'token': token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]
        app.logger.debug(f"Authorization Header: {request.headers.get('Authorization')}")
        app.logger.debug(f"Extracted Token: {token}")
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/faq')
def faq():
    return send_from_directory('frontend', 'faq.html')



@app.route('/help')
def help():
    return send_from_directory('frontend', 'help.html')

@app.route('/support')
def support():
    return send_from_directory('frontend', 'support.html')

@app.route('/about')
def about():
    return send_from_directory('frontend', 'about.html')

@app.route('/privacy_policy')
def privacy_policy():
    return send_from_directory('frontend', 'privacy_policy.html')

@app.route('/terms_of_service')
def terms_of_service():
    return send_from_directory('frontend', 'terms_of_service.html')

@app.route('/logs_view')
def logs_view():
    return send_from_directory('frontend', 'logs_view.html')

@app.route('/contact')
def contact():
    return send_from_directory('frontend', 'contact.html')

@app.route('/api/resources', methods=['GET'])
def fetch_resources():
    try:
        conn = sqlite3.connect('Logsys/logs.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT resource FROM logs")
        resources = cursor.fetchall()
        
        conn.close()
        
        # Convert the list of tuples to a list of strings
        resources = [resource[0] for resource in resources]
        
        return jsonify(resources), 200
    except sqlite3.Error as e:
        return jsonify({'message': 'Internal Server Error', 'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def fetch_logs():
    conn = sqlite3.connect('Logsys/logs.db')
    cursor = conn.cursor()
    
    # Fetch query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search_query = request.args.get('search_query')
    resources = request.args.getlist('resources')
    categories = request.args.getlist('categories')
    levels = request.args.getlist('levels')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    # Build the query
    query = "SELECT id, date, resource, category, message, level FROM logs WHERE 1=1"
    params = []
    
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    if search_query:
        query += " AND (message LIKE ? OR resource LIKE ? OR category LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])
    if resources:
        query += " AND resource IN ({})".format(','.join('?' for _ in resources))
        params.extend(resources)
    if categories:
        query += " AND category IN ({})".format(','.join('?' for _ in categories))
        params.extend(categories)
    if levels:
        query += " AND level IN ({})".format(','.join('?' for _ in levels))
        params.extend(levels)
    
    query += " ORDER BY date DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])
    
    cursor.execute(query, params)
    logs = cursor.fetchall()
    conn.close()
    
    return jsonify(logs)

@app.route('/user/<int:user_id>', methods=['GET', 'PUT'])
@token_required
def get_user(user_id):
    if request.method == 'GET':
        conn = sqlite3.connect('Logsys/users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, username, status FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return jsonify({'id': user[0], 'email': user[1], 'username': user[2], 'status': user[3]})
        return jsonify({'message': 'User not found'}), 404
    elif request.method == 'PUT':
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        status = data.get('status')
        password = data.get('password')
        conn = sqlite3.connect('Logsys/users.db')
        cursor = conn.cursor()
        if password:
            hashed_password = generate_password_hash(password)
            cursor.execute("UPDATE users SET email = ?, username = ?, status = ?, password = ? WHERE id = ?", (email, username, status, hashed_password, user_id))
        else:
            cursor.execute("UPDATE users SET email = ?, username = ?, status = ? WHERE id = ?", (email, username, status, user_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User updated successfully'})

@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    import time
    retries = 5
    while retries > 0:
        try:
            conn = sqlite3.connect('Logsys/users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            break
        except sqlite3.OperationalError:
            retries -= 1
            time.sleep(0.1)
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[0], password):
        token = jwt.encode({'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        print(f"Generated Token: {token}")
        log_action('auth', 'login', f'User {username} logged in', 'info')
        return jsonify({"token": token}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'mp4'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
@token_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        log_action('file', 'upload', f'File {filename} uploaded', 'info')
        return jsonify({'message': 'File uploaded successfully', 'url': f"/uploads/{filename}"}), 201
    return jsonify({'message': 'File type not allowed'}), 400

@app.route('/users', methods=['GET'])
@token_required
def get_users():
    import time
    retries = 5
    while retries > 0:
        try:
            conn = sqlite3.connect('Logsys/users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, username, status FROM users")
            break
        except sqlite3.OperationalError:
            retries -= 1
            time.sleep(0.1)
    users = cursor.fetchall()
    conn.close()
    return jsonify(users), 200

@app.route('/add_user', methods=['POST'])
@token_required
def add_user():
    data = request.json
    username = data['username']
    password = generate_password_hash(data['password'])
    conn = sqlite3.connect('Logsys/users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, status) VALUES (?, ?, ?)", (username, password, 'active'))
    conn.commit()
    import time
    time.sleep(0.1)
    conn.close()
    log_action('user', 'add', f'User {username} added', 'info')
    return jsonify({"message": "User added successfully"}), 201

@app.route('/edit_user', methods=['PUT'])
@token_required
def edit_user():
    data = request.json
    user_id = data['id']
    username = data['username']
    password = generate_password_hash(data['password'])
    conn = sqlite3.connect('Logsys/users.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (username, password, user_id))
    conn.commit()
    conn.close()
    log_action('user', 'edit', f'User {username} updated', 'info')
    return jsonify({"message": "User updated successfully"}), 200

@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    data = request.json
    user_id = data['id']
    conn = sqlite3.connect('Logsys/users.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    log_action('user', 'delete', f'User {user_id} deleted', 'info')
    return jsonify({"message": "User deleted successfully"}), 200

@app.route('/logs', methods=['GET'])
def retrieve_logs():
    conn = sqlite3.connect('Logsys/logs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs")
    logs = cursor.fetchall()
    conn.close()
    return jsonify(logs), 200

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.run(port=5001)
