from flask import Flask
from config import Config
from extensions import db, migrate
from courses.routes import courses_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(courses_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)