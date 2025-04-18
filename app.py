from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
from datetime import datetime, timedelta
import PyPDF2
from docx import Document
import base64

app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load environment variables
load_dotenv()

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == "admin" and password == "7782":
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/translate', methods=['POST'])
@login_required
def translate():
    data = request.json
    text = data.get('text')
    target_country = data.get('target_country')
    
    # Initialize Gemini client
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')
    
    # Translation logic here
    # ...
    
    return jsonify({'translation': 'Translated text'})

@app.route('/history')
@login_required
def get_history():
    try:
        with open('history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
        return jsonify(history)
    except:
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True) 