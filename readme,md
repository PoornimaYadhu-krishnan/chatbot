# Django and React Integration Guide

## Django Installation

### 1. Install Django
```bash
mkdir django-react-project
cd django-react-project
python -m venv env
env\Scripts\activate
pip install django djangorestframework
```

### 2. Start a Django Project
```bash
django-admin startproject myproject .
cd myproject
```

### 3. Open the Project in an IDE
Open the folder in VS Code or any IDE. You'll see a new project named `myproject` with files like `settings.py` and `urls.py`.

### 4. Run the Django Server
```bash
python manage.py runserver
```

### 5. Test the Setup
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser to see the default Django welcome page.

---

## Create Backend App

### 1. Create a New App
```bash
python manage.py startapp logapi
```
A new folder `logapi` will be created with files including `urls.py` and `views.py`.

### 2. Add the App to `INSTALLED_APPS`
In `myproject/settings.py`, add `logapi` and `rest_framework` to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # Other apps
    'rest_framework',
    'logapi',
]
```

### 3. Add Logic to the App
Create a file `logapi/utils.py` and add your log analysis function:
```python
import openai

openai.api_key = "your_azure_openai_api_key"

def analyze_log(log_file_content):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Analyze the following log for exceptions and root causes:\n{log_file_content}",
            max_tokens=500
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return str(e)
```

### 4. Create an API Endpoint
In `logapi/views.py`, create a view to expose your logic:
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import analyze_log

@api_view(['POST'])
def analyze_log_view(request):
    log_file = request.data.get('log_file', '')
    if not log_file:
        return Response({'error': 'Log file content is required'}, status=400)

    analysis = analyze_log(log_file)
    return Response({'analysis': analysis})
```

### 5. Define a URL for the Endpoint
In `logapi/urls.py`, add the route for the API:
```python
from django.urls import path
from .views import analyze_log_view

urlpatterns = [
    path('analyze-log/', analyze_log_view, name='analyze-log'),
]
```

### 6. Include App URLs in the Project
In `myproject/urls.py`, include the `logapi` URLs:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('logapi.urls')),
]
```

### 7. Test the API
Run the server and test the endpoint using Postman or cURL:
```bash
python manage.py runserver
```
**cURL Command:**
```bash
curl -X POST http://127.0.0.1:8000/api/analyze-log/ \
-H "Content-Type: application/json" \
-d '{"log_file": "Your log file content here"}'
```

---

## ReactJS Setup

### 1. Install Node.js and NPM
Download and install [Node.js](https://nodejs.org/).

### 2. Set Up React App
```bash
npx create-react-app react-frontend
cd react-frontend
```

### 3. Open the Project in an IDE
Open the `react-frontend` folder in VS Code or any IDE.

### 4. Test the Installation
```bash
npm start
```

### 5. Install Axios
Stop the server and install Axios:
```bash
npm install axios
```

---

## React App

### 1. Update `src/App.js`
Replace the content of `src/App.js` with:
```javascript
import React, { useState } from "react";

const App = () => {
    const [logFile, setLogFile] = useState("");
    const [analysis, setAnalysis] = useState("");

    const handleAnalyze = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/api/analyze-log/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ log_file: logFile }),
            });

            const data = await response.json();
            if (response.ok) {
                setAnalysis(data.analysis);
            } else {
                alert(data.error || "Error analyzing log file.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Failed to analyze log file.");
        }
    };

    return (
        <div>
            <textarea
                value={logFile}
                onChange={(e) => setLogFile(e.target.value)}
                placeholder="Paste your log file content here"
            />
            <button onClick={handleAnalyze}>Analyze</button>
            {analysis && <pre>{analysis}</pre>}
        </div>
    );
};

export default App;
```

### 2. Save the File

---

## Configure CORS in Django

### 1. Install `django-cors-headers`
```bash
pip install django-cors-headers
```

### 2. Modify `myproject/settings.py`
Add `corsheaders` to `INSTALLED_APPS` and middleware, and define allowed origins:
```python
INSTALLED_APPS = [
    # Existing apps
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # Other middlewares
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

---

## Run the Application
1. Start the Django server:
   ```bash
   python manage.py runserver
   ```
2. Start the React server:
   ```bash
   npm start
   ```
3. Open [http://localhost:3000](http://localhost:3000) to access the application.
