# app/routes/tarefas.py

from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from app.services.tarefa_service import TaskService
import jwt # Importe jwt para as funções de token se ainda estiverem sendo usadas (idealmente no decorador)

from app.utils.decorators import token_required


tarefas_bp = Blueprint('tasks', __name__)

# Mantenha estas funções se ainda precisar delas em algum lugar fora do decorador.
# Caso contrário, pode removê-las.
def obter_user_id_do_token(token):
    try:
        decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"], options={"verify_exp": True})
        return decoded_token.get("user_id")
    except jwt.ExpiredSignatureError:
        print("Erro: Token expirado!")
        return None
    except jwt.InvalidTokenError:
        print("Erro: Token inválido!")
        return None

def extrair_token_do_header():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None


# ----------------- ROTAS TAREFAS -----------------

@tarefas_bp.route('/tasks', methods=['POST'])
@token_required
@swag_from({
    'tags': ['Tarefas'],
    'description': 'Cria uma nova tarefa associada a um board de um usuário autenticado',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'tarefa',
            'in': 'body',
            'type': 'object',
            'required': True,
            'properties': {
                'title': {'type': 'string', 'description': 'Título da tarefa'},
                'description': {'type': 'string', 'description': 'Descrição da tarefa'},
                'status': {'type': 'string', 'enum': ['toDo', 'doing', 'done', 'archived'], 'default': 'toDo', 'description': 'Status da tarefa'},
                'labels': {'type': 'array', 'items': {'type': 'integer'}, 'description': 'Lista de IDs de labels a serem associadas à tarefa (opcional)'} # NOVO CAMPO
            },
            'example': {
                'title': 'Nova Tarefa',
                'description': 'Descrição da tarefa',
                'status': 'toDo',
                'labels': [1, 2] # Exemplo de IDs de labels
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Tarefa criada com sucesso',
            'examples': {
                'application/json': {
                    'id': 1, # Adicionado ID da tarefa
                    'user_task_id': 1,
                    'title': 'Nova Tarefa',
                    'description': 'Descrição da tarefa',
                    'user_id': 1,
                    'board_id': 1,
                    'status': 'toDo',
                    'labels': [{'id': 1, 'name': 'Urgente', 'hex_color': '#FF0000'}] # Exemplo de labels associadas
                }
            }
        },
        '400': {
            'description': 'Campos obrigatórios ausentes ou erro na requisição',
            'examples': {
                'application/json': {'erro': 'Título é obrigatório!'},
                'application/json': {'erro': 'Alguma(s) label(s) fornecida(s) não pertence(m) a você ou não existe(m)!'}
            }
        },
        '401': {
            'description': 'Token inválido ou expirado',
            'examples': {
                'application/json': {'erro': 'Token inválido ou expirado!'}
            }
        },
        '404': {
            'description': 'Board não encontrado para o usuário',
            'examples': {
                'application/json': {'erro': 'Board não encontrado para o usuário!'}
            }
        },
        '500': {
            'description': 'Erro interno do servidor',
            'examples': {
                'application/json': {'erro': 'Erro interno do servidor ao criar tarefa!'}
            }
        }
    }
})
def criar_tarefa(user_id):
    try:
        data = request.get_json()

        title = data.get('title')
        description = data.get('description')
        status = data.get('status', 'toDo')
        label_ids = data.get('labels', []) # Novo: lista de IDs de labels

        if not title:
            return jsonify({"erro": "Título é obrigatório!"}), 400

        board_id = TaskService.obter_board_do_usuario(user_id)
        if not board_id:
            return jsonify({"erro": "Board não encontrado para o usuário!"}), 404

        tarefa = TaskService.criar_tarefa(title, description, user_id, board_id, status)
        
        if tarefa:
            # Associar labels se forem fornecidas
            if label_ids:
                for label_id in label_ids:
                    response, status_code = TaskService.vincular_label_a_tarefa(tarefa['id'], label_id, user_id)
                    if status_code != 200: # Se houver erro ao vincular uma label
                        # Rollback da criação da tarefa se uma label não puder ser vinculada
                        TaskService.excluir_tarefa(tarefa['id'], user_id)
                        return jsonify({"erro": f"Erro ao vincular label {label_id}: {response['erro']}"}), status_code
                # Após vincular todas as labels, buscar a tarefa novamente para retornar com as labels
                tarefa_completa = TaskService.buscar_tarefa_por_id(tarefa['id'], user_id)
                return jsonify(tarefa_completa), 201
            return jsonify(tarefa), 201
        else:
            return jsonify({"erro": "Não foi possível criar a tarefa devido a um problema interno."}), 500

    except Exception as e:
        print(f"Erro inesperado ao criar tarefa: {e}")
        return jsonify({"erro": "Erro interno do servidor ao criar tarefa!"}), 500

