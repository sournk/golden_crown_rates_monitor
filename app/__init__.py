from flask import Flask
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.cli import bp as cli_bp
    # cli_gorup=None for direct call commmand `flask update-rates` against `flask update-rates`
    app.register_blueprint(cli_bp, cli_group=None)

    return app
