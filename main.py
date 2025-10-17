from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_database
import asyncio

app = Flask(__name__)
CORS(app)

event_loop = asyncio.new_event_loop()
asyncio.set_event_loop(event_loop)
db = get_database()

def run_async(coro):
    return event_loop.run_until_complete(coro)

@app.route('/login', methods=['POST'])
def login():
    print("hi")
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'status': 'error', 'message': 'email and password required'}), 400

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

    if not email or not password or not fullname:
        return jsonify({'status': 'error', 'message': 'email, password and fullname required'}), 400

    user = run_async(db.add_user(fullname, email, password))
    if not user:
        return jsonify({'status': 'error', 'message': 'user with that email already exists'}), 409

    return jsonify({
        'status': 'ok',
        'message': 'register successful',
        'user': user
    }), 201

if __name__ == '__main__':
    app.run(debug=True)