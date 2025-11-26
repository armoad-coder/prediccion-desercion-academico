from flask import Flask
from config import Config
from extensions import db, bcrypt, jwt, cors
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    # Importar modelos aqui para que SQLAlchemy los registre
    from models.user import User
    from models.models import Student, Subject, StudentSubject

    # Importar y registrar las rutas
    from routes.main_routes import main_bp
    from routes.auth_routes import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Para migraciones
    Migrate(app, db)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)