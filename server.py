from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, emit
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'flowchat_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads' # <-- 1. MEKA ADD
db = SQLAlchemy(app)
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} # <-- 2. MEKA ADD

def allowed_file(filename): # <-- 3. MEKA ADD
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database Model <-- 4. MEKA OKKOMA REPLACE KARANNA
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200), nullable=False)
    profile_pic = db.Column(db.String(200), default='default.png') # ALUTH
    status = db.Column(db.String(20), default='offline') # ALUTH
    last_seen = db.Column(db.DateTime, default=datetime.utcnow) # ALUTH

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all() # first time witharak

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Register <-- 5. EMAIL ADD KARANNA
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email'] # ALUTH
        password = generate_password_hash(request.form['password'])
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Login <-- 6. LOGIN UNAMA ONLINE KARANA EKA
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            user.status = 'online' # ALUTH
            db.session.commit() # ALUTH
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# Logout <-- 7. LOGOUT UNAMA OFFLINE KARANA EKA
@app.route('/logout')
@login_required
def logout():
    current_user.status = 'offline' # ALUTH
    current_user.last_seen = datetime.utcnow() # ALUTH
    db.session.commit() # ALUTH
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html', username=current_user.username)

@app.route('/room/<room>')
@login_required
def room(room):
    return render_template('room.html', room=room, username=current_user.username)

# 8. PROFILE ROUTE EKA OKKOMA ALUTH EKA
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if request.form.get('username'):
            current_user.username = request.form['username']
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{current_user.id}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.profile_pic = filename
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('profile.html', user=current_user)

@socketio.on('join')
def on_join(data):
    join_room(data['room'])

@socketio.on('message')
def handle_message(data):
    emit('message', data, room=data['room'])

if __name__ == '__main__':
    socketio.run(app)
