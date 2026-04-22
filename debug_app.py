import subprocess
import time
import requests

print("Starting Flask app in background...")
proc = subprocess.Popen(["python", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=r"c:\Users\AKASH YADAV\Documents\antigravity_website")
time.sleep(3) # Wait for it to start

# Check if it crashed
if proc.poll() is not None:
    stdout, stderr = proc.communicate()
    print("CRASHED!")
    print("STDOUT:", stdout.decode())
    print("STDERR:", stderr.decode())
else:
    print("App is running. Testing /register route...")
    data = {
        'student_id': 'TEST001',
        'name': 'Test User',
        'email': 'test@example.com',
        'department': 'CS',
        'category': 'Academic',
        'title': 'Test Subject',
        'description': 'Test Description',
        'priority': 'Low'
    }
    try:
        response = requests.post("http://127.0.0.1:5000/register", data=data)
        print("Response Code:", response.status_code)
        print("Response Body:", response.text)
    except Exception as e:
        print("Request failed:", e)
        
    proc.terminate()
