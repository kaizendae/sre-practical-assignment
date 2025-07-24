from logging import debug
import os
import json
from flask import Flask, request, render_template_string, redirect, url_for
from google.cloud import storage
from google.oauth2 import service_account

# --- Configuration ---
# Your Google Cloud Storage bucket name
BUCKET_NAME = os.getenv("BUCKET_NAME", "sre-images-bucket")
# Path to your Google Cloud service account key file
CREDENTIALS_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "./credentials.json")

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Google Cloud Storage Client Initialization ---
# Ensure the credentials file exists
if not os.path.exists(CREDENTIALS_FILE):
    print(f"Error: {CREDENTIALS_FILE} not found.")
    print("Please create a service account key file and name it 'credentials.json' in the same directory as this script.")
    print("You can download it from Google Cloud Console -> IAM & Admin -> Service Accounts -> Create Key.")
    exit(1)

try:
    # Load credentials from the JSON file
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE)
    # Initialize the Google Cloud Storage client with the loaded credentials
    storage_client = storage.Client(credentials=credentials)
    print(f"Successfully initialized Google Cloud Storage client with credentials from {CREDENTIALS_FILE}")
except Exception as e:
    print(f"Error initializing Google Cloud Storage client: {e}")
    print("Please ensure your 'credentials.json' file is valid and has the necessary permissions.")
    exit(1)

# Get a reference to the bucket
try:
    bucket = storage_client.get_bucket(BUCKET_NAME)
    print(f"Successfully connected to bucket: {BUCKET_NAME}")
except Exception as e:
    print(f"Error accessing bucket '{BUCKET_NAME}': {e}")
    print("Please ensure the bucket name is correct and the service account has 'Storage Object Admin' or 'Storage Object Creator' permissions.")
    exit(1)

# --- HTML Template for the Web Interface ---
# This template provides a file upload form and lists existing files.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GCS Flask Uploader</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f0f4f8;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .container {
            background-color: #ffffff;
            padding: 2.5rem;
            border-radius: 1rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 28rem;
            text-align: center;
        }
        .file-list {
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid #e2e8f0;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-top: 1.5rem;
            background-color: #f7fafc;
        }
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #edf2f7;
        }
        .file-item:last-child {
            border-bottom: none;
        }
    </style>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen">
    <div class="container bg-white p-10 rounded-xl shadow-lg">
        <h1 class="text-3xl font-bold text-gray-800 mb-6">Upload to GCS Bucket: {{ BUCKET_NAME }}</h1>

        <!-- File Upload Form -->
        <form action="{{ url_for('upload_file') }}" method="post" enctype="multipart/form-data" class="space-y-4">
            <label for="file" class="block text-left text-gray-700 font-medium mb-2">Choose File:</label>
            <input type="file" name="file" id="file" class="block w-full text-sm text-gray-900
                file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100
                cursor-pointer" required>
            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg
                transition duration-300 ease-in-out transform hover:scale-105 shadow-md">
                Upload File
            </button>
        </form>

        <!-- Message Display -->
        {% if message %}
            <p class="mt-4 text-green-600 font-semibold">{{ message }}</p>
        {% elif error %}
            <p class="mt-4 text-red-600 font-semibold">{{ error }}</p>
        {% endif %}

        <!-- List of Uploaded Files -->
        <h2 class="text-2xl font-bold text-gray-800 mt-8 mb-4">Files in Bucket:</h2>
        {% if files %}
            <div class="file-list">
                {% for file in files %}
                    <div class="file-item">
                        <span class="text-gray-700">{{ file }}</span>
                        <a href="https://storage.googleapis.com/{{ BUCKET_NAME }}/{{ file }}" target="_blank" class="text-blue-500 hover:underline text-sm">View</a>
                    </div>
                {% endfor %}
            </div>
        {% else %}
            <p class="text-gray-600">No files found in the bucket.</p>
        {% endif %}
    </div>
</body>
</html>
"""

# --- Flask Routes ---

@app.route('/')
def index():
    """
    Renders the main page with the file upload form and lists existing files in the bucket.
    """
    files_in_bucket = []
    try:
        # List all blobs (files) in the bucket
        blobs = storage_client.list_blobs(BUCKET_NAME)
        for blob in blobs:
            files_in_bucket.append(blob.name)
        message = request.args.get('message')
        error = request.args.get('error')
        return render_template_string(HTML_TEMPLATE, files=files_in_bucket, BUCKET_NAME=BUCKET_NAME, message=message, error=error)
    except Exception as e:
        print(f"Error listing files: {e}")
        return render_template_string(HTML_TEMPLATE, files=[], BUCKET_NAME=BUCKET_NAME, error=f"Error listing files: {e}")

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles file uploads to the Google Cloud Storage bucket.
    """
    if 'file' not in request.files:
        return redirect(url_for('index', error='No file part in the request.'))

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for('index', error='No selected file.'))

    if file:
        try:
            # Create a new blob (file) in the bucket
            blob = bucket.blob(file.filename)
            # Upload the file's content
            blob.upload_from_file(file)
            print(f"File '{file.filename}' uploaded successfully to {BUCKET_NAME}.")
            return redirect(url_for('index', message=f"File '{file.filename}' uploaded successfully!"))
        except Exception as e:
            print(f"Error uploading file: {e}")
            return redirect(url_for('index', error=f"Error uploading file: {e}"))

@app.route('/healthz')
def health_check():
    """
    Health endpoint to test access to the Google Cloud Storage bucket.
    It attempts to list blobs to verify connectivity and permissions.
    """
    try:
        # Attempt to list blobs in the bucket.
        # We only need to iterate over the generator once to confirm access.
        # Using max_results=1 to make it efficient for a health check.
        list(storage_client.list_blobs(BUCKET_NAME, max_results=1))
        return "Bucket access OK", 200
    except Exception as e:
        # If any exception occurs, bucket access failed.
        return f"Bucket access FAILED: {e}", 500

@app.route('/readyz')
def readyz_check():
    """
    Readiness endpoint to indicate if the application is ready to serve traffic.
    It performs the same check as the health endpoint to verify bucket access.
    """
    try:
        # Attempt to list blobs in the bucket to verify readiness.
        list(storage_client.list_blobs(BUCKET_NAME, max_results=1))
        return "Application READY", 200
    except Exception as e:
        return f"Application NOT READY: {e}", 503 # Use 503 Service Unavailable for readiness probe failure


# --- Run the Flask App ---
if __name__ == '__main__':
    # Flask will run on http://127.0.0.1:5000/ by default
    flask_debug = os.getenv("FLASK_DEBUG", "false").lower() in ["1", "true", "yes"]
    app.run(host="0.0.0.0", debug=flask_debug, port=8080) # debug mode controlled by FLASK_DEBUG env var
