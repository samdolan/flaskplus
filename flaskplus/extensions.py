from flask.ext.debugtoolbar import DebugToolbarExtension
from flask.ext.migrate import Migrate
from flask.ext.sqlalchemy import SQLAlchemy

__all__ = ['db', 'toolbar', 'migrate']

db = SQLAlchemy()
toolbar = DebugToolbarExtension()

migrate = Migrate()
