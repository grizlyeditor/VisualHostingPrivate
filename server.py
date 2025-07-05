from flask import Flask, request, jsonify, send_file
import os, subprocess, threading

app = Flask(__name__)
bot_file = None
bot_process = None

@app.route('/')
def home():
    return send_file("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    global bot_file
    file = request.files.get("file")
    if not file or not file.filename.endswith(".py"):
        return jsonify({"status": "error", "message": "Invalid file"}), 400
    bot_file = file.filename
    file.save(bot_file)
    return jsonify({"status": "success"})

@app.route('/start', methods=['POST'])
def start():
    global bot_file, bot_process
    if not bot_file or not os.path.exists(bot_file):
        return jsonify({"status": "error", "message": "File missing"})
    if bot_process and bot_process.poll() is None:
        bot_process.terminate()
    def run():
        global bot_process
        bot_process = subprocess.Popen(['python3', bot_file])
    threading.Thread(target=run).start()
    return jsonify({"status": "started"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
