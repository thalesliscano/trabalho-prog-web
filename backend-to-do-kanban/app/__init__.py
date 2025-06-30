import sqlite3
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from .routes.usuarios import usuarios_bp
from .routes.tarefas import tarefas_bp
from .routes.labels import labels_bp # <-- NOVA IMPORTAÇÃO
from .config import Config

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app, origins=["http://localhost:8080"])

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "API To-Do Kanban",
            "description": "Documentação da API do sistema To-Do Kanban",
            "version": "1.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Digite: **Bearer &lt;seu_token&gt;**"
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ]
    }

    Swagger(app, template=swagger_template)

    app.register_blueprint(usuarios_bp)
    app.register_blueprint(tarefas_bp)
    app.register_blueprint(labels_bp) # <-- REGISTRE O NOVO BLUEPRINT

    return app