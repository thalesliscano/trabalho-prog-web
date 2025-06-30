# app/config.py
import os

class Config:
    # Recomenda-se carregar de variáveis de ambiente em produção
    # Para desenvolvimento, você pode definir um valor padrão
    SECRET_KEY = os.environ.get('SECRET_KEY', 'minha_chave_secreta_muito_segura_para_dev')
    DATABASE = os.environ.get('DATABASE_PATH', 'database.db')