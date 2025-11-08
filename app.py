from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import io
import os
import base64
from werkzeug.utils import secure_filename
app = Flask(__name__)

# In-memory storage for demo (replace with database for real use)
sample_data = []

#-----------------Stuff for Taking CSV input and Storing It----------
UPLOAD_FOLDER = 'Uploaded CSVs'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CSV Upload</title>
    </head>
    <body>
        <h1>Upload CSV File</h1>
        <form method="post" action="/upload" enctype="multipart/form-data">
            <input type="file" id="csvInput" name="csvFile" accept=".csv" required>
            <button type="submit">Upload CSV</button>
        </form>
    </body>
    </html>
'''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'csvFile' not in request.files:
        return 'No file part'
    
    file = request.files['csvFile']
    
    # Check if exists
    if file.filename == '':
        return 'No selected file'
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file first
        file.save(filepath)
        
        # Then check if valid CSV
        try:
            df = pd.read_csv(filepath)
            return f'''
            <h2>File uploaded successfully!</h2>
            <p>Filename: {filename}</p>
            <p>Shape: {df.shape} (rows: {df.shape[0]}, columns: {df.shape[1]})</p>
            <p>Columns: {', '.join(df.columns)}</p>
            <a href="/">Upload another file</a>
            <br><br>
            <a href="/process/{filename}">Process this file</a>
            '''
        except Exception as e:
            return f'Error reading CSV: {str(e)}'
    
    return 'Invalid file type'


#ok after this stuff the file is saved as filename

#----------------------------------------------------------------------

@app.route('/')
def home():
    return redirect('/mrg-schneider-prize')

@app.route('/mrg-schneider-prize')
def dashboard():
    """Main page that displays all the processed data"""
    return render_template('dashboard.html', samples=sample_data)

@app.route('/api/upload', methods=['POST'])
def upload_data():
    """API endpoint that receives data from the processor"""
    try:
        data = request.get_json()
        
        # Add timestamp and store the data
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sample_data.append(data)
        
        print(f"Received data for sample: {data['sample_id']}")
        return jsonify({"status": "success", "message": "Data uploaded successfully"})
    
    except Exception as e:
        print(f"Error processing upload: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/samples')
def get_samples():
    """API endpoint to get all sample data (optional, for JavaScript)"""
    return jsonify(sample_data)

# @app.route('/api/graph')
# def get_graph():
#     return send_file(graph_image_path,mimetype='image/png')

if __name__ == '__main__':
    print("Starting Schneider Prize Demo...")
    print(" Main Webpage: http://localhost:5000/mrg-schneider-prize")
    app.run(host='0.0.0.0', port=5000, debug=True)