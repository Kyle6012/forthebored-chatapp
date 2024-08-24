import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from utils.db import create_tables, add_user, verify_user, get_db_connection, check_email
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.secret_key = 'bealthguy701'
socketio = SocketIO(app, async_mode='eventlet')
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

create_tables()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('chat'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if verify_user(username, password):
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if check_email(email):
            return 'Email already registered', 400
        if add_user(username, email, password):
            return redirect(url_for('login'))
        else:
            return 'Username already exists!', 400
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html')

@socketio.on('join')
def handle_join(data):
    username = session.get('username')
    room = data['room']
    join_room(room)
    emit('status', {'msg': f'{username} has entered the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    username = session.get('username')

    if not username:
        return 'User not found!'

    message = data['msg']
    save_message(username, room, message)
    emit('message', {'msg': message, 'username': username}, room=room)

@socketio.on('private_message')
def handle_private_message(data):
    sender = session.get('username')
    receiver = data['receiver']
    message = data['msg']
    save_private_message(sender, receiver, message)
    emit('private_message', {'msg': message, 'sender': sender}, room=receiver)

@socketio.on('leave')
def handle_leave(data):
    username = session.get('username')
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f'{username} has left the room.'}, room=room)

def save_message(username, room, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (username, room, message) VALUES (?, ?, ?)', (username, room, message))
    conn.commit()
    conn.close()

def save_private_message(sender, receiver, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO private_messages (sender, receiver, message) VALUES (?, ?, ?)', (sender, receiver, message))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
