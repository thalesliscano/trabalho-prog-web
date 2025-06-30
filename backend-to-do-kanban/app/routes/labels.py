from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from app.services.label_service import LabelService
from app.utils.decorators import token_required


labels_bp = Blueprint('labels', __name__)


@labels_bp.route('/labels', methods=['POST'])
@token_required
@swag_from({
    'tags': ['Labels'],
    'description': 'Cria uma nova label para o usuário autenticado',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'label',
            'in': 'body',
            'type': 'object',
            'required': True,
            'properties': {
                'name': {'type': 'string', 'description': 'Nome da label'},
                'hex_color': {'type': 'string', 'description': 'Cor hexadecimal da label (ex: #FF0000)'}
            },
            'example': {
                'name': 'Urgente',
                'hex_color': '#FF0000'
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Label criada com sucesso',
            'examples': {
                'application/json': {
                    'id': 1,
                    'name': 'Urgente',
                    'hex_color': '#FF0000',
                    'user_id': 1
                }
            }
        },
        '400': {
            'description': 'Campos obrigatórios ausentes ou label já existe',
            'examples': {
                'application/json': {'erro': 'Nome da label e cor são obrigatórios!'},
                'application/json': {'erro': 'Label "Urgente" já existe para você!'}
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
                'application/json': {'erro': 'Erro interno do servidor ao criar label!'}
            }
        }
    }
})
def criar_label(user_id):
    try:
        data = request.get_json()
        name = data.get('name')
        hex_color = data.get('hex_color')

        if not name or not hex_color:
            return jsonify({"erro": "Nome da label e cor são obrigatórios!"}), 400

        label = LabelService.criar_label(name, hex_color, user_id)

        if label and "erro" in label:
            return jsonify(label), 400
        elif label:
            return jsonify(label), 201
        else: # <--- RE-ADICIONE ESTE BLOCO!
            print("DEBUG: LabelService.criar_label retornou None. Retornando erro 500.")
            return jsonify({"erro": "Não foi possível criar a label devido a um problema interno."}), 500

    except Exception as e:
        print(f"Erro inesperado ao criar label: {e}")
        return jsonify({"erro": "Erro interno do servidor ao criar label!"}), 500


