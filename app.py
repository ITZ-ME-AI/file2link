from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from imagekitio import ImageKit
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
            response = requests.get('https://file2link-3pse.onrender.com')
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

# Initialize ImageKit
imagekit = ImageKit(
    private_key='private_2K+1aGgq4ATkxUq5B6w8NRq8lL0=',
    public_key='public_J2LWdBYDTxY8z0l3fKPMMq7lfak=',
    url_endpoint='https://ik.imagekit.io/veltrixvision'
)

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

    try:
        # Generate a unique filename
        original_filename = file.filename
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # Upload to ImageKit
        upload_response = imagekit.upload(
            file=file,
            file_name=unique_filename,
            options={
                "folder": "/veltrixvision",
                "use_unique_file_name": True,
                "tags": ["file2link", "veltrixvision"]
            }
        )

        return jsonify({
            'success': True,
            'access_url': upload_response['url'],
            'original_filename': original_filename,
            'unique_filename': unique_filename,
            'metadata': {
                'uploaded_at': datetime.now().isoformat(),
                'tags': upload_response.get('tags', [])
            }
        })

    except Exception as e:
        return jsonify({'error': str(e), 'progress': 0}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
