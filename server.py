from flask import Flask, request, jsonify, send_file
import os, subprocess, threading

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
current_process = None

@app.route('/')
def index():
    return send_file('index.html')  # Serve HTML directly

@app.route('/run-bot', methods=['POST'])
def run_bot():
    global current_process
    file = request.files.get('file')
    if not file or not file.filename.endswith('.py'):
        return jsonify({'status': 'error', 'message': 'Only .py files allowed'}), 400
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    if current_process and current_process.poll() is None:
        current_process.terminate()
    def start():
        global current_process
        current_process = subprocess.Popen(['python3', filepath])
    threading.Thread(target=start).start()
    return jsonify({'status': 'success', 'message': 'Bot started!'})

@app.route('/stop-bot', methods=['POST'])
def stop_bot():
    global current_process
    if current_process and current_process.poll() is None:
        current_process.terminate()
        return jsonify({'status': 'success', 'message': 'Bot stopped.'})
    return jsonify({'status': 'info', 'message': 'No bot running.'})