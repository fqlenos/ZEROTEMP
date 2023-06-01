import os
import secrets

basedir = os.path.abspath(os.path.dirname(__file__))
parentdir = os.path.abspath(os.path.join(basedir, os.pardir))

class Config:
    SECRET_KEY = 'zerotemp'
    UPLOAD_FOLDER = os.path.join(parentdir, 'app', 'uploads')
    DOWNLOAD_FOLDER = os.path.join(parentdir, 'app', 'downloads')
    ALLOWED_EXTENSIONS = { 'jpg', 'jpeg', 'png' }
    MAX_CONTENT_LENGTH = 64 * 1024 * 1024 # 64MB
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.jpeg', '.zip']
    STORAGE_URI = None

class Development(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'zerotemp.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DEBUG = True
    TESTING = True
    TEMPLATES_AUTO_RELOAD = True
    SESSION_COOKIE_SECURE =  False
    SESSION_COOKIE_HTTPONLY =  False
    SEND_FILE_MAX_AGE_DEFAULT = 0

class Production(Config):
    SECRET_KEY = secrets.token_hex(32 // 2) # 32 bytes is enough, more bytes could affect the performance
