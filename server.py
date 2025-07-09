from flask import Flask, request, jsonify, render_template, session
import os
import uuid
import subprocess
import threading
import telebot
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
UPLOAD_FOLDER = 'user_data'
ALLOWED_EXTENSIONS = {'py', 'txt'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Telegram Bot Manager
class BotManager:
    def __init__(self):
        self.active_bots = {}
    
    def start_bot(self, user_id, token, code):
        bot = telebot.TeleBot(token)
        
        @bot.message_handler(commands=['start'])
        def send_welcome(message):
            bot.reply_to(message, f"Hello! This is your personal bot (User {user_id})")
        
        # Save bot file
        user_dir = os.path.join(UPLOAD_FOLDER, user_id)
        os.makedirs(user_dir, exist_ok=True)
        
        bot_file = os.path.join(user_dir, 'bot.py')
        with open(bot_file, 'w') as f:
            f.write(code)
        
        # Run in background
        def run():
            bot.infinity_polling()
        
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
        
        self.active_bots[user_id] = {
            'bot': bot,
            'thread': thread,
            'file': bot_file
        }

bot_manager = BotManager()

@app.before_request
def assign_user_id():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        user_dir = os.path.join(UPLOAD_FOLDER, session['user_id'])
        os.makedirs(user_dir, exist_ok=True)
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(user_dir, filename)
        file.save(filepath)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'user_id': session['user_id']
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/run', methods=['POST'])
def run_bot():
    data = request.json
    user_id = session['user_id']
    code = data.get('code', '')
    token = data.get('token', '')
    
    if not code or not token:
        return jsonify({'error': 'Missing code or token'}), 400
    
    try:
        bot_manager.start_bot(user_id, token, code)
        return jsonify({
            'message': 'Bot started successfully',
            'user_id': user_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
