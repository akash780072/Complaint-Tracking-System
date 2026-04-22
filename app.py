from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import os
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'super_secret_key_2025'
DB_PATH = 'complaints.db'

# --- EMAIL CONFIGURATION ---
SMTP_SERVER = 'smtp.gmail.com' # Changing this below if needed, but Veltech might use Google.
# If Veltech uses Outlook, you might need to change it to 'smtp.office365.com'. Let's try Google first.
SMTP_SERVER = 'smtp.gmail.com' # If Veltech uses Outlook, change to 'smtp.office365.com'
SMTP_PORT = 587
SENDER_EMAIL = 'akashyadav04622@gmail.com'
# IMPORTANT: Replace 'YOUR_APP_PASSWORD' with your actual generated App Password.
# Do NOT use your normal email password.
SENDER_PASSWORD = 'zmlr lcii gphv ydfw' 

def send_email_async(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = f"Alpha College Grievance Cell <{SENDER_EMAIL}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'html'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def send_email(to_email, subject, body):
    # Run in a background thread so the website doesn't freeze while sending
    thread = threading.Thread(target=send_email_async, args=(to_email, subject, body))
    thread.start()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Ensure db exists and has the correct table
try:
    conn = get_db_connection()
    conn.execute('SELECT student_id FROM complaints LIMIT 1')
    conn.close()
except sqlite3.OperationalError:
    # If the column doesn't exist, the schema is old. Reset the DB.
    from database import init_db
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        email = request.form.get('email')
        department = request.form.get('department')
        category = request.form.get('category')
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority')
        
        conn = get_db_connection()
        conn.execute('INSERT INTO complaints (student_id, name, email, department, category, title, description, priority) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                     (student_id, name, email, department, category, title, description, priority))
        conn.commit()
        
        cursor = conn.cursor()
        cursor.execute("SELECT last_insert_rowid()")
        complaint_id = cursor.fetchone()[0]
        conn.close()
        
        # Send Confirmation Email
        subject = f"Grievance Received - ID: #{complaint_id}"
        body = f"""
        <h3>Hello {name},</h3>
        <p>Your grievance has been successfully submitted to the Alpha College Grievance Cell.</p>
        <p><strong>Tracking ID:</strong> #{complaint_id}<br>
        <strong>Category:</strong> {category}<br>
        <strong>Subject:</strong> {title}</p>
        <p>We are looking into this and will update you soon. You can track the status on our portal.</p>
        <br>
        <p>Regards,<br>Alpha College Administration</p>
        """
        send_email(email, subject, body)
        
        return jsonify({'status': 'success', 'message': 'Complaint registered successfully!', 'complaint_id': complaint_id})

    return render_template('register.html')

@app.route('/track', methods=['GET', 'POST'])
def track():
    complaint = None
    error = None
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        search_type = request.form.get('search_type')
        
        conn = get_db_connection()
        if search_type == 'id':
            complaint = conn.execute('SELECT * FROM complaints WHERE id = ?', (search_query,)).fetchone()
        else:
            complaint = conn.execute('SELECT * FROM complaints WHERE email = ? ORDER BY timestamp DESC', (search_query,)).fetchone()
        conn.close()
        
        if not complaint:
            error = "No complaint found with the given details."
            
    return render_template('track.html', complaint=complaint, error=error)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'Alpha' and password == 'Alpha@12345':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid credentials. Please try again."
    return render_template('admin_login.html', error=error)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    conn = get_db_connection()
    complaints = conn.execute('SELECT * FROM complaints ORDER BY timestamp DESC').fetchall()
    
    # Calculate stats
    total = len(complaints)
    resolved = sum(1 for c in complaints if c['status'] == 'Resolved')
    pending = sum(1 for c in complaints if c['status'] == 'Pending')
    
    conn.close()
    
    return render_template('admin_dashboard.html', complaints=complaints, stats={'total': total, 'resolved': resolved, 'pending': pending})

@app.route('/admin/update_status', methods=['POST'])
def update_status():
    if not session.get('admin_logged_in'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        
    complaint_id = request.form.get('id')
    new_status = request.form.get('status')
    
    if complaint_id and new_status:
        conn = get_db_connection()
        conn.execute('UPDATE complaints SET status = ? WHERE id = ?', (new_status, complaint_id))
        
        # Fetch student details for the email
        complaint = conn.execute('SELECT * FROM complaints WHERE id = ?', (complaint_id,)).fetchone()
        conn.commit()
        conn.close()
        
        if complaint:
            student_email = complaint['email']
            student_name = complaint['name']
            title = complaint['title']
            
            subject = f"Update on Grievance #{complaint_id}"
            body = f"""
            <h3>Hello {student_name},</h3>
            <p>The status of your grievance regarding "<strong>{title}</strong>" has been updated.</p>
            <p><strong>New Status:</strong> <span style="color: blue;">{new_status}</span></p>
            <p>You can check the full details by tracking your ID on the portal.</p>
            <br>
            <p>Regards,<br>Alpha College Administration</p>
            """
            send_email(student_email, subject, body)
            
        return jsonify({'status': 'success'})
        
    return jsonify({'status': 'error', 'message': 'Invalid data'})

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
