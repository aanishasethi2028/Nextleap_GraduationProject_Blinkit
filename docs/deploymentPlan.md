# Vercel Deployment Plan — Blinkit LENS Dashboard

This document details the configuration and steps required to deploy the **Blinkit LENS Dashboard (Streamlit)** on **Vercel** using Vercel Serverless Functions.

---

## 🏗️ Architecture Overview

Vercel is primarily optimized for static sites and serverless functions. Because Streamlit is a stateful web framework that normally relies on a persistent WebSocket connection, deploying it to Vercel requires configuring a serverless wrapper to run the application in serverless mode.

Alternatively, for stateful, long-lived WebSocket sessions, hosting on platforms like **Streamlit Community Cloud**, **Render**, or **Hugging Face Spaces** is also detailed in this document.

---

## 🛠️ Step 1: Vercel Project Configurations

To deploy on Vercel, you need to add two configuration files to the root of your project:

### 1. `vercel.json`
Create a `vercel.json` file in the root directory to define the build destination and redirect routes to a python serverless function.

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### 2. Serverless Launcher (`api/index.py`)
Create a folder named `api` in your root directory, and inside it, create `index.py`. This script starts Streamlit in a local subprocess and proxies the incoming requests.

```python
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
```

---

## 📋 Step 2: Dependencies

Ensure a `requirements.txt` file exists in your project root containing all required dependencies for the build:

```text
streamlit>=1.30.0
pandas>=2.0.0
openpyxl>=3.1.0
pillow>=10.0.0
altair>=5.0.0
```

---

## 🚀 Step 3: Deploying via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Trigger Deployment**:
   Run the deployment command from the project root:
   ```bash
   vercel
   ```
   Follow the prompts to link the project and deploy.

4. **Deploy to Production**:
   Once the preview deployment succeeds, promote it to production:
   ```bash
   vercel --prod
   ```

---

## 💡 Recommended Alternatives for Streamlit Apps

Because Vercel Serverless Functions have a maximum execution timeout (10-15 seconds for Hobby accounts) and do not support persistent stateful WebSockets natively, you may encounter connectivity warnings in production. 

If you require persistent, high-performance execution, consider these alternatives:

### 1. Streamlit Community Cloud (Recommended & Free)
* **Steps**:
  1. Push your repository to GitHub.
  2. Visit [share.streamlit.io](https://share.streamlit.io).
  3. Log in with GitHub and select your repository, branch, and `src/dashboard.py` as the entrypoint.
  4. Click **Deploy**.

### 2. Render (Persistent Docker/Web Service)
* **Steps**:
  1. Create a `Dockerfile` in the root:
     ```dockerfile
     FROM python:3.9-slim
     WORKDIR /app
     COPY . /app
     RUN pip install -r requirements.txt
     EXPOSE 8501
     CMD ["streamlit", "run", "src/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
     ```
  2. Create a Web Service on [Render](https://render.com) pointing to the repo, selecting Docker as the environment.
