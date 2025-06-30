# app/utils/decorators.py
from functools import wraps
from flask import request, jsonify, current_app # Importe current_app
from app.services.auth import AuthService # Importe AuthService

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'erro': 'Token de autenticação não fornecido'}), 401

        token = token.split(" ")[1] if " " in token else token

        # Aqui, AuthService.validar_token precisa acessar current_app.config['SECRET_KEY']
        # Certifique-se que o AuthService está configurado para isso.
        user_id = AuthService.validar_token(token) 

        if not user_id:
            return jsonify({'erro': 'Token inválido ou expirado'}), 401

        kwargs['user_id'] = user_id
        return f(*args, **kwargs)
    return decorated