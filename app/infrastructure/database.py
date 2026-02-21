# ==============================================================================
# FILE: app/database.py
# DESCRIPTION: Central registry for Flask database (SQLAlchemy, etc.).
#              Prevents circular import errors by decoupling initialization.
# ==============================================================================

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()