"""
routes/auth.py — Login, Register, Logout
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import models

auth_bp = Blueprint('auth', __name__)
mysql   = None  # injected by app.py via init_auth(mysql_instance)


def init_auth(mysql_instance):
    global mysql
    mysql = mysql_instance


# ---------------------------------------------------------------------------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        cur  = models.get_db(mysql)
        user = models.get_user_by_email(cur, email)
        cur.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id']   = user['id']
            session['user_name'] = user['full_name']
            session['user_role'] = user['role']
            flash('Welcome back, ' + user['full_name'] + '!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        full_name        = request.form.get('full_name', '').strip()
        email            = request.form.get('email', '').strip().lower()
        password         = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not all([full_name, email, password, confirm_password]):
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        cur = models.get_db(mysql)
        existing = models.get_user_by_email(cur, email)
        if existing:
            cur.close()
            flash('Email is already registered.', 'danger')
            return render_template('register.html')

        hashed = generate_password_hash(password)
        models.create_user(cur, full_name, email, hashed)
        mysql.connection.commit()
        cur.close()

        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
