import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Project configuration - reads from environment variables, with safe
    # development defaults as fallback. Never hardcode SECRET_KEY or
    # DEBUG=True for a real deployment; see README > Configuration.
    app.config.from_mapping(
        DEBUG=os.environ.get("FLASK_DEBUG", "0") == "1",
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-not-for-production"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///todolist.db"),
    )

    db.init_app(app)

    # Register blueprints
    from . import todo
    app.register_blueprint(todo.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    @app.route('/')
    def index():
        """Render the public landing page."""
        return render_template('index.html')
    
    with app.app_context():
        db.create_all()

    return app
