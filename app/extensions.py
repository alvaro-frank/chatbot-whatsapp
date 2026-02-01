# ==============================================================================
# FILE: app/extensions.py
# DESCRIPTION: Central registry for Flask extensions (SQLAlchemy, etc.).
#              Prevents circular import errors by decoupling initialization.
# ==============================================================================

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()