from flask import Flask, render_template, request, jsonify, redirect, g
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import io
import os
import base64
import sqlite3
import uuid
from werkzeug.utils import secure_filename
from io import BytesIO
import base64

# Global state for loaded data
baseline_file = None
sample_batch = []

app = Flask(__name__)

sample_data = []

#-----------------Database Setup for CSV Files----------
UPLOAD_FOLDER = 'Uploaded CSVs'
ALLOWED_EXTENSIONS = {'csv'}
DATABASE = 'file_registry.db'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max
app.config['DATABASE'] = DATABASE
selected_graph_files = set()
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database setup functions
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT UNIQUE NOT NULL,
                original_name TEXT NOT NULL,
                saved_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                upload_time TIMESTAMP NOT NULL,
                rows INTEGER,
                columns INTEGER,
                column_names TEXT
            )
        ''')
        db.commit()

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.teardown_appcontext
def teardown_db(e=None):
    close_db(e)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database on startup
with app.app_context():
    init_db()

#-----------------CSV Upload Routes----------
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CSV Upload</title>
        <style>
            .file-list { margin: 20px 0; }
            .file-item { 
                border: 1px solid #ddd; 
                padding: 10px; 
                margin: 5px 0; 
                border-radius: 5px;
            }
            .nav-links { margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>Upload CSV File</h1>
        <form method="post" action="/upload" enctype="multipart/form-data">
            <input type="file" id="csvInput" name="csvFile" accept=".csv" multiple required>
            <button type="submit">Upload CSV</button>
        </form>
        
        <div class="nav-links">
            <a href="/mrg-schneider-prize">Go to MRG Schneider Prize Dashboard</a>
        </div>

        <div class="file-list">
            <h3>Previously Uploaded Files:</h3>
            <div id="fileList">
                <!-- Files will be loaded via JavaScript -->
            </div>
        </div>

        <script>
            // Load files on page load
            fetch('/files')
                .then(response => response.text())
                .then(html => {
                    document.getElementById('fileList').innerHTML = html;
                });
        </script>
    </body>
    </html>
'''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'csvFile' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
    
    uploaded_files = request.files.getlist('csvFile')
    
    if not uploaded_files or all(file.filename == '' for file in uploaded_files):
        return jsonify({'success': False, 'message': 'No files selected'}), 400
    
    success_count = 0
    error_files = []
    
    for file_obj in uploaded_files:
        if file_obj.filename == '':
            continue
            
        if file_obj and allowed_file(file_obj.filename):
            try:
                file_id = str(uuid.uuid4())[:8]
                original_filename = secure_filename(file_obj.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
                
                # Save the file 
                file_obj.save(filepath)
                
                # Read CSV and store in database
                df = pd.read_csv(filepath)
                
                db = get_db()
                db.execute('''
                    INSERT INTO files 
                    (file_id, original_name, saved_filename, file_path, upload_time, rows, columns, column_names)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_id,
                    file_obj.filename,
                    original_filename,
                    filepath,
                    datetime.now(),
                    df.shape[0],
                    df.shape[1],
                    ','.join(df.columns.tolist())
                ))
                db.commit()
                
                success_count += 1
                
            except Exception as e:
                error_files.append(f"{file_obj.filename}: {str(e)}")
                # Clean up failed file
                if os.path.exists(filepath):
                    os.remove(filepath)
    
    if success_count == 0:
        return jsonify({
            'success': False, 
            'message': f'No files uploaded. Errors: {"; ".join(error_files)}'
        }), 400
    
    return jsonify({
        'success': True,
        'message': f'Successfully uploaded {success_count} file(s)',
        'count': success_count
    })

@app.route('/files')
def list_files():
    db = get_db()
    files = db.execute('''
        SELECT * FROM files ORDER BY upload_time DESC
    ''').fetchall()
    
    if not files:
        return '<p>No files uploaded yet</p>'
    
    files_html = ''
    for file in files:
        files_html += f'''
        <div class="file-item">
            <strong>{file['original_name']}</strong> (ID: {file['file_id']})<br>
            <small>
                Uploaded: {file['upload_time']} | 
                Size: {file['rows']} × {file['columns']} | 
                Columns: {file['column_names']}
            </small><br>
            <a href="/process/{file['file_id']}">Process</a> | 
            <a href="/download/{file['file_id']}">Download</a> | 
            <a href="/delete/{file['file_id']}">Delete</a>
        </div>
        '''
    return files_html

@app.route('/process/<file_id>')
def process_file(file_id):
    db = get_db()
    file_record = db.execute(
        'SELECT * FROM files WHERE file_id = ?', (file_id,)
    ).fetchone()
    
    if not file_record:
        return 'File not found', 404
    
    try:
        df = pd.read_csv(file_record['file_path'])
        return f'''
        <h2>Processing: {file_record['original_name']}</h2>
        <p>File loaded from database registry!</p>
        <h3>Preview:</h3>
        <div style="max-height: 400px; overflow: auto;">
            {df.head(10).to_html(classes='table table-striped', index=False)}
        </div>
        <div style="margin-top: 20px;">
            <a href="/">Back to upload</a> | 
            <a href="/files">View all files</a> |
            <a href="/mrg-schneider-prize">Go to Dashboard</a>
        </div>
        '''
    except Exception as e:
        return f'Error processing file: {str(e)}', 500

@app.route('/delete/<file_id>')
def delete_file(file_id):
    db = get_db()
    file_record = db.execute(
        'SELECT * FROM files WHERE file_id = ?', (file_id,)
    ).fetchone()
    
    if not file_record:
        return 'File not found', 404
    
    try:
        # Delete physical file
        if os.path.exists(file_record['file_path']):
            os.remove(file_record['file_path'])
        
        # Delete database record
        db.execute('DELETE FROM files WHERE file_id = ?', (file_id,))
        db.commit()
        
        # Also remove from selected files if it was selected
        if file_id in selected_graph_files:
            selected_graph_files.remove(file_id)
        
        return f'File {file_id} deleted successfully'
    except Exception as e:
        return f'Error deleting file: {str(e)}', 500

# Download endpoint
@app.route('/download/<file_id>')
def download_file(file_id):
    db = get_db()
    file_record = db.execute(
        'SELECT * FROM files WHERE file_id = ?', (file_id,)
    ).fetchone()
    
    if not file_record:
        return 'File not found', 404
    
    try:
        from flask import send_file
        return send_file(file_record['file_path'], as_attachment=True, download_name=file_record['original_name'])
    except Exception as e:
        return f'Error downloading file: {str(e)}', 500

#----------------------------------------------------------------------

#----------------- File Selection Routes for Graphing ----------------
@app.route('/select-file/<file_id>', methods=['POST'])
def select_file(file_id):
    """Add a file to the graph selection"""
    try:
        # Verify file exists
        db = get_db()
        file_record = db.execute(
            'SELECT * FROM files WHERE file_id = ?', (file_id,)
        ).fetchone()
        
        if not file_record:
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        selected_graph_files.add(file_record)
        
        return jsonify({
            'success': True, 
            'message': f"File '{file_record['original_name']}' added to graph selection",
            'selected_count': len(selected_graph_files)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/deselect-file/<file_id>', methods=['POST'])
def deselect_file(file_id):
    """Remove a file from the graph selection"""
    try:
        if file_id in selected_graph_files:
            selected_graph_files.remove(file_id)
            
        return jsonify({
            'success': True, 
            'message': 'File removed from graph selection',
            'selected_count': len(selected_graph_files)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/clear-selection', methods=['POST'])
def clear_selection():
    """Clear all files from graph selection"""
    try:
        selected_graph_files.clear()
        return jsonify({
            'success': True, 
            'message': 'All files cleared from graph selection'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/get-selected-files')
def get_selected_files():
    """Get all currently selected files for graphing"""
    try:
        db = get_db()
        selected_files_data = []
        
        for file_id in selected_graph_files:
            file_record = db.execute(
                'SELECT * FROM files WHERE file_id = ?', (file_id,)
            ).fetchone()
            
            if file_record:
                selected_files_data.append({
                    'file_id': file_record['file_id'],
                    'original_name': file_record['original_name'],
                    'upload_time': file_record['upload_time'],
                    'rows': file_record['rows'],
                    'columns': file_record['columns'],
                    'column_names': file_record['column_names']
                })
        
        return jsonify({
            'selected_files': selected_files_data,
            'count': len(selected_files_data)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/generate-graph', methods=['POST'])
def generate_graph():
    """Generate graph from selected files"""
    try:
        if not selected_graph_files:
            return jsonify({'success': False, 'message': 'No files selected for graphing'})
        
        db = get_db()
        selected_files_data = []
        
        # Get detailed information for selected files
        for file_id in selected_graph_files:
            file_record = db.execute(
                'SELECT * FROM files WHERE file_id = ?', (file_id,)
            ).fetchone()
            
            if file_record:
                selected_files_data.append({
                    'file_id': file_record['file_id'],
                    'original_name': file_record['original_name'],
                    'rows': file_record['rows'],
                    'columns': file_record['columns'],
                    'column_names': file_record['column_names'].split(',') if file_record['column_names'] else []
                })
        
        # Your actual graph generation logic would go here
        graph_html = f'''
        <div style="width: 100%; text-align: center;">
            <h3> Graph Analysis</h3>
            <p>Generated from {len(selected_files_data)} selected file(s)</p>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0;">
        '''
        
        for file_info in selected_files_data:
            graph_html += f'''
                <div style="border: 2px solid #007bff; padding: 15px; border-radius: 8px; background: #f0f8ff;">
                    <strong>📄 {file_info["original_name"]}</strong><br>
                    <small>ID: {file_info["file_id"]}</small><br>
                    <small>Size: {file_info["rows"]} × {file_info["columns"]}</small><br>
                    <small>Columns: {", ".join(file_info["column_names"][:3])}{"..." if len(file_info["column_names"]) > 3 else ""}</small>
                </div>
            '''
        
        graph_html += '''
            </div>
            
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 10px; margin-top: 20px;">
                <h4>Graph Visualization Area</h4>
                <p><em>Your actual graph would be generated here</em></p>
                <p>Selected files are stored separately in Flask memory</p>
                <div style="margin-top: 20px;">
                    <button class="process-btn" style="background: white; color: #667eea; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;" onclick="alert('Export functionality would be implemented here')">
                        Export Graph
                    </button>
                </div>
            </div>
        </div>
        '''
        
        return jsonify({
            'success': True,
            'message': f'Graph generated from {len(selected_files_data)} files',
            'html': graph_html,
            'selected_files': selected_files_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating graph: {str(e)}'})

#----------------- MRG Schneider Prize Routes----------
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

@app.route('/files-data')
def files_data():
    """API endpoint to get files as JSON for the file browser"""
    db = get_db()
    files = db.execute('''
        SELECT * FROM files ORDER BY upload_time DESC
    ''').fetchall()
    
    files_list = []
    for file in files:
        files_list.append({
            'file_id': file['file_id'],
            'original_name': file['original_name'],
            'upload_time': file['upload_time'],
            'rows': file['rows'],
            'columns': file['columns'],
            'column_names': file['column_names']
        })
    
    return jsonify(files_list)

@app.route('/file-preview/<file_id>')
def file_preview(file_id):
    """API endpoint to get file preview data"""
    db = get_db()
    file_record = db.execute(
        'SELECT * FROM files WHERE file_id = ?', (file_id,)
    ).fetchone()
    
    if not file_record:
        return '<div style="text-align: center; color: #dc3545;">File not found</div>'
    
    try:
        df = pd.read_csv(file_record['file_path'])
        # Return first 10 rows as HTML table
        return df.head(10).to_html(classes='preview-table', index=False, escape=False)
    except Exception as e:
        return f'<div style="text-align: center; color: #dc3545;">Error loading preview: {str(e)}</div>'

@app.route('/delete-all', methods=['POST'])
def delete_all_files():
    """Delete all files from the database and file system"""
    try:
        db = get_db()
        
        # Get all file records
        files = db.execute('SELECT * FROM files').fetchall()
        
        deleted_count = 0
        errors = []
        
        # Delete physical files
        for file_record in files:
            try:
                if os.path.exists(file_record['file_path']):
                    os.remove(file_record['file_path'])
                deleted_count += 1
            except Exception as e:
                errors.append(f"{file_record['original_name']}: {str(e)}")
        
        # Delete all database records
        db.execute('DELETE FROM files')
        db.commit()
        
        # Clear the selected files set since all files are deleted
        selected_graph_files.clear()
        
        if errors:
            return f'Deleted {deleted_count} files, but encountered errors: {"; ".join(errors)}', 500
        
        return f'Successfully deleted all {deleted_count} files'
        
    except Exception as e:
        return f'Error deleting all files: {str(e)}', 500

if __name__ == '__main__':
    print("Starting Schneider Prize Demo...")
    print("CSV Upload Page: http://localhost:5000/")
    print("Main Webpage: http://localhost:5000/mrg-schneider-prize")
    app.run(host='0.0.0.0', port=5000, debug=True)



@app.route('/get-filename/<file_id>')
def get_filename(file_id):
    """Get the original filename for a specific file_id"""
    try:
        db = get_db()
        file_record = db.execute(
            'SELECT original_name FROM files WHERE file_id = ?', (file_id,)
        ).fetchone()
        
        if not file_record:
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'original_name': file_record['original_name']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500