from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'randomsecretkey123')

# SocketIO - gevent use karan nisa async_mode eka auto detect wenawa
socketio = SocketIO(app, cors_allowed_origins="*")

# Room walata users store karanna
rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/room/<room_id>')
def room(room_id):
    return render_template('room.html', room_id=room_id)

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    if room not in rooms:
        rooms[room] = []
    rooms[room].append(request.sid)
    emit('message', {'msg': 'User joined'}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    if room in rooms and request.sid in rooms[room]:
        rooms[room].remove(request.sid)
    emit('message', {'msg': 'User left'}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    emit('message', data, room=room)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    socketio.run(app, host='0.0.0.0', port=port)
