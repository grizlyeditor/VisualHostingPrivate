from flask import Flask, request, jsonify, render_template, session
import os
import uuid
import subprocess
import threading
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
UPLOAD_FOLDER = 'user_data'
PREBUILD_BOTS = {
    'echo': {
        'code': '''from telebot import TeleBot

bot = TeleBot("{}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"You said: {message.text}")

bot.infinity_polling()''',
        'description': 'Simple bot that echoes your messages'
    },
    'welcome': {
        'code': '''from telebot import TeleBot

bot = TeleBot("{}")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to your custom bot!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "I'm a simple welcome bot")

bot.infinity_polling()''',
        'description': 'Bot with welcome message'
    }
}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.before_request
def assign_user_id():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

@app.route('/')
def home():
    return render_template('index.html', bots=PREBUILD_BOTS)

@app.route('/run-bot', methods=['POST'])
def run_bot():
    user_id = session['user_id']
    data = request.json
    
    # Create user directory
    user_dir = os.path.join(UPLOAD_FOLDER, user_id)
    os.makedirs(user_dir, exist_ok=True)
    
    # Handle pre-built bots
    if data.get('prebuild'):
        bot_type = data['bot_type']
        token = data.get('token', 'YOUR_DEFAULT_TOKEN')  # Replace with a real token
        
        if bot_type not in PREBUILD_BOTS:
            return jsonify({'error': 'Invalid bot type'}), 400
        
        bot_code = PREBUILD_BOTS[bot_type]['code'].format(token)
        bot_file = os.path.join(user_dir, f'{bot_type}_bot.py')
    
    # Handle custom code
    else:
        bot_code = data['code']
        token = data['token']  # Required for custom code
        bot_file = os.path.join(user_dir, 'custom_bot.py')
    
    # Save bot file
    with open(bot_file, 'w') as f:
        f.write(bot_code)
    
    # Run bot in background
    def run_bot_process():
        try:
            subprocess.run(['python', bot_file], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Bot failed: {e}")

    thread = threading.Thread(target=run_bot_process)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'message': 'Bot started successfully',
        'user_id': user_id,
        'bot_file': os.path.basename(bot_file)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
