import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# SQLite database file
SQLITE_DB_PATH = os.path.join(BASE_DIR, 'homebrew.db')

# Flask configuration
class Config:
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{SQLITE_DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
