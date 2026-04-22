import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'vtu27249@veltech.edu.in'
SENDER_PASSWORD = 'fxuuiqcjrpyysvjo'

print("Testing Gmail SMTP...")
try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.set_debuglevel(1)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    print("Gmail login successful!")
    server.quit()
except Exception as e:
    print(f"Gmail failed: {e}")

print("\nTesting Office365 SMTP...")
SMTP_SERVER_O365 = 'smtp.office365.com'
try:
    server = smtplib.SMTP(SMTP_SERVER_O365, SMTP_PORT)
    server.set_debuglevel(1)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    print("Office365 login successful!")
    server.quit()
except Exception as e:
    print(f"Office365 failed: {e}")
