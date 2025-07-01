import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from api import api
from frontend import frontend
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()
secret_key = os.getenv('FLASK_SECRET_KEY')

if secret_key is None:
    print("Create the .env file with the SECRET_KEY variable")
    exit()

def create_app(include_frontend=True):
    """Creates the flask application with configurations"""

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv('FLASK_SECRET_KEY')
    CORS(app)

    # Fix for proxy headers to get correct IP
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    # register blueprints
    app.register_blueprint(api, url_prefix="/api/")

    # bundles frontend in with the flask app for easier run
    if include_frontend:
        app.register_blueprint(frontend, url_prefix="/")

    return app

if __name__ == '__main__':
    create_app(include_frontend=False).run(host="0.0.0.0", port=5000, debug=False)
