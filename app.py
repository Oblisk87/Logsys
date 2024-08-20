from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Dummy check for username and password
    if username == 'Freedom' and password == 'password':
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'detail': 'Invalid credentials'}), 401

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    status = data.get('status')

    # Dummy update logic
    user = {
        'id': user_id,
        'email': email,
        'username': username,
        'password': password,  # In a real application, hash the password
        'status': status
    }
    return jsonify({'message': 'User updated successfully', 'user': user})

@app.route('/users')
def get_users():
    users = [
        {'id': 1, 'email': 'freedom@example.com', 'username': 'Freedom', 'status': 'active'}
    ]
    return jsonify(users)

@app.route('/logs')
def get_logs():
    logs = [
        {'date': '2023-10-01', 'resource_name': 'Resource1', 'category': 'Category1', 'message': 'Log message 1', 'level': 'INFO'}
    ]
    return jsonify(logs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
