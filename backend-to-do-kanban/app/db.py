# app/db.py
import sqlite3
import os
from .config import Config # Importe Config aqui!

# Remova o DB_FILE e o conectar_bd() antigo se eles estiverem duplicados.
# Use a versão centralizada do conectar_bd() e init_db().

def conectar_bd():
    # Use o caminho do banco de dados da sua configuração centralizada
    conn = sqlite3.connect(Config.DATABASE, timeout=30)
    conn.row_factory = sqlite3.Row # Adicione esta linha para retornar dicionários
    return conn

def init_db():
    conn = conectar_bd()
    cursor = conn.cursor()
    # Coloque aqui o script SQL completo para criar todas as tabelas
    # (users, boards, tasks, labels, task_labels)
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS boards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_task_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL CHECK(status IN ('toDo', 'doing', 'done', 'archived')),
            user_id INTEGER NOT NULL,
            board_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (board_id) REFERENCES boards (id) ON DELETE CASCADE,
            UNIQUE (user_task_id, user_id)
        );
        CREATE TABLE IF NOT EXISTS labels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            hex_color TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(name, user_id)
        );
        CREATE TABLE IF NOT EXISTS task_labels (
            task_id INTEGER NOT NULL,
            label_id INTEGER NOT NULL,
            PRIMARY KEY (task_id, label_id),
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
            FOREIGN KEY (label_id) REFERENCES labels (id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()

# O código de inicialização do DB e do app deve estar no seu run.py
# ou em um arquivo de inicialização da aplicação, não diretamente em db.py
# Apenas a função 'criar_tabelas' ou 'init_db' deve ser chamada onde você inicializa o DB.
# Por exemplo, no seu 'run.py' ou 'app/__init__.py'.

# Exemplo de como você pode usar init_db no seu run.py ou app/__init__.py:
# if os.path.exists(Config.DATABASE):
#     os.remove(Config.DATABASE) # Apenas para desenvolvimento, apaga e recria o DB
# init_db()