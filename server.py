from flask import Flask, request, jsonify, send_file
import os, subprocess, threading

app = Flask(__name__)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Track user processes
user_data = {}  # {user_id: {"file": path, "process": subprocess}}

@app.route('/')
def home():
    return send_file("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    user_id = request.remote_addr.replace(".", "_")  # fallback ID if Telegram ID not available
    file = request.files.get("file")
    if not file or not file.filename.endswith(".py"):
        return jsonify({"status": "error", "message": "Upload a .py file only"}), 400

    # Create user folder
    user_folder = os.path.join(UPLOAD_DIR, f"user_{user_id}")
    os.makedirs(user_folder, exist_ok=True)

    filepath = os.path.join(user_folder, "bot.py")
    file.save(filepath)

    # Store in user_data
    user_data[user_id] = {"file": filepath, "process": None}

    return jsonify({"status": "success", "message": "File uploaded!"})

@app.route('/start', methods=['POST'])
def start():
    user_id = request.remote_addr.replace(".", "_")
    user = user_data.get(user_id)

    if not user or not os.path.exists(user["file"]):
        return jsonify({"status": "error", "message": "No uploaded bot for this user."})

    if user["process"] and user["process"].poll() is None:
        return jsonify({"status": "error", "message": "Bot already running."})

    def run_bot():
        user["process"] = subprocess.Popen(['python3', user["file"]])

    threading.Thread(target=run_bot).start()
    return jsonify({"status": "started"})

@app.route('/stop', methods=['POST'])
def stop():
    user_id = request.remote_addr.replace(".", "_")
    user = user_data.get(user_id)

    if user and user["process"] and user["process"].poll() is None:
        user["process"].terminate()
        return jsonify({"status": "stopped"})
    return jsonify({"status": "not_running"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
