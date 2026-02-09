"""Flask application factory for ProjectFlow.

Provides a ``create_app`` function following the standard Flask factory
pattern.  All route blueprints are registered here, and the shared
``ProjectStore`` instance is initialized on the app.
"""

from flask import Flask

from .routes import api
from .services import ProjectStore


def create_app() -> Flask:
    """Create and configure the Flask application.

    Initializes a fresh ``ProjectStore`` and attaches it to the app so
    that route handlers can access it via ``current_app.store``.

    Returns:
        A fully configured Flask app instance with all blueprints
        registered and ready to serve requests.
    """
    app = Flask(__name__)
    app.store = ProjectStore()
    app.register_blueprint(api, url_prefix="/api")
    return app
