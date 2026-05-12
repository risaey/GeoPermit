"""
test_email.py — Test Mailtrap connection
Run: python test_email.py
"""
from flask import Flask
from flask_mail import Mail, Message
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)

def test_email():
    try:
        msg = Message(
            subject='GeoPermit Test Email',
            recipients=['risalynpontrividabaisac@gmail.com'],
            body='This is a test email from GeoPermit system.'
        )
        mail.send(msg)
        print("✅ Email sent successfully!")
        print("Check your Mailtrap inbox: https://mailtrap.io")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    with app.app_context():
        test_email()