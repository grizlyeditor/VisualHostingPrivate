from flask import Flask, request, render_template, redirect
import subprocess, os

app = Flask(__name__)
LOG_PATH = "logs/bot.log"
UPLOAD_PATH = "uploaded_bot.py"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["botfile"]
        if file and file.filename.endswith(".py"):
            file.save(UPLOAD_PATH)
            return redirect("/")
    with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
        log_data = f.read()
    return render_template("index.html", log_data=log_data)

@app.route("/start", methods=["POST"])
def start():
    if os.path.exists(UPLOAD_PATH):
        with open(LOG_PATH, "w"): pass  # clear log
        subprocess.Popen(
            ["python3", UPLOAD_PATH],
            stdout=open(LOG_PATH, "a"),
            stderr=subprocess.STDOUT
        )
    return redirect("/")

@app.route("/log")
def log():
    with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
