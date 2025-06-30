from app import create_app
import sqlite3
import os

DB_FILE = 'database.db'

def conectar_bd():
    return sqlite3.connect(DB_FILE)

def criar_tabelas():
    conn = conectar_bd()
    cursor = conn.cursor()

    # Tabela users
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
    ''')

    # Tabela boards
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS boards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')

    # Tabela tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_task_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            user_id INTEGER NOT NULL,
            board_id INTEGER NOT NULL,
            status TEXT CHECK(status IN ('toDo', 'doing', 'done', 'archived')) DEFAULT 'doing',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (board_id) REFERENCES boards(id)
        );
    ''')

    # Tabela labels (com user_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS labels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            hex_color TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(name, user_id)
        );
    ''')

    # Tabela task_labels
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_labels (
            task_id INTEGER NOT NULL,
            label_id INTEGER NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
            FOREIGN KEY (label_id) REFERENCES labels(id) ON DELETE CASCADE,
            PRIMARY KEY (task_id, label_id)
        );
    ''')

    conn.commit()
    conn.close()

# if os.path.exists(DB_FILE):
#     os.remove(DB_FILE)

# Cria as tabelas após apagar o banco
criar_tabelas()

# Inicializa a aplicação Flask
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
