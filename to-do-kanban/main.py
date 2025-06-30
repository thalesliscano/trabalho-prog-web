from flask import Flask, request, jsonify
import json
import jwt
import datetime
from flask_cors import CORS  # Importando CORS

app = Flask(__name__)
CORS(app)  # Ativando CORS para todas as rotas

# Chave secreta para assinar o JWT
SECRET_KEY = "sua_chave_secreta"  # Mude para algo seguro

# Função para carregar as credenciais do JSON
def load_credentials():
    with open("users.json", "r") as file:
        return json.load(file)

# Função para gerar o token JWT
def generate_token(username):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expira em 1 hora
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Rota para login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # Carrega as credenciais do arquivo JSON
    credentials = load_credentials()

    # Verifica as credenciais
    if username == credentials["username"] and password == credentials["password"]:
        token = generate_token(username)
        return jsonify({"message": "Login successful", "status": "success", "token": token}), 200
    else:
        return jsonify({"message": "Invalid username or password", "status": "failure"}), 401

if __name__ == "__main__":
    app.run(debug=True)
