from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import internetarchive as ia
import os
from datetime import datetime
import uuid
import threading
import time
import requests
import json

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "X-CSRFToken"],
        "supports_credentials": True,
        "max_age": 600
    }
})

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def ping_file2link():
    """Ping the file2link service every 10 seconds"""
    while True:
        try:
            response = requests.get('https://file2link-ol4p.onrender.com')
            if response.status_code == 200:
                print(f"[{datetime.now()}] Successfully pinged file2link service")
            else:
                print(f"[{datetime.now()}] Failed to ping file2link service: {response.status_code}")
        except Exception as e:
            print(f"[{datetime.now()}] Error pinging file2link service: {str(e)}")
        time.sleep(10)

# Start the pinging thread
ping_thread = threading.Thread(target=ping_file2link, daemon=True)
ping_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    if request.method == 'OPTIONS':
        return '', 200
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        # Use shop_proj as the identifier
        item_id = 'shop_proj'
        
        try:
            # Generate a unique filename
            original_filename = file.filename
            file_extension = os.path.splitext(original_filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Prepare metadata
            metadata = {
                'title': f'File2Link Upload - {original_filename}',
                'mediatype': 'data',
                'collection': 'opensource',
                'description': f'Original filename: {original_filename}',
                'creator': 'File2Link Uploader',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'licenseurl': 'https://creativecommons.org/licenses/by/4.0/',
                'subject': ['file2link', 'file sharing'],
                'original_filename': original_filename
            }

            def generate_progress():
                total_size = 0
                uploaded_size = 0
                
                # Get file size
                file.seek(0, os.SEEK_END)
                total_size = file.tell()
                file.seek(0)
                
                # Upload the file with metadata
                r = ia.upload(
                    item_id,
                    files={unique_filename: file},
                    metadata=metadata,
                    access_key='PrJnoIKjNt4ul1Fr',
                    secret_key='S0tCXWb7fM43m44Y'
                )
                
                if r[0].status_code == 200:
                    # Get the access URL with the correct format
                    access_url = f'https://archive.org/download/{item_id}/{unique_filename}'
                    
                    return json.dumps({
                        'success': True,
                        'access_url': access_url,
                        'item_id': item_id,
                        'original_filename': original_filename,
                        'unique_filename': unique_filename,
                        'metadata': metadata
                    })
                else:
                    return json.dumps({'error': 'Upload failed'})

            return Response(generate_progress(), mimetype='application/json')
            
        except Exception as e:
            return jsonify({'error': str(e), 'progress': 0}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 