@tarefas_bp.route('/tasks', methods=['GET'])
@token_required
@swag_from({
    'tags': ['Tarefas'],
    'description': 'Busca as tarefas associadas ao usuário autenticado',
    'security': [{'Bearer': []}],
    'responses': {
        '200': {
            'description': 'Lista de tarefas encontradas para o usuário logado (pode ser vazia)',
            'examples': {
                'application/json': [
                    {'id': 1, 'user_task_id': 1, 'title': 'Tarefa 1', 'description': 'Descrição 1', 'status': 'toDo', 'created_at': '2025-06-19 10:00:00', 'labels': [{'id': 1, 'name': 'Urgente', 'hex_color': '#FF0000'}]},
                    {'id': 2, 'user_task_id': 2, 'title': 'Tarefa 2', 'description': 'Descrição 2', 'status': 'doing', 'created_at': '2025-06-19 10:05:00', 'labels': []}
                ]
            }
        },
        '401': {
            'description': 'Token ausente ou inválido',
            'examples': {
                'application/json': {'erro': 'Token de autenticação não fornecido'}
            }
        },
        '500': {
            'description': 'Erro interno do servidor',
            'examples': {
                'application/json': {'erro': 'Erro interno do servidor ao buscar tarefas!'}
            }
        }
    }
})
def buscar_tarefas(user_id):
    try:
        tarefas = TaskService.buscar_tarefas_por_usuario(user_id)
        return jsonify(tarefas), 200
    except Exception as e:
        print(f"Erro inesperado ao buscar tarefas: {e}")
        return jsonify({"erro": "Erro interno do servidor ao buscar tarefas!"}), 500


@tarefas_bp.route('/tasks/status/<int:task_id>', methods=['PATCH'])
@token_required
@swag_from({
    'tags': ['Tarefas'],
    'description': 'Atualiza o status de uma tarefa existente do usuário autenticado',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'integer',
            'description': 'ID principal da tarefa a ser atualizada',
            'required': True
        },
        {
            'name': 'status',
            'in': 'body',
            'type': 'object',
            'required': True,
            'properties': {
                'status': {'type': 'string', 'enum': ['toDo', 'doing', 'done', 'archived'], 'description': 'Novo status da tarefa'}
            },
            'example': {
                'status': 'done'
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Status da tarefa atualizado com sucesso',
            'examples': {
                'application/json': {
                    'id': 1,
                    'title': 'Nova Tarefa',
                    'description': 'Descrição da tarefa',
                    'status': 'done',
                    'user_id': 1,
                    'board_id': 1,
                    'labels': [{'id': 1, 'name': 'Urgente', 'hex_color': '#FF0000'}] # Exemplo de labels associadas
                }
            }
        },
        '400': {
            'description': 'Campos obrigatórios ausentes',
            'examples': {
                'application/json': {'erro': 'Status é obrigatório!'}
            }
        },
        '401': {
            'description': 'Token ausente ou inválido',
            'examples': {
                'application/json': {'erro': 'Token de autenticação não fornecido'}
            }
        },
        '404': {
            'description': 'Tarefa não encontrada ou não pertence ao usuário',
            'examples': {
                'application/json': {'erro': 'Tarefa não encontrada ou não pertence ao usuário!'}
            }
        },
        '500': {
            'description': 'Erro interno do servidor',
            'examples': {
                'application/json': {'erro': 'Erro interno do servidor ao editar tarefa!'}
            }
        }
    }
})
def editar_tarefa_status(task_id, user_id):
    try:
        data = request.get_json()
        status = data.get('status')
        if not status:
            return jsonify({"erro": "Status é obrigatório!"}), 400

        tarefa_atualizada = TaskService.atualizar_status_tarefa(task_id, user_id, status)

        if not tarefa_atualizada:
            return jsonify({"erro": "Tarefa não encontrada ou não pertence ao usuário!"}), 404

        return jsonify(tarefa_atualizada), 200

    except Exception as e:
        print(f"Erro inesperado ao editar tarefa status: {e}")
        return jsonify({"erro": "Erro interno do servidor ao editar tarefa!"}), 500

@tarefas_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_required
@swag_from({
    'tags': ['Tarefas'],
    'description': 'Exclui uma tarefa específica do usuário autenticado',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'integer',
            'description': 'ID principal da tarefa a ser excluída',
            'required': True
        }
    ],
    'responses': {
        '200': {
            'description': 'Tarefa excluída com sucesso',
            'examples': {
                'application/json': {'mensagem': 'Tarefa excluída com sucesso!'}
            }
        },
        '401': {
            'description': 'Token ausente ou inválido',
            'examples': {
                'application/json': {'erro': 'Token de autenticação não fornecido'}
            }
        },
        '404': {
            'description': 'Tarefa não encontrada ou não pertence ao usuário',
            'examples': {
                'application/json': {'erro': 'Tarefa não encontrada ou não pertence ao usuário!'}
            }
        },
        '500': {
            'description': 'Erro interno do servidor',
            'examples': {
                'application/json': {'erro': 'Erro interno do servidor ao excluir tarefa!'}
            }
        }
    }
})
def excluir_tarefa(task_id, user_id):
    try:
        tarefa_excluida = TaskService.excluir_tarefa(task_id, user_id)

        if not tarefa_excluida:
            return jsonify({"erro": "Tarefa não encontrada ou não pertence ao usuário!"}), 404

        return jsonify({"mensagem": "Tarefa excluída com sucesso!"}), 200

    except Exception as e:
        print(f"Erro inesperado ao excluir tarefa: {e}")
        return jsonify({"erro": "Erro interno do servidor ao excluir tarefa!"}), 500