@labels_bp.route('/labels', methods=['GET'])
@token_required
@swag_from({
    'tags': ['Labels'],
    'description': 'Busca todas as labels associadas ao usuário autenticado',
    'security': [{'Bearer': []}],
    'responses': {
        '200': {
            'description': 'Lista de labels encontradas para o usuário (pode ser vazia)',
            'examples': {
                'application/json': [
                    {'id': 1, 'name': 'Urgente', 'hex_color': '#FF0000', 'user_id': 1}, # Incluído na resposta
                    {'id': 2, 'name': 'Pessoal', 'hex_color': '#00FF00', 'user_id': 1}
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
                'application/json': {'erro': 'Erro interno do servidor ao buscar labels!'}
            }
        }
    }
})
def buscar_labels(user_id):
    try:
        labels = LabelService.buscar_labels_por_usuario(user_id)
        return jsonify(labels), 200
    except Exception as e:
        print(f"Erro inesperado ao buscar labels: {e}")
        return jsonify({"erro": "Erro interno do servidor ao buscar labels!"}), 500


@labels_bp.route('/labels/<int:label_id>', methods=['PATCH'])
@token_required
@swag_from({
    'tags': ['Labels'],
    'description': 'Edita o nome e a cor de uma label existente do usuário autenticado',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'label_id',
            'in': 'path',
            'type': 'integer',
            'description': 'ID da label a ser editada',
            'required': True
        },
        {
            'name': 'body', # Alterado para 'body' para conter múltiplos campos
            'in': 'body',
            'type': 'object',
            'required': True,
            'properties': {
                'name': {'type': 'string', 'description': 'Novo nome da label'},
                'hex_color': {'type': 'string', 'description': 'Nova cor hexadecimal da label (ex: #FF0000)'} # NOVO CAMPO
            },
            'example': {
                'name': 'Prioridade Alta',
                'hex_color': '#FFA500' # Exemplo de nova cor
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Label atualizada com sucesso',
            'examples': {
                'application/json': {
                    'id': 1,
                    'name': 'Prioridade Alta',
                    'hex_color': '#FFA500', # Incluído na resposta
                    'user_id': 1
                }
            }
        },
        '400': {
            'description': 'Pelo menos um campo (nome ou cor) é obrigatório ou label com este nome já existe',
            'examples': {
                'application/json': {'erro': 'Pelo menos o nome ou a cor da label é obrigatório para atualização!'},
                'application/json': {'erro': 'Uma label com o nome "Prioridade Alta" já existe para você!'}
            }
        },
        '401': {
            'description': 'Token ausente ou inválido',
            'examples': {
                'application/json': {'erro': 'Token de autenticação não fornecido'}
            }
        },
        '404': {
            'description': 'Label não encontrada ou não pertence ao usuário',
            'examples': {
                'application/json': {'erro': 'Label não encontrada ou não pertence ao usuário!'}
            }
        },
        '500': {
            'description': 'Erro interno do servidor',
            'examples': {
                'application/json': {'erro': 'Erro interno do servidor ao editar label!'}
            }
        }
    }
})
def editar_label(label_id, user_id):
    try:
        data = request.get_json()
        name = data.get('name')
        hex_color = data.get('hex_color') # Obtendo a nova cor

        if not name and not hex_color: # Pelo menos um dos dois deve ser fornecido
            return jsonify({"erro": "Pelo menos o nome ou a cor da label é obrigatório para atualização!"}), 400

        # O serviço vai lidar com a lógica de quais campos atualizar
        label_atualizada = LabelService.editar_label(label_id, name, hex_color, user_id) # Passando ambos os campos

        if label_atualizada and "erro" in label_atualizada:
            return jsonify(label_atualizada), 400
        elif not label_atualizada:
            return jsonify({"erro": "Label não encontrada ou não pertence ao usuário!"}), 404

        return jsonify(label_atualizada), 200

    except Exception as e:
        print(f"Erro inesperado ao editar label: {e}")
        return jsonify({"erro": "Erro interno do servidor ao editar label!"}), 500


@labels_bp.route('/labels/<int:label_id>', methods=['DELETE'])
@token_required
@swag_from({
    'tags': ['Labels'],
    'description': 'Exclui uma label específica do usuário autenticado',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'label_id',
            'in': 'path',
            'type': 'integer',
            'description': 'ID da label a ser excluída',
            'required': True
        }
    ],
    'responses': {
        '200': {
            'description': 'Label excluída com sucesso',
            'examples': {
                'application/json': {'mensagem': 'Label excluída com sucesso!'}
            }
        },
        '401': {
            'description': 'Token ausente ou inválido',
            'examples': {
                'application/json': {'erro': 'Token de autenticação não fornecido'}
            }
        },
        '404': {
            'description': 'Label não encontrada ou não pertence ao usuário',
            'examples': {
                'application/json': {'erro': 'Label não encontrada ou não pertence ao usuário!'}
            }
        },
        '500': {
            'description': 'Erro interno do servidor',
            'examples': {
                'application/json': {'erro': 'Erro interno do servidor!'}
            }
        }
    }
})
def excluir_label(label_id, user_id):
    try:
        label_excluida = LabelService.excluir_label(label_id, user_id)

        if not label_excluida:
            return jsonify({"erro": "Label não encontrada ou não pertence ao usuário!"}), 404

        return jsonify({"mensagem": "Label excluída com sucesso!"}), 200

    except Exception as e:
        print(f"Erro inesperado ao excluir label: {e}")
        return jsonify({"erro": "Erro interno do servidor ao excluir label!"}), 500