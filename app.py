from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure random key in production

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')  # Connect to MongoDB
db = client['livestream_db']  # Use the 'livestream_db' database
users = db['users']  # Use or create a collection named 'users'

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username and password match
        user = users.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials!"

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username already exists
        if users.find_one({'username': username}):
            return "Username already exists. Please choose a different username."

        # Save the new user to MongoDB
        users.insert_one({'username': username, 'password': password})
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/recorded_videos')
def recorded_videos():
    if 'username' in session:
        return render_template('recorded_videos.html')
    return redirect(url_for('login'))

@app.route('/live_stream')
def live_stream():
    if 'username' in session:
        return render_template('live_stream.html')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)