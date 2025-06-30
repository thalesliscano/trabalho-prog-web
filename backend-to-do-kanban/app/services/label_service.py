# app/services/label_service.py

from ..db import conectar_bd
import sqlite3

class LabelService:

    @staticmethod
    def criar_label(name, hex_color, user_id): # Linha 9 - Esta linha deve estar identada corretamente
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO labels (name, hex_color, user_id) VALUES (?, ?, ?)",
                (name, hex_color, user_id)
            )
            conn.commit()

            label_id = cursor.lastrowid
            return {
                'id': label_id,
                'name': name,
                'hex_color': hex_color,
                'user_id': user_id
            }
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                print(f"Erro: Label '{name}' já existe para o usuário {user_id}.")
                # Modificação: Retorna um dicionário de erro aqui, sem relançar.
                return {"erro": f"Label '{name}' já existe para você!"}
            else:
                # Se for outro tipo de IntegrityError (improvável neste caso), ainda trate.
                print(f"Erro de integridade inesperado ao criar label: {e}")
                return {"erro": "Erro de integridade ao criar label!"}
        except sqlite3.Error as e:
            print(f"Erro no banco de dados ao criar label: {e}")
            return None # Continua retornando None para erros gerais de DB
        finally:
            if conn:
                conn.close()

    @staticmethod
    def buscar_labels_por_usuario(user_id):
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            # Selecionando hex_color também
            cursor.execute("SELECT id, name, hex_color, user_id FROM labels WHERE user_id = ?", (user_id,))
            labels = cursor.fetchall()

            if labels:
                # Incluindo hex_color no dicionário retornado
                return [{'id': label['id'], 'name': label['name'], 'hex_color': label['hex_color'], 'user_id': label['user_id']} for label in labels]
            return []
        except sqlite3.Error as e:
            print(f"Erro no banco de dados ao buscar labels: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def editar_label(label_id, new_name, hex_color, user_id): # Adicionado hex_color para edição
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            # Atualiza a label, garantindo que ela pertença ao user_id e atualizando a cor
            cursor.execute(
                "UPDATE labels SET name = ?, hex_color = ? WHERE id = ? AND user_id = ?", # Atualizando hex_color
                (new_name, hex_color, label_id, user_id)
            )
            conn.commit()

            if cursor.rowcount > 0:
                return {
                    'id': label_id,
                    'name': new_name,
                    'hex_color': hex_color, # Retornando hex_color atualizado
                    'user_id': user_id
                }
            return None
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                print(f"Erro: Label com o nome '{new_name}' já existe para o usuário {user_id}.")
                return {"erro": f"Uma label com o nome '{new_name}' já existe para você!"}
            raise e
        except sqlite3.Error as e:
            print(f"Erro no banco de dados ao editar label: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def excluir_label(label_id, user_id):
        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM labels WHERE id = ? AND user_id = ?",
                (label_id, user_id)
            )
            conn.commit()

            if cursor.rowcount > 0:
                return True
            return False
        except sqlite3.Error as e:
            print(f"Erro no banco de dados ao excluir label: {e}")
            return False
        finally:
            if conn:
                conn.close()