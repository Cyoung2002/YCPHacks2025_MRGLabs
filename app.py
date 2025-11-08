from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# In-memory storage for demo (replace with database for real use)
sample_data = []

# Test data to display something on the page
sample_data.append({
    'sample_id': '12345',
    'standard_rgb': [120, 80, 200],
    'test_rgb': [200, 150, 50],
    'image_filename': 'test.png',
    'timestamp': '2024-01-20 14:30:00'
})

@app.route('/')
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)