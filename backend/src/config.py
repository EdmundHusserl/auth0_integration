from os import urandom


class Development:
    DEVELOPMENT = True
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///database/database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = urandom(32)    
    CORS_HEADERS = "Content-Type"
