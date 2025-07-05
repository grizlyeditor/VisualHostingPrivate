from flask import Flask, request, jsonify, send_file
import os, subprocess, threading

app = Flask(__name__)
uploaded_file = None
bot_process = None

@app.route('/')
def home():
    return send_file("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    global uploaded_file
    file = request.files.get("file")
    if not file or not file.filename.endswith(".py"):
        return jsonify({"status": "error", "message": "Only .py files allowed"})
    uploaded_file = file.filename
    file.save(uploaded_file)
    return jsonify({"status": "success"})

@app.route('/start', methods=['POST'])
def start():
    global uploaded_file, bot_process
    if not uploaded_file or not os.path.exists(uploaded_file):
        return jsonify({"status": "error", "message": "File not found"})
    if bot_process and bot_process.poll() is None:
        return jsonify({"status": "error", "message": "Already running"})

    def run():
        global bot_process
        bot_process = subprocess.Popen(['python3', uploaded_file])
    threading.Thread(target=run).start()
    return jsonify({"status": "started"})

@app.route('/stop', methods=['POST'])
def stop():
    global bot_process
    if bot_process and bot_process.poll() is None:
        bot_process.terminate()
        return jsonify({"status": "stopped"})
    return jsonify({"status": "not_running"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
