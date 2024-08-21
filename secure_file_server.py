
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
import hashlib
import hmac
import base64
import sqlite3
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'mp4'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB
SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
DATABASE = os.getenv('DATABASE', 'users.db')

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set up logging
handler = RotatingFileHandler('server.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                      )''')
    conn.commit()
    conn.close()

init_db()

# Set up rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return jsonify({'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def check_auth(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user[0], password):
        return True
    return False

def verify_signature(data, signature):
    mac = hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)

@app.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    app.logger.info('Register endpoint called')
    data = request.get_json()
    app.logger.info(f'Received data: {data}')
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    hashed_password = generate_password_hash(password)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username already exists'}), 400
    finally:
        conn.close()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/upload', methods=['POST'])
@authenticate
@limiter.limit("10 per minute")
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename
        while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], new_filename)):
            new_filename = f"{base}_{counter}{ext}"
            counter += 1
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
        filename = new_filename
    category = request.form.get('category', 'default')
    if category not in ['anticheat', 'log', 'media', 'mediapic', 'mediamov', 'mediapolitie', 'mediapicpolitie', 'mediamovpolitie']:
        return jsonify({'message': 'Invalid category'}), 400
    return jsonify({'message': 'File uploaded successfully', 'filename': filename, 'category': category}), 201
    # Voeg hier de 202 - Accepted statuscode toe
    # return jsonify({'message': 'Accepted'}), 202
    return jsonify({'message': 'File type not allowed'}), 400

@app.route('/files/<filename>', methods=['GET'])
@authenticate
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(port=8000)


