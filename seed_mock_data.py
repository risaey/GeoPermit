"""
seed_mock_data.py — Add test data to GeoPermit database
Run: python seed_mock_data.py
"""
from flask_mysqldb import MySQL
from flask import Flask
from config import Config
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import MySQLdb.cursors

app = Flask(__name__)
app.config.from_object(Config)
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def seed_database():
    cur = mysql.connection.cursor()

    try:
        # 1. Insert test users
        test_users = [
            {'full_name': 'Juan dela Cruz', 'email': 'juan@example.com',   'password': 'password123', 'role': 'user'},
            {'full_name': 'Maria Santos',   'email': 'maria@example.com',  'password': 'password123', 'role': 'user'},
            {'full_name': 'Carlos Reyes',   'email': 'carlos@example.com', 'password': 'password123', 'role': 'user'},
            {'full_name': 'Ana Garcia',     'email': 'ana@example.com',    'password': 'password123', 'role': 'user'},
        ]

        for user in test_users:
            hashed_pwd = generate_password_hash(user['password'])
            try:
                cur.execute(
                    "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                    (user['full_name'], user['email'], hashed_pwd, user['role'])
                )
                print(f"✅ Created user: {user['full_name']} ({user['email']})")
            except MySQLdb.IntegrityError:
                print(f"⚠️  User already exists: {user['email']}")

        mysql.connection.commit()

        # 2. Get user IDs
        cur.execute("SELECT id, email FROM users WHERE role='user' LIMIT 4")
        users = cur.fetchall()
        user_ids = [u['id'] for u in users]

        # 3. Insert test applications — NOTE: loop variable renamed to 'appl'
        #    and submitted_at uses strftime instead of isoformat
        test_applications = [
            {
                'user_id': user_ids[0] if len(user_ids) > 0 else 2,
                'permit_type_id': 1,
                'project_title': 'Tree Removal at Lahug Avenue',
                'project_description': 'Removal of 5 old mango trees blocking the road',
                'location_lat': 10.3163,
                'location_lng': 123.8854,
                'location_address': 'Lahug Avenue, Cebu City',
                'is_hazard_zone': True,
                'hazard_info': 'Located in Lahug River Flood Zone',
                'status': 'pending',
                'admin_remarks': None,
                'submitted_at': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'user_id': user_ids[1] if len(user_ids) > 1 else 3,
                'permit_type_id': 2,
                'project_title': 'New Office Building at IT Park',
                'project_description': '5-storey commercial office building with parking',
                'location_lat': 10.3170,
                'location_lng': 123.8890,
                'location_address': 'IT Park, Cebu City',
                'is_hazard_zone': False,
                'hazard_info': None,
                'status': 'approved',
                'admin_remarks': 'All requirements met. Approved for construction.',
                'submitted_at': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'user_id': user_ids[2] if len(user_ids) > 2 else 4,
                'permit_type_id': 3,
                'project_title': 'Road Foundation Excavation',
                'project_description': 'Excavation for new road infrastructure in Banilad',
                'location_lat': 10.3200,
                'location_lng': 123.9200,
                'location_address': 'Banilad, Cebu City',
                'is_hazard_zone': True,
                'hazard_info': 'Near Tabu Protected Area - environmental assessment required',
                'status': 'under_review',
                'admin_remarks': 'Awaiting environmental compliance certificate',
                'submitted_at': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'user_id': user_ids[3] if len(user_ids) > 3 else 5,
                'permit_type_id': 4,
                'project_title': 'Billboard Installation at Paseo',
                'project_description': '12x8 feet LED billboard for commercial advertisement',
                'location_lat': 10.3100,
                'location_lng': 123.8800,
                'location_address': 'Paseo de Santa Rosa, Cebu City',
                'is_hazard_zone': False,
                'hazard_info': None,
                'status': 'rejected',
                'admin_remarks': 'Rejected: Location violates zoning regulations.',
                'submitted_at': (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'user_id': user_ids[0] if len(user_ids) > 0 else 2,
                'permit_type_id': 1,
                'project_title': 'Tree Cutting at Busay Heights',
                'project_description': 'Trimming of trees for safety purposes',
                'location_lat': 10.3600,
                'location_lng': 123.8700,
                'location_address': 'Busay Heights, Cebu City',
                'is_hazard_zone': True,
                'hazard_info': 'Busay Heights Landslide Zone - geotechnical assessment needed',
                'status': 'pending',
                'admin_remarks': None,
                'submitted_at': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
            },
        ]

        app_ids = []
        for appl in test_applications:                          # ← 'appl' not 'app'
            cur.execute(
                """INSERT INTO applications
                   (user_id, permit_type_id, project_title, project_description,
                    location_lat, location_lng, location_address, is_hazard_zone,
                    hazard_info, status, admin_remarks, submitted_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (appl['user_id'], appl['permit_type_id'], appl['project_title'],
                 appl['project_description'], appl['location_lat'], appl['location_lng'],
                 appl['location_address'], appl['is_hazard_zone'], appl['hazard_info'],
                 appl['status'], appl['admin_remarks'], appl['submitted_at'])
            )
            app_ids.append(cur.lastrowid)
            print(f"✅ Created application: {appl['project_title']} (Status: {appl['status']})")

        mysql.connection.commit()

        # 4. Documents — same as your original, no changes needed
        sample_docs = [
            {'app_id': app_ids[0], 'filename': 'barangay_clearance_001.pdf', 'original_name': 'Barangay Clearance',    'file_type': 'pdf'},
            {'app_id': app_ids[0], 'filename': 'land_title_001.pdf',         'original_name': 'Land Title',            'file_type': 'pdf'},
            {'app_id': app_ids[1], 'filename': 'building_plan_001.pdf',      'original_name': 'Approved Building Plan','file_type': 'pdf'},
            {'app_id': app_ids[1], 'filename': 'tax_clearance_001.pdf',      'original_name': 'Tax Clearance',         'file_type': 'pdf'},
            {'app_id': app_ids[2], 'filename': 'site_plan_001.pdf',          'original_name': 'Site Plan',             'file_type': 'pdf'},
            {'app_id': app_ids[2], 'filename': 'geo_assessment_001.pdf',     'original_name': 'Geological Assessment', 'file_type': 'pdf'},
            {'app_id': app_ids[3], 'filename': 'structural_analysis_001.pdf','original_name': 'Structural Analysis',   'file_type': 'pdf'},
            {'app_id': app_ids[4], 'filename': 'barangay_clearance_002.pdf', 'original_name': 'Barangay Clearance',    'file_type': 'pdf'},
        ]

        for doc in sample_docs:
            cur.execute(
                "INSERT INTO documents (application_id, filename, original_name, file_type) VALUES (%s, %s, %s, %s)",
                (doc['app_id'], doc['filename'], doc['original_name'], doc['file_type'])
            )
            print(f"✅ Added document: {doc['original_name']} → Application #{doc['app_id']}")

        mysql.connection.commit()

        print("\n" + "="*60)
        print("✅ MOCK DATA SEEDING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nTest Accounts:")
        print("  juan@example.com   / password123")
        print("  maria@example.com  / password123")
        print("  carlos@example.com / password123")
        print("  ana@example.com    / password123")
        print("\nAdmin:")
        print("  admin@geopermit.gov / admin123")
        print("="*60)

    except Exception as e:
        print(f"❌ Error: {e}")
        mysql.connection.rollback()
    finally:
        cur.close()