import os
import sys
import subprocess

# Add project root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def handler(request):
    # Command to run Streamlit in headless serverless mode
    cmd = [
        "streamlit",
        "run",
        "src/dashboard.py",
        "--server.headless",
        "true",
        "--server.port",
        "8501"
    ]
    
    # Run Streamlit as a subprocess
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": "Streamlit server initialized. Access via proxy."
    }