import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'geopermit-dev-secret-key-change-in-production')

    # MySQL connection
    MYSQL_HOST     = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER     = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'baisac.1123')
    MYSQL_DB       = os.environ.get('MYSQL_DB', 'geopermit_db')

    # File uploads
    UPLOAD_FOLDER    = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

    MAIL_SERVER   = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS  = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME','')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD','')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@geopermit.gov') 

    ADMIN_EMAIL = os.environ.get('ADMIN_EMAILS', 'admin@geopermit.gov')