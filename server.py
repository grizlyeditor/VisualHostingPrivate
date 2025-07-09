from flask import Flask, request, render_template, redirect
import subprocess, os

app = Flask(__name__)

LOG_PATH = "logs/bot.log"
UPLOAD_PATH = "uploaded_bot.py"

# ✅ Ensure logs folder and log file exist
os.makedirs("logs", exist_ok=True)
if not os.path.exists(LOG_PATH):
    with open(LOG_PATH, "w"): pass  # create empty log file

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("botfile")
        if file and file.filename.endswith(".py"):
            file.save(UPLOAD_PATH)
            return redirect("/")
    with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
        log_data = f.read()
    return render_template("index.html", log_data=log_data)

@app.route("/start", methods=["POST"])
def start():
    if os.path.exists(UPLOAD_PATH):
        with open(LOG_PATH, "w"): pass  # clear old log
        subprocess.Popen(
            ["bash", "-c", "while true; do python3 uploaded_bot.py; sleep 2; done"],
            stdout=open(LOG_PATH, "a"),
            stderr=subprocess.STDOUT
        )
    return redirect("/")

@app.route("/log")
def log():
    with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
