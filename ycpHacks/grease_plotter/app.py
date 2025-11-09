import os
import io
import zipfile
from flask import Flask, request, jsonify, send_from_directory, render_template
import pandas as pd
import matplotlib

from utils.plotting import generate_plot

matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
GRAPH_FOLDER = os.path.join("static", "graphs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GRAPH_FOLDER, exist_ok=True)

state = {"baseline": None, "samples": []}


# =========================
#  ROUTE: upload files
# =========================
@app.route("/")
def home():
    return render_template("index.html")

import shutil

@app.route("/upload", methods=["POST"])
def upload_files():
    baseline_file = request.files.get("baseline")
    sample_files = request.files.getlist("samples")

    # --- Step 1: Clear all folders ---
    for folder in [os.path.join(UPLOAD_FOLDER, "baseline"),
                   os.path.join(UPLOAD_FOLDER, "samples"),
                   GRAPH_FOLDER]:
        if os.path.exists(folder):
            for f in os.listdir(folder):
                path = os.path.join(folder, f)
                if os.path.isfile(path):
                    os.remove(path)

    # --- Step 2: Update current baseline if a new file is selected ---
    if baseline_file and baseline_file.filename:
        baseline_path = os.path.join(UPLOAD_FOLDER, "baseline", baseline_file.filename)
        os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
        baseline_file.save(baseline_path)
        state["baseline"] = baseline_path  # store current baseline
    elif "baseline" in state:
        # reuse existing baseline file
        baseline_path = state["baseline"]
        # Copy the existing baseline into the cleared folder
        os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
        # make sure the file is still in baseline folder
        import shutil
        shutil.copy(state["baseline"], baseline_path)
    else:
        return jsonify({"error": "No baseline selected"}), 400

    # --- Step 3: Update current samples if new files are selected ---
    state["samples"] = []
    if sample_files:
        for s in sample_files:
            if not s.filename:
                continue
            sample_path = os.path.join(UPLOAD_FOLDER, "samples", s.filename)
            os.makedirs(os.path.dirname(sample_path), exist_ok=True)
            s.save(sample_path)
            state["samples"].append({"filename": s.filename, "path": sample_path})
    elif state.get("samples"):
        # Copy old samples into cleared folder
        import shutil
        for s in state["samples"]:
            src_path = s["path"]
            dst_path = os.path.join(UPLOAD_FOLDER, "samples", os.path.basename(src_path))
            shutil.copy(src_path, dst_path)
            s["path"] = dst_path
    else:
        return jsonify({"error": "No samples available"}), 400

    # --- Step 4: Regenerate all graphs ---
    for s in state["samples"]:
        graph_filename = f"{os.path.splitext(s['filename'])[0]}.png"
        graph_path = os.path.join(GRAPH_FOLDER, graph_filename)
        try:
            generate_plot(baseline_path, s["path"], graph_path)
        except Exception as e:
            print(f"⚠️ Error plotting {s['filename']}: {e}")
        s["graph"] = f"/static/graphs/{graph_filename}"

    return jsonify({
        "message": "Upload and process completed",
        "samples": state["samples"]
    })


# =========================
#  ROUTE: get list of samples
# =========================
@app.route("/get_samples")
def get_samples():
    return jsonify(state.get("samples", []))


# =========================
#  ROUTE: preview sample graph
# =========================
@app.route("/preview/<filename>")
def preview(filename):
    sample = next((s for s in state["samples"] if s["filename"] == filename), None)
    if not sample:
        return jsonify({"error": "Sample not found"}), 404
    return jsonify({"graph": sample["graph"]})


# =========================
#  ROUTE: export all as zip
# =========================
@app.route("/export_all", methods=["POST"])
def export_all():
    zip_filename = "graphs.zip"
    zip_path = os.path.join(GRAPH_FOLDER, zip_filename)
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for s in state["samples"]:
            graph_path = os.path.join("static", "graphs", f"{os.path.splitext(s['filename'])[0]}.png")
            if os.path.exists(graph_path):
                zipf.write(graph_path, os.path.basename(graph_path))
    return send_from_directory(GRAPH_FOLDER, zip_filename, as_attachment=True)


# =========================
#  MAIN ENTRY POINT
# =========================
if __name__ == "__main__":
    app.run(debug=True)
