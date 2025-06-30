# app/services/tarefa_service.py

from ..db import conectar_bd
import sqlite3

class TaskService:

    @staticmethod
    def criar_tarefa(title, description, user_id, board_id, status):
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT MAX(user_task_id) FROM tasks WHERE user_id = ?", (user_id,))
            max_user_task_id = cursor.fetchone()[0]
            
            if max_user_task_id is None:
                user_task_id = 1
            else:
                user_task_id = max_user_task_id + 1

            cursor.execute(
                "INSERT INTO tasks (user_task_id, title, description, user_id, board_id, status) VALUES (?, ?, ?, ?, ?, ?)",
                (user_task_id, title, description, user_id, board_id, status)
            )
            conn.commit()

            return {
                'id': cursor.lastrowid, # Retorna o ID da tarefa recém-criada
                'user_task_id': user_task_id,
                'title': title,
                'description': description,
                'status': status,
                'user_id': user_id,
                'board_id': board_id,
                'labels': [] # Inicialmente sem labels
            }
        except sqlite3.Error as e:
            print(f"Erro ao criar tarefa: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def buscar_tarefas_por_usuario(user_id):
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    t.id, t.user_task_id, t.title, t.description, t.status, t.created_at,
                    GROUP_CONCAT(l.id || ':' || l.name || ':' || l.hex_color) as labels
                FROM tasks t
                LEFT JOIN task_labels tl ON t.id = tl.task_id
                LEFT JOIN labels l ON tl.label_id = l.id
                WHERE t.user_id = ?
                GROUP BY t.id
                ORDER BY t.created_at DESC
            """, (user_id,))
            tarefas = cursor.fetchall()
            
            if tarefas:
                tarefas_formatadas = []
                for tarefa in tarefas:
                    labels_data = []
                    if tarefa['labels']:
                        for label_str in tarefa['labels'].split(','):
                            label_parts = label_str.split(':')
                            if len(label_parts) == 3:
                                labels_data.append({
                                    'id': int(label_parts[0]),
                                    'name': label_parts[1],
                                    'hex_color': label_parts[2]
                                })
                    tarefas_formatadas.append({
                        'id': tarefa['id'],
                        'user_task_id': tarefa['user_task_id'],
                        'title': tarefa['title'],
                        'description': tarefa['description'],
                        'status': tarefa['status'],
                        'created_at': tarefa['created_at'],
                        'labels': labels_data
                    })
                return tarefas_formatadas
            else:
                return []
        except sqlite3.Error as e:
            print(f"Erro ao buscar tarefas por usuário: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def obter_board_do_usuario(user_id):
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boards WHERE user_id = ?", (user_id,))
            board = cursor.fetchone()
            
            if board:
                return board[0]
            return None
        except sqlite3.Error as e:
            print(f"Erro ao obter board do usuário: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def atualizar_status_tarefa(task_id, user_id, status):
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, title, description, status, user_id, board_id FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
            tarefa_existente = cursor.fetchone()

            if not tarefa_existente:
                return None

            cursor.execute("UPDATE tasks SET status = ? WHERE id = ? AND user_id = ?", (status, task_id, user_id))
            conn.commit()

            cursor.execute("""
                SELECT 
                    t.id, t.user_task_id, t.title, t.description, t.status, t.created_at, t.user_id, t.board_id,
                    GROUP_CONCAT(l.id || ':' || l.name || ':' || l.hex_color) as labels
                FROM tasks t
                LEFT JOIN task_labels tl ON t.id = tl.task_id
                LEFT JOIN labels l ON tl.label_id = l.id
                WHERE t.id = ? AND t.user_id = ?
                GROUP BY t.id
            """, (task_id, user_id))
            updated_task = cursor.fetchone()
            
            if updated_task:
                labels_data = []
                if updated_task['labels']:
                    for label_str in updated_task['labels'].split(','):
                        label_parts = label_str.split(':')
                        if len(label_parts) == 3:
                            labels_data.append({
                                'id': int(label_parts[0]),
                                'name': label_parts[1],
                                'hex_color': label_parts[2]
                            })
                return {
                    'id': updated_task['id'],
                    'user_task_id': updated_task['user_task_id'],
                    'title': updated_task['title'],
                    'description': updated_task['description'],
                    'status': updated_task['status'],
                    'created_at': updated_task['created_at'],
                    'user_id': updated_task['user_id'],
                    'board_id': updated_task['board_id'],
                    'labels': labels_data
                }
            return None
        except sqlite3.Error as e:
            print(f"Erro ao atualizar status da tarefa: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def excluir_tarefa(task_id, user_id):
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            
            # Deletar da tabela task_labels primeiro para garantir integridade referencial
            cursor.execute("DELETE FROM task_labels WHERE task_id = ?", (task_id,))
            
            cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                return True
            else:
                return False
        except sqlite3.Error as e:
            print(f"Erro ao excluir tarefa: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def vincular_label_a_tarefa(task_id, label_id, user_id):
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            # 1. Verificar se a tarefa pertence ao usuário
            cursor.execute("SELECT id FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
            task_exists = cursor.fetchone()
            if not task_exists:
                return {"erro": "Tarefa não encontrada ou não pertence ao usuário!"}, 404

            # 2. Verificar se a label pertence ao usuário
            cursor.execute("SELECT id FROM labels WHERE id = ? AND user_id = ?", (label_id, user_id))
            label_exists = cursor.fetchone()
            if not label_exists:
                return {"erro": "Label não encontrada ou não pertence ao usuário!"}, 404

            # 3. Vincular a label à tarefa na tabela task_labels
            cursor.execute(
                "INSERT OR IGNORE INTO task_labels (task_id, label_id) VALUES (?, ?)",
                (task_id, label_id)
            )
            conn.commit()

            # Retorna a tarefa atualizada com suas labels
            return TaskService.buscar_tarefa_por_id(task_id, user_id)

        except sqlite3.IntegrityError as e:
            print(f"Erro de integridade ao vincular label: {e}")
            return {"erro": "Vínculo de label já existe!"}, 400
        except sqlite3.Error as e:
            print(f"Erro no banco de dados ao vincular label: {e}")
            return {"erro": "Erro interno do servidor ao vincular label!"}, 500
        finally:
            if conn:
                conn.close()

    @staticmethod
    def desvincular_label_da_tarefa(task_id, label_id, user_id):
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            # 1. Verificar se a tarefa pertence ao usuário
            cursor.execute("SELECT id FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
            task_exists = cursor.fetchone()
            if not task_exists:
                return {"erro": "Tarefa não encontrada ou não pertence ao usuário!"}, 404

            # 2. Verificar se a label pertence ao usuário (importante para segurança)
            cursor.execute("SELECT id FROM labels WHERE id = ? AND user_id = ?", (label_id, user_id))
            label_exists = cursor.fetchone()
            if not label_exists:
                return {"erro": "Label não encontrada ou não pertence ao usuário!"}, 404

            # 3. Remover o vínculo na tabela task_labels
            cursor.execute(
                "DELETE FROM task_labels WHERE task_id = ? AND label_id = ?",
                (task_id, label_id)
            )
            conn.commit()

            if cursor.rowcount > 0:
                # Retorna a tarefa atualizada com suas labels
                return TaskService.buscar_tarefa_por_id(task_id, user_id)
            else:
                return {"erro": "Vínculo de label não encontrado para esta tarefa!"}, 404
        except sqlite3.Error as e:
            print(f"Erro no banco de dados ao desvincular label: {e}")
            return {"erro": "Erro interno do servidor ao desvincular label!"}, 500
        finally:
            if conn:
                conn.close()

    @staticmethod
    def buscar_tarefa_por_id(task_id, user_id):
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    t.id, t.user_task_id, t.title, t.description, t.status, t.created_at, t.user_id, t.board_id,
                    GROUP_CONCAT(l.id || ':' || l.name || ':' || l.hex_color) as labels
                FROM tasks t
                LEFT JOIN task_labels tl ON t.id = tl.task_id
                LEFT JOIN labels l ON tl.label_id = l.id
                WHERE t.id = ? AND t.user_id = ?
                GROUP BY t.id
            """, (task_id, user_id))
            tarefa = cursor.fetchone()

            if tarefa:
                labels_data = []
                if tarefa['labels']:
                    for label_str in tarefa['labels'].split(','):
                        label_parts = label_str.split(':')
                        if len(label_parts) == 3:
                            labels_data.append({
                                'id': int(label_parts[0]),
                                'name': label_parts[1],
                                'hex_color': label_parts[2]
                            })
                return {
                    'id': tarefa['id'],
                    'user_task_id': tarefa['user_task_id'],
                    'title': tarefa['title'],
                    'description': tarefa['description'],
                    'status': tarefa['status'],
                    'created_at': tarefa['created_at'],
                    'user_id': tarefa['user_id'],
                    'board_id': tarefa['board_id'],
                    'labels': labels_data
                }
            return None
        except sqlite3.Error as e:
            print(f"Erro ao buscar tarefa por ID: {e}")
            return None
        finally:
            if conn:
                conn.close()