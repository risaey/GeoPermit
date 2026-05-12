"""
app.py — GeoPermit System Entry Point
Run:  python app.py
"""
import os
from flask import Flask, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

from config import Config
from email_service import mail

# Blueprints
from routes.auth      import auth_bp,      init_auth
from routes.dashboard import dashboard_bp, init_dashboard
from routes.permits   import permits_bp,   init_permits
from routes.admin     import admin_bp,     init_admin

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure uploads folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # MySQL — Set default cursor class BEFORE creating MySQL instance
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    
    mysql = MySQL(app)

    # initialize Flask-Mail
    mail.init_app(app)
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        app.logger.warning(
            'EMAIL WARNING: MAIL_USERNAME and MAIL_PASSWORD are not configured. '
            'SMTP email delivery is disabled until valid credentials are provided.'
        )


    #override the default cursor class to return dicts
    @app.before_request
    def set_mysql_cursor():
        pass #DictCursor configured below via mokey-patch

    # Inject mysql into each blueprint module AFTER mysql is created
    with app.app_context():
        init_auth(mysql)
        init_dashboard(mysql)
        init_permits(mysql)
        init_admin(mysql)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(permits_bp)
    app.register_blueprint(admin_bp)

    # Root redirect
    @app.route('/')
    def root():
        return redirect(url_for('auth.login'))

    # Custom DictCursor so fetchone/fetchall return dicts
    original_mysql_connection = MySQL.connection.fget
 
    def dict_cursor_connection(self):
        conn = original_mysql_connection(self)
        conn.cursorclass = MySQLdb.cursors.DictCursor
        return conn
 
    MySQL.connection = property(dict_cursor_connection)
    # Global template context
    
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'GeoPermit System',
            'current_user_name': session.get('user_name', ''),
            'current_user_role': session.get('user_role', ''),
        }

    return app


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)