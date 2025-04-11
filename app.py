from flask import Flask, render_template, request, redirect, url_for, session, Response
from pymongo import MongoClient
from flask_socketio import SocketIO
import cv2
import numpy as np
import mss
import os
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['livestream_db']
users = db['users']

# Stream management
stream_status = {
    'live': False,
    'viewers': 0
}
MAX_VIEWERS = 5

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username
            session['role'] = 'admin' if username.lower() == 'admin' else 'viewer'
            return redirect(url_for('dashboard'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.find_one({'username': username}):
            return "Username taken", 400
        users.insert_one({'username': username, 'password': password, 'role': 'viewer'})
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html',
                           username=session['username'],
                           role=session['role'],
                           stream_status=stream_status)

@app.route('/recorded_videos')
def recorded_videos():
    if 'username' not in session:
        return redirect(url_for('login'))

    video_dir = os.path.join(app.static_folder, 'videos')
    videos = [f for f in os.listdir(video_dir) if f.endswith('.mp4')] if os.path.exists(video_dir) else []

    return render_template('recorded_videos.html',
                           username=session['username'],
                           videos=videos)

@app.route('/start_stream')
def start_stream():
    if 'username' not in session or session['role'] != 'admin':
        return "Unauthorized", 403
    stream_status['live'] = True
    return redirect(url_for('live_stream'))

@app.route('/stop_stream')
def stop_stream():
    if 'username' not in session or session['role'] != 'admin':
        return "Unauthorized", 403
    stream_status['live'] = False
    stream_status['viewers'] = 0
    socketio.emit('stream_ended')
    return redirect(url_for('dashboard'))

@app.route('/live_stream')
def live_stream():
    if 'username' not in session or session['role'] != 'admin':
        return "Unauthorized", 403
    return render_template('live_stream.html',
                           username=session['username'],
                           stream_status=stream_status)

@app.route('/view_stream')
def view_stream():
    if 'username' not in session:
        return redirect(url_for('login'))
    if not stream_status['live']:
        return "Stream offline", 403
    if stream_status['viewers'] >= MAX_VIEWERS:
        return "Viewer limit reached", 403

    stream_status['viewers'] += 1
    socketio.emit('viewer_count', stream_status['viewers'])

    return render_template('view_stream.html',
                           username=session['username'],
                           stream_status=stream_status)


@app.route('/video_feed')
def video_feed():
    def generate():
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Adjust if needed for different screen

            while stream_status['live']:
                # Capture screenshot
                img = sct.grab(monitor)

                # Convert to numpy array
                frame = np.array(img)

                # Optional: Resize frame (reduce bandwidth, increase performance)
                frame = cv2.resize(frame, (1280, 720))

                # Convert BGRA to BGR
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                # Encode to JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue

                # Stream frame
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                
                # Optional: Limit FPS
                time.sleep(0.03)  # ~30 FPS

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/leave_stream')
def leave_stream():
    if 'username' in session and stream_status['viewers'] > 0:
        stream_status['viewers'] -= 1
        socketio.emit('viewer_count', stream_status['viewers'])
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@socketio.on('disconnect')
def handle_disconnect():
    if 'username' in session and stream_status['viewers'] > 0:
        stream_status['viewers'] -= 1
        socketio.emit('viewer_count', stream_status['viewers'])

@app.context_processor
def inject_stream_status():
    return {'stream_status': stream_status}

if __name__ == '__main__':
  import eventlet
eventlet.monkey_patch()
socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
