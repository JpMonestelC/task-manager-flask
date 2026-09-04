import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuración del proyecto - lee de variables de entorno, con valores
    # de desarrollo seguros como respaldo. Nunca fijes SECRET_KEY ni DEBUG=True
    # en el código para un despliegue real; ver README > Configuration.
    app.config.from_mapping(
        DEBUG=os.environ.get("FLASK_DEBUG", "0") == "1",
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-not-for-production"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///todolist.db"),
    )

    db.init_app(app)

    # Registro de blueprints
    from . import todo
    app.register_blueprint(todo.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    @app.route('/')
    def index():
        return render_template('index.html')
    
    with app.app_context():
        db.create_all()

    return app
