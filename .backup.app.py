
import jwt
import datetime
from functools import wraps
from flask import Flask, send_from_directory, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

app = Flask(__name__, static_folder='frontend')
app.config['SECRET_KEY'] = 'your_secret_key'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-tokens')
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

@app.route('/login', methods=['POST'])
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
        return jsonify({"token": token}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

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
    return jsonify({"message": "User updated successfully"}), 200

@app.route('/delete_user', methods=['DELETE'])
@token_required
def delete_user():
    user_id = request.json['id']
    conn = sqlite3.connect('Logsys/users.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "User deleted successfully"}), 200

if __name__ == '__main__':
    app.run(port=5000)
