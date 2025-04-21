# ─── IMPORTS ────────────────────────────────────────────────────────────────
from flask import Flask, render_template, request, redirect, url_for, session, Response, flash
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from gridfs import GridFS  # For storing large video files
from flask_socketio import SocketIO  # Real-time communication
import cv2, numpy as np, mss, time
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os
from bson.objectid import ObjectId

# ─── INITIALIZATION ─────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secure_secure_key_here")
socketio = SocketIO(app)

# ─── MONGODB SETUP ──────────────────────────────────────────────────────────
try:
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.server_info()  # Check MongoDB connection
    db = client['livestream_db']
    users = db['users']
    fs = GridFS(db, collection='videos')  # GridFS for storing uploaded videos
    print("Connected to MongoDB successfully!")
except ServerSelectionTimeoutError as e:
    print(f"Failed to connect to MongoDB: {e}")

# ─── CREATE ADMIN USER ──────────────────────────────────────────────────────
if users.count_documents({}) == 0:
    users.create_index('username', unique=True)
    users.insert_one({
        '_id': '67f543c79842d98dcb52746e',
        'username': 'admin',
        'email': '',
        'password_hash': generate_password_hash('admin123'),
        'role': 'admin',
        'password': ''
    })

# ─── STREAM STATUS ──────────────────────────────────────────────────────────
stream_status = {
    'live': False,
    'viewers': 0
}
MAX_VIEWERS = 5

# ─── LOGIN REQUIRED DECORATOR ───────────────────────────────────────────────
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'username' not in session:
                flash('Login required', 'error')
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash('Unauthorized access', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

# ─── ROUTES ─────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return redirect(url_for('dashboard') if 'username' in session else 'login')

# ─── LOGIN ──────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users.find_one({'username': username})
        if user:
            if user.get('password_hash') and check_password_hash(user['password_hash'], password):
                session['username'] = username
                session['role'] = user.get('role', 'viewer')
                return redirect(url_for('dashboard'))
            elif user.get('password') == password:  # Legacy plaintext
                users.update_one({'username': username}, {'$set': {'password_hash': generate_password_hash(password)}})
                session['username'] = username
                session['role'] = user.get('role', 'viewer')
                return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

# ─── REGISTER ───────────────────────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Username and password are required', 'error')
        elif users.find_one({'username': username}):
            flash('Username already exists', 'error')
        else:
            users.insert_one({
                'username': username,
                'email': '',
                'password_hash': generate_password_hash(password),
                'role': 'viewer',
                'password': ''
            })
            flash('Registration successful! Please login', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

# ─── DASHBOARD ──────────────────────────────────────────────────────────────
@app.route('/dashboard')
@login_required()
def dashboard():
    return render_template('dashboard.html', username=session['username'],
                           role=session.get('role', 'viewer'),
                           stream_status=stream_status)

# ─── VIDEO UPLOAD + LIST ────────────────────────────────────────────────────
@app.route('/recorded_videos', methods=['GET', 'POST'])
@login_required()
def recorded_videos():
    videos = [{
        'filename': v.filename,
        'id': str(v._id),
        'uploaded_by': v.metadata.get('uploaded_by', 'Unknown'),
        'upload_time': v.upload_date.strftime('%Y-%m-%d %H:%M:%S')
    } for v in fs.find()]

    if request.method == 'POST' and session.get('role') == 'admin':
        video = request.files.get('video')
        if not video or video.filename == '':
            flash('No selected video', 'error')
        else:
            fs.put(video, filename=video.filename, metadata={
                'uploaded_by': session['username'],
                'upload_date': datetime.utcnow()
            })
            flash('Video uploaded successfully!', 'success')
            return redirect(url_for('recorded_videos'))

    return render_template('recorded_videos.html',
                           username=session['username'],
                           videos=videos,
                           is_admin=session.get('role') == 'admin')

# ─── DELETE VIDEO ───────────────────────────────────────────────────────────
@app.route('/delete_video/<video_id>', methods=['POST'])
@login_required(role='admin')
def delete_video(video_id):
    try:
        fs.delete(ObjectId(video_id))
        flash('Video deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting video: {e}', 'error')
    return redirect(url_for('recorded_videos'))

# ─── STREAM VIDEO ───────────────────────────────────────────────────────────
@app.route('/video/<video_id>')
def get_video(video_id):
    video = fs.get(ObjectId(video_id))
    return Response(video.read(), mimetype='video/mp4')

# ─── STREAM CONTROL ─────────────────────────────────────────────────────────
@app.route('/start_stream')
@login_required(role='admin')
def start_stream():
    stream_status['live'] = True
    return redirect(url_for('live_stream'))

@app.route('/stop_stream', methods=['POST'])
@login_required(role='admin')
def stop_stream():
    stream_status['live'] = False
    stream_status['viewers'] = 0
    socketio.emit('stream_ended')
    return redirect(url_for('dashboard'))

# ─── ADMIN STREAM PAGE ──────────────────────────────────────────────────────
@app.route('/live_stream')
@login_required(role='admin')
def live_stream():
    return render_template('live_stream.html', stream_status=stream_status)

# ─── VIEW STREAM ────────────────────────────────────────────────────────────
@app.route('/view_stream')
@login_required()
def view_stream():
    if not stream_status['live']:
        return render_template('stream_offline.html')
    if stream_status['viewers'] >= MAX_VIEWERS:
        return render_template('viewer_limit.html')
    stream_status['viewers'] += 1
    socketio.emit('viewer_count', stream_status['viewers'])
    return render_template('view_stream.html', stream_status=stream_status)

# ─── VIDEO STREAMING (SCREEN CAPTURE) ───────────────────────────────────────
@app.route('/video_feed')
def video_feed():
    def generate():
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            while stream_status['live']:
                img = sct.grab(monitor)
                frame = cv2.resize(np.array(img), (1280, 720))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                time.sleep(0.05)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ─── VIEWER EXIT STREAM ─────────────────────────────────────────────────────
@app.route('/leave_stream')
def leave_stream():
    if 'username' in session:
        stream_status['viewers'] = max(0, stream_status['viewers'] - 1)
        socketio.emit('viewer_count', stream_status['viewers'])
    return redirect(url_for('dashboard'))

# ─── LOGOUT ─────────────────────────────────────────────────────────────────
@app.route('/logout')
def logout():
    if 'username' in session:
        stream_status['viewers'] = max(0, stream_status['viewers'] - 1)
        socketio.emit('viewer_count', stream_status['viewers'])
    session.clear()
    return redirect(url_for('login'))

# ─── SOCKET DISCONNECT EVENT ────────────────────────────────────────────────
@socketio.on('disconnect')
def handle_disconnect():
    stream_status['viewers'] = max(0, stream_status['viewers'] - 1)
    socketio.emit('viewer_count', stream_status['viewers'])

# ─── RUN SERVER ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Crucial for Docker
