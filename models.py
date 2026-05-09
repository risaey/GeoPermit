"""
models.py — Database query helpers for GeoPermit System
All functions use flask_mysqldb cursor and return dicts or lists of dicts.
"""
import json
import math
from flask import g


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def get_db(mysql):
    """Return a DictCursor connected to MySQL."""
    return mysql.connection.cursor()


def haversine_distance(lat1, lng1, lat2, lng2):
    """Return distance in meters between two lat/lng points."""
    R = 6_371_000  # Earth radius in metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ---------------------------------------------------------------------------
# User model
# ---------------------------------------------------------------------------

def get_user_by_email(cursor, email):
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    return cursor.fetchone()


def get_user_by_id(cursor, user_id):
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()


def create_user(cursor, full_name, email, password_hash, role='user'):
    cursor.execute(
        "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
        (full_name, email, password_hash, role)
    )


def get_all_users(cursor):
    cursor.execute("SELECT id, full_name, email, role, created_at FROM users ORDER BY created_at DESC")
    return cursor.fetchall()


def delete_user(cursor, user_id):
    cursor.execute("DELETE FROM users WHERE id = %s AND role != 'admin'", (user_id,))


# ---------------------------------------------------------------------------
# Permit type model
# ---------------------------------------------------------------------------

def get_all_permit_types(cursor):
    cursor.execute("SELECT * FROM permit_types ORDER BY name")
    rows = cursor.fetchall()
    for row in rows:
        if isinstance(row['required_docs'], str):
            row['required_docs'] = json.loads(row['required_docs'])
    return rows


def get_permit_type_by_id(cursor, permit_type_id):
    cursor.execute("SELECT * FROM permit_types WHERE id = %s", (permit_type_id,))
    row = cursor.fetchone()
    if row and isinstance(row['required_docs'], str):
        row['required_docs'] = json.loads(row['required_docs'])
    return row


# ---------------------------------------------------------------------------
# Hazard zone model
# ---------------------------------------------------------------------------

def get_all_hazard_zones(cursor):
    cursor.execute("SELECT * FROM hazard_zones")
    return cursor.fetchall()


def check_hazard(cursor, lat, lng):
    """
    Check if (lat, lng) falls within any hazard zone.
    Returns a list of hazard zone dicts that the point falls in.
    """
    zones  = get_all_hazard_zones(cursor)
    hits   = []
    for zone in zones:
        dist = haversine_distance(lat, lng, float(zone['center_lat']), float(zone['center_lng']))
        if dist <= zone['radius_meters']:
            zone['distance_m'] = round(dist)
            hits.append(zone)
    return hits


# ---------------------------------------------------------------------------
# Application model
# ---------------------------------------------------------------------------

def create_application(cursor, user_id, permit_type_id, project_title,
                        project_description, lat, lng, address,
                        is_hazard, hazard_info):
    cursor.execute(
        """INSERT INTO applications
           (user_id, permit_type_id, project_title, project_description,
            location_lat, location_lng, location_address,
            is_hazard_zone, hazard_info)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (user_id, permit_type_id, project_title, project_description,
         lat, lng, address, is_hazard, hazard_info)
    )
    return cursor.lastrowid


def get_application_by_id(cursor, app_id):
    cursor.execute(
        """SELECT a.*, u.full_name, u.email, pt.name AS permit_type_name
           FROM applications a
           JOIN users u ON a.user_id = u.id
           JOIN permit_types pt ON a.permit_type_id = pt.id
           WHERE a.id = %s""",
        (app_id,)
    )
    return cursor.fetchone()


def get_applications_by_user(cursor, user_id):
    cursor.execute(
        """SELECT a.*, pt.name AS permit_type_name
           FROM applications a
           JOIN permit_types pt ON a.permit_type_id = pt.id
           WHERE a.user_id = %s
           ORDER BY a.submitted_at DESC""",
        (user_id,)
    )
    return cursor.fetchall()


def get_all_applications(cursor, status_filter=None):
    if status_filter and status_filter != 'all':
        cursor.execute(
            """SELECT a.*, u.full_name, u.email, pt.name AS permit_type_name
               FROM applications a
               JOIN users u ON a.user_id = u.id
               JOIN permit_types pt ON a.permit_type_id = pt.id
               WHERE a.status = %s
               ORDER BY a.submitted_at DESC""",
            (status_filter,)
        )
    else:
        cursor.execute(
            """SELECT a.*, u.full_name, u.email, pt.name AS permit_type_name
               FROM applications a
               JOIN users u ON a.user_id = u.id
               JOIN permit_types pt ON a.permit_type_id = pt.id
               ORDER BY a.submitted_at DESC"""
        )
    return cursor.fetchall()


def update_application_status(cursor, app_id, status, remarks):
    cursor.execute(
        "UPDATE applications SET status = %s, admin_remarks = %s WHERE id = %s",
        (status, remarks, app_id)
    )


def get_stats(cursor):
    cursor.execute("SELECT COUNT(*) AS total FROM applications")
    total = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS cnt FROM applications WHERE status = 'approved'")
    approved = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) AS cnt FROM applications WHERE status = 'rejected'")
    rejected = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) AS cnt FROM applications WHERE status = 'pending'")
    pending = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) AS cnt FROM applications WHERE is_hazard_zone = 1")
    hazard = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'user'")
    users = cursor.fetchone()['cnt']

    return {
        'total': total,
        'approved': approved,
        'rejected': rejected,
        'pending': pending,
        'hazard': hazard,
        'users': users,
    }


# ---------------------------------------------------------------------------
# Document model
# ---------------------------------------------------------------------------

def save_document(cursor, application_id, filename, original_name, file_type):
    cursor.execute(
        "INSERT INTO documents (application_id, filename, original_name, file_type) VALUES (%s, %s, %s, %s)",
        (application_id, filename, original_name, file_type)
    )


def get_documents_by_application(cursor, application_id):
    cursor.execute(
        "SELECT * FROM documents WHERE application_id = %s",
        (application_id,)
    )
    return cursor.fetchall()
