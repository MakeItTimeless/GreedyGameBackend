from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_database
import asyncio

app = Flask(__name__)
CORS(app)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Accept, Content-Type, Origin"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

event_loop = asyncio.new_event_loop()
asyncio.set_event_loop(event_loop)
db = get_database()

def run_async(coro):
    return event_loop.run_until_complete(coro)

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({'status': 'ok', 'message': 'hello world'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'status': 'error', 'message': 'email and password required'}), 400
    
    ADMIN_EMAIL = "admin@greedygame.io"
    ADMIN_PASSWORD = "admin"

    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        return jsonify({
            'status': 'ok',
            'message': 'admin login successful',
            'user': {
                'fullname': 'Admin User',
                'email': ADMIN_EMAIL,
                'user_type': 'super_user'
            }
        }), 200

    user = run_async(db.login_user(email, password))

    if not user:
        return jsonify({'status': 'error', 'message': 'invalid credentials'}), 401

    return jsonify({
        'status': 'ok',
        'message': 'login successful',
        'user': user
    }), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    fullname = data.get('fullname')
    user_type = "user"

    if not email or not password or not fullname:
        return jsonify({'status': 'error', 'message': 'email, password and fullname required'}), 400

    if user_type not in ('user', 'super_user'):
        return jsonify({'status': 'error', 'message': "user_type must be 'user' or 'super_user'"}), 400

    user = run_async(db.add_user(fullname, email, password, user_type))
    if not user:
        return jsonify({'status': 'error', 'message': 'user with that email already exists'}), 409

    return jsonify({
        'status': 'ok',
        'message': 'register successful',
        'user': user
    }), 201

@app.route('/change_user_type', methods=['POST'])
def change_user_type():
    data = request.get_json() or {}
    email = data.get('email')
    new_type = data.get('new_type')

    if not email or not new_type:
        return jsonify({'status': 'error', 'message': 'email and new_type required'}), 400

    if new_type not in ('user', 'super_user'):
        return jsonify({'status': 'error', 'message': "new_type must be 'user' or 'super_user'"}), 400

    user = run_async(db.change_user_type(email, new_type))
    if not user:
        return jsonify({'status': 'error', 'message': 'user not found'}), 404

    return jsonify({
        'status': 'ok',
        'message': 'user type changed successfully',
        'user': user
    }), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    users = run_async(db.list_users())
    return jsonify({
        'status': 'ok',
        'users': users
    }), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)