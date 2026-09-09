import os
import uuid
import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv

from pipeline import run_pipeline
from synthesize import run_synthesize

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "agentic-cinema-secret")

@app.route('/health')
def health():
    return 'ok', 200

# In-memory store for background jobs
# Structure: { job_id: {"status": "running"|"completed"|"error", "memo": {...}, "error": "..."} }
jobs = {}

def background_task(job_id, film_data):
    try:
        print(f"[{job_id}] Starting pipeline...")
        pipeline_data = run_pipeline(film_data)
        print(f"[{job_id}] Pipeline complete. Starting synthesize...")
        memo = run_synthesize(pipeline_data)
        print(f"[{job_id}] Synthesize complete.")
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["memo"] = memo
    except Exception as e:
        print(f"[{job_id}] Error: {e}")
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route('/how-it-works')
def how_it_works():
    return render_template('how-it-works.html')

@app.route("/submit", methods=["POST"])
def submit():
    film_data = {
        "genre": request.form.get("genre") or "psychological thriller",
        "runtime_minutes": int(request.form.get("runtime_minutes") or 92),
        "budget_tier": request.form.get("budget_tier") or "micro-budget (under $500k)",
        "festival_pedigree": request.form.get("festival_pedigree") or "world premiere, no prior festival history"
    }
    
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running"}
    
    # Start the background task
    thread = threading.Thread(target=background_task, args=(job_id, film_data))
    thread.daemon = True
    thread.start()
    
    return jsonify({"job_id": job_id})

@app.route("/status/<job_id>", methods=["GET"])
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify({"status": job["status"]})

@app.route("/results/<job_id>", methods=["GET"])
def results(job_id):
    job = jobs.get(job_id)
    if not job:
        return "Job not found", 404
        
    if job["status"] == "running":
        return "Job is still running. Please wait.", 400
        
    if job["status"] == "error":
        return f"An error occurred: {job.get('error')}", 500
        
    return render_template("results.html", memo=job["memo"])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
