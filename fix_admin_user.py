"""
fix_admin_user.py — Reset admin password to a valid hash
Run: python fix_admin_user.py
"""
from flask import Flask
from flask_mysqldb import MySQL
from config import Config
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def fix_admin():
    cur = mysql.connection.cursor()
    
    try:
        # Generate a proper password hash for 'password123'
        hashed_password = generate_password_hash('password123')
        
        # Update admin user with valid hash
        cur.execute(
            "UPDATE users SET password_hash = %s WHERE email = %s",
            (hashed_password, 'admin@geopermit.gov')
        )
        
        mysql.connection.commit()
        
        print("✅ Admin user password has been reset!")
        print("\nLogin with:")
        print("  Email: admin@geopermit.gov")
        print("  Password: password123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        mysql.connection.rollback()
    finally:
        cur.close()

if __name__ == '__main__':
    with app.app_context():
        fix_admin()