from flask import Flask, render_template, request, session, redirect, send_from_directory
from flask_socketio import SocketIO, send, join_room
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flowchat_secret_123'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/chat')
def chat():
    name = request.args.get('name')
    room = request.args.get('room')
    if not name or not room: 
        return redirect('/')
    session['name'] = name
    session['room'] = room
    return render_template('chat.html', name=name, room=room)

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@socketio.on('join')
def on_join(data):
    join_room(data['room'])
    send({'name': 'System', 'msg': f"{data['name']} joined FlowCHAT"}, to=data['room'])

@socketio.on('message')
def handle_message(data):
    send({'name': session.get('name'), 'msg': data['msg']}, to=session.get('room'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)