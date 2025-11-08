import os
import io
import zipfile
from flask import Flask, request, jsonify, send_from_directory, render_template
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
GRAPH_FOLDER = os.path.join("static", "graphs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GRAPH_FOLDER, exist_ok=True)

state = {"baseline": None, "samples": []}


# =========================
#  HELPER: generate_plot()
# =========================
def generate_plot(baseline_path, sample_path, output_path):
    """Generate and save a plot comparing baseline vs sample."""
    base = pd.read_csv(baseline_path, skiprows=1)
    sample = pd.read_csv(sample_path, skiprows=1)

    base_label = os.path.splitext(os.path.basename(baseline_path))[0]
    sample_label = os.path.splitext(os.path.basename(sample_path))[0]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(base["cm-1"], base["A"], label=base_label, linewidth=1)
    ax.plot(sample["cm-1"], sample["A"], label=sample_label, linewidth=1)

    plt.xlabel("cm-1")
    plt.ylabel("A")

    plt.legend(
        loc="lower left",
        bbox_to_anchor=(0, -0.1),
        borderaxespad=0,
        frameon=False
    )

    fig.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Created plot: {output_path}")


# =========================
#  ROUTE: upload files
# =========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_files():
    baseline = request.files.get("baseline")
    samples = request.files.getlist("samples")

    # Handle baseline upload
    if baseline and baseline.filename:
        baseline_path = os.path.join(UPLOAD_FOLDER, "baseline", baseline.filename)
        os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
        baseline.save(baseline_path)
        state["baseline"] = baseline_path
        print(f"✅ Baseline uploaded: {baseline.filename}")

        # Re-generate graphs for existing samples if any
        if "samples" in state and state["samples"]:
            for s in state["samples"]:
                graph_filename = f"{os.path.splitext(os.path.basename(s['path']))[0]}.png"
                graph_path = os.path.join(GRAPH_FOLDER, graph_filename)
                try:
                    generate_plot(baseline_path, s["path"], graph_path)
                    s["graph"] = f"/static/graphs/{graph_filename}"
                except Exception as e:
                    print(f"⚠️ Error plotting {s['filename']}: {e}")

    # Handle sample uploads
    if samples:
        for s in samples:
            if not s.filename:
                continue
            sample_path = os.path.join(UPLOAD_FOLDER, "samples", s.filename)
            os.makedirs(os.path.dirname(sample_path), exist_ok=True)
            s.save(sample_path)

            graph_filename = f"{os.path.splitext(s.filename)[0]}.png"
            graph_path = os.path.join(GRAPH_FOLDER, graph_filename)

            # Only generate graph if baseline exists
            if "baseline" in state and state["baseline"]:
                try:
                    generate_plot(state["baseline"], sample_path, graph_path)
                except Exception as e:
                    print(f"⚠️ Error plotting {s.filename}: {e}")

            # Add to state
            state.setdefault("samples", []).append({
                "filename": s.filename,
                "path": sample_path,
                "graph": f"/static/graphs/{graph_filename}"
            })

    return jsonify({
        "message": "Files uploaded and processed successfully",
        "samples": state.get("samples", [])
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
