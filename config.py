class Config:
    SECRET_KEY = 'une_clé_secrète'  # Pour sécuriser les sessions
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # Base de données SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False
