import sqlite3
from ..db import conectar_bd
from app.services.auth import AuthService
# Importamos TaskService e LabelService aqui também para que UsuarioService
# possa buscar dados relacionados de outros serviços, seguindo a lógica de camadas.
from .board_service import BoardService
from .tarefa_service import TaskService # Adicionado
from .label_service import LabelService # Adicionado

class UsuarioService:

    @staticmethod
    def criar_usuario(nome, email, senha):
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return {'erro': 'E-mail já em uso'}
            
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (nome, email, senha)
            )
            conn.commit()
            
            user_id = cursor.lastrowid
            
            return {
                'usuario': {
                    'id': user_id,
                    'name': nome,
                    'email': email
                }
            }
        except sqlite3.Error as e:
            print(f"Erro no banco de dados ao criar usuário: {e}")
            return {'erro': 'Erro interno do servidor ao criar usuário.'}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def login(email, senha):
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            # Usar row_factory para retornar dicionários, se ainda não estiver configurado globalmente
            # conn.row_factory = sqlite3.Row # Remova se já configurado em conectar_bd()
            cursor.execute("SELECT id, name, email FROM users WHERE email = ? AND password = ?", (email, senha))
            usuario = cursor.fetchone()

            if not usuario:
                return None

            # Retornar como dicionário, se não estiver usando row_factory
            if isinstance(usuario, sqlite3.Row):
                return dict(usuario)
            else:
                # Assumindo que os índices estão corretos se não for sqlite3.Row
                return {'id': usuario[0], 'name': usuario[1], 'email': usuario[2]}

        except sqlite3.Error as e:
            print(f"Erro no banco de dados durante o login: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    # --- NOVO MÉTODO ---
    @staticmethod
    def buscar_usuario_por_id(user_id):
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            
            # Usar row_factory para retornar dicionários, se ainda não estiver configurado globalmente
            # conn.row_factory = sqlite3.Row # Remova se já configurado em conectar_bd()
            cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
            usuario = cursor.fetchone()

            if not usuario:
                return None # Retorna None se o usuário não for encontrado

            # Retornar como dicionário, se não estiver usando row_factory
            if isinstance(usuario, sqlite3.Row):
                return dict(usuario)
            else:
                return {'id': usuario[0], 'name': usuario[1], 'email': usuario[2]}

        except sqlite3.Error as e:
            print(f"Erro no banco de dados ao buscar usuário por ID: {e}")
            return None
        finally:
            if conn:
                conn.close()
    # --- FIM DO NOVO MÉTODO ---

    @staticmethod
    def buscar_todos_usuarios():
        # Este método não é chamado diretamente na rota '/usuarios/todos' (que chama buscar_todos_usuarios_detalhado),
        # mas pode ser útil para outros fins.
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT id, name, email FROM users")
            usuarios = cursor.fetchall()

            usuarios_com_labels = []

            for usuario_row in usuarios: # Renomeado para evitar conflito com a classe
                user_id = usuario_row[0]
                name = usuario_row[1]
                email = usuario_row[2]

                # Busca as labels do usuário usando LabelService
                labels = LabelService.buscar_labels_por_usuario(user_id)
                
                usuarios_com_labels.append({
                    'id': user_id,
                    'name': name,
                    'email': email,
                    'labels': labels
                })
            return usuarios_com_labels
        except sqlite3.Error as e:
            print(f"Erro no banco de dados ao buscar todos os usuários: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def buscar_todos_usuarios_detalhado():
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT id, name, email FROM users")
            usuarios_db = cursor.fetchall()

            usuarios_com_detalhes = []

            for user_row in usuarios_db:
                user_id = user_row[0]
                name = user_row[1]
                email = user_row[2]

                # Buscar o board com as tarefas associadas
                # Reutiliza o método existente que já busca tarefas
                board_com_tarefas = BoardService.buscar_board_com_tarefas_por_usuario(user_id)
                if not board_com_tarefas:
                    # Se um usuário não tem board (o que não deve acontecer se você sempre cria um padrão)
                    board_com_tarefas = {'id': None, 'name': 'Nenhum Board', 'tarefas': []}

                # Buscar as labels do usuário usando LabelService
                labels = LabelService.buscar_labels_por_usuario(user_id)

                usuario_detalhado = {
                    'id': user_id,
                    'name': name,
                    'email': email,
                    'board': board_com_tarefas,
                    'labels': labels
                }
                usuarios_com_detalhes.append(usuario_detalhado)

            return usuarios_com_detalhes
        except sqlite3.Error as e:
            print(f"Erro no banco de dados ao buscar todos os usuários detalhado: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    # Este método não é estático no seu código, mas deve ser se é chamado por UsuarioService.buscar_labels_por_usuario
    # Além disso, já foi implementado em LabelService, então é melhor chamar LabelService.buscar_labels_por_usuario
    # em vez de duplicar a lógica aqui. Removido a duplicação se o LabelService já existe.
    @staticmethod
    def buscar_labels_por_usuario(user_id):
        # Este método está duplicado e é melhor chamá-lo diretamente do LabelService
        # Isso ajuda a manter a responsabilidade do LabelService sobre as labels.
        # Se você realmente quer uma fachada aqui, chame o LabelService:
        return LabelService.buscar_labels_por_usuario(user_id)