# NOVO ENDPOINT: Vincular uma label a uma tarefa
@tarefas_bp.route('/tasks/<int:task_id>/labels', methods=['POST'])
@token_required
@swag_from({
    'tags': ['Tarefas'],
    'description': 'Vincula uma label existente a uma tarefa específica do usuário autenticado',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'integer',
            'description': 'ID da tarefa à qual a label será vinculada',
            'required': True
        },
        {
            'name': 'body',
            'in': 'body',
            'type': 'object',
            'required': True,
            'properties': {
                'label_id': {'type': 'integer', 'description': 'ID da label a ser vinculada'}
            },
            'example': {
                'label_id': 1
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Label vinculada à tarefa com sucesso',
            'examples': {
                'application/json': {
                    'id': 1,
                    'user_task_id': 1,
                    'title': 'Tarefa com Label',
                    'description': '...',
                    'status': 'toDo',
                    'user_id': 1,
                    'board_id': 1,
                    'labels': [{'id': 1, 'name': 'Urgente', 'hex_color': '#FF0000'}]
                }
            }
        },
        '400': {
            'description': 'ID da label ausente ou vínculo já existente',
            'examples': {
                'application/json': {'erro': 'ID da label é obrigatório!'},
                'application/json': {'erro': 'Vínculo de label já existe!'}
            }
        },
        '401': {
            'description': 'Token ausente ou inválido',
            'examples': {
                'application/json': {'erro': 'Token de autenticação não fornecido'}
            }
        },
        '404': {
            'description': 'Tarefa ou Label não encontrada ou não pertence ao usuário',
            'examples': {
                'application/json': {'erro': 'Tarefa não encontrada ou não pertence ao usuário!'},
                'application/json': {'erro': 'Label não encontrada ou não pertence ao usuário!'}
            }
        },
        '500': {
            'description': 'Erro interno do servidor',
            'examples': {
                'application/json': {'erro': 'Erro interno do servidor ao vincular label!'}
            }
        }
    }
})
def vincular_label_tarefa(task_id, user_id):
    try:
        data = request.get_json()
        label_id = data.get('label_id')

        if not label_id:
            return jsonify({"erro": "ID da label é obrigatório!"}), 400

        result = TaskService.vincular_label_a_tarefa(task_id, label_id, user_id)
        
        if "erro" in result:
            return jsonify(result), result.get("status_code", 500) # Usar status_code do serviço, se presente
        
        return jsonify(result), 200

    except Exception as e:
        print(f"Erro inesperado ao vincular label à tarefa: {e}")
        return jsonify({"erro": "Erro interno do servidor ao vincular label!"}), 500

# NOVO ENDPOINT: Desvincular uma label de uma tarefa
@tarefas_bp.route('/tasks/<int:task_id>/labels/<int:label_id>', methods=['DELETE'])
@token_required
@swag_from({
    'tags': ['Tarefas'],
    'description': 'Desvincula uma label de uma tarefa específica do usuário autenticado',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'integer',
            'description': 'ID da tarefa da qual a label será desvinculada',
            'required': True
        },
        {
            'name': 'label_id',
            'in': 'path',
            'type': 'integer',
            'description': 'ID da label a ser desvinculada',
            'required': True
        }
    ],
    'responses': {
        '200': {
            'description': 'Label desvinculada da tarefa com sucesso',
            'examples': {
                'application/json': {
                    'id': 1,
                    'user_task_id': 1,
                    'title': 'Tarefa sem Label',
                    'description': '...',
                    'status': 'toDo',
                    'user_id': 1,
                    'board_id': 1,
                    'labels': []
                }
            }
        },
        '401': {
            'description': 'Token ausente ou inválido',
            'examples': {
                'application/json': {'erro': 'Token de autenticação não fornecido'}
            }
        },
        '404': {
            'description': 'Tarefa, Label ou vínculo não encontrado ou não pertence ao usuário',
            'examples': {
                'application/json': {'erro': 'Tarefa não encontrada ou não pertence ao usuário!'},
                'application/json': {'erro': 'Label não encontrada ou não pertence ao usuário!'},
                'application/json': {'erro': 'Vínculo de label não encontrado para esta tarefa!'}
            }
        },
        '500': {
            'description': 'Erro interno do servidor',
            'examples': {
                'application/json': {'erro': 'Erro interno do servidor ao desvincular label!'}
            }
        }
    }
})
def desvincular_label_tarefa(task_id, label_id, user_id):
    try:
        result = TaskService.desvincular_label_da_tarefa(task_id, label_id, user_id)

        if "erro" in result:
            return jsonify(result), result.get("status_code", 500)
        
        return jsonify(result), 200

    except Exception as e:
        print(f"Erro inesperado ao desvincular label da tarefa: {e}")
        return jsonify({"erro": "Erro interno do servidor ao desvincular label!"}), 500