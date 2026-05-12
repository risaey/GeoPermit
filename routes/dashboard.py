"""
routes/dashboard.py — Main dashboard for users and admins
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash
from functools import wraps
import models

dashboard_bp = Blueprint('dashboard', __name__)
mysql = None


def init_dashboard(mysql_instance):
    global mysql
    mysql = mysql_instance


# ---------------------------------------------------------------------------
# Auth decorators
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('user_role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    cur = models.get_db(mysql)

    if session.get('user_role') == 'admin':
        cur.close()
        return redirect(url_for('admin.overview'))   # ← redirect, not render
    else:
        applications = models.get_applications_by_user(cur, session['user_id'])
        cur.close()
        return render_template('dashboard.html', applications=applications)
