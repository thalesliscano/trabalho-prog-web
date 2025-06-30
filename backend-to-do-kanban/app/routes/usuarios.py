from flask import Flask, Blueprint, request, jsonify
from flasgger import swag_from
from functools import wraps
from ..services.usuario_service import UsuarioService
from ..services.board_service import BoardService
from app.services.auth import AuthService
import json
from flask import Response
from app.utils.decorators import token_required
from app.services.label_service import LabelService # Importar LabelService

# Agora, defina as rotas normalmente
usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/usuarios', methods=['POST'])
@swag_from({
    'tags': ['Usuários'],
    'description': 'Cria um novo usuário no sistema e um board padrão associado',
    'parameters': [
        {
            'name': 'usuario',
            'in': 'body',
            'type': 'object',
            'required': True,
            'properties': {
                'name': {'type': 'string', 'description': 'Nome do usuário'},
                'email': {'type': 'string', 'description': 'E-mail do usuário (deve ser único)'},
                'password': {'type': 'string', 'description': 'Senha do usuário'}
            },
            'example': {
                'name': 'João',
                'email': 'joao@exemplo.com',
                'password': 'senha123'
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Usuário e board padrão criados com sucesso',
            'examples': {
                'application/json': {
                    'mensagem': 'Usuário criado com sucesso',
                    'usuario': {'id': 1, 'name': 'João', 'email': 'joao@exemplo.com'},
                    'board': {'id': 1, 'name': 'Meu Board Padrão'}
                }
            }
        },
        '400': {
            'description': 'Erro ao criar usuário',
            'examples': {
                'application/json': {'erro': 'E-mail já em uso'}
            }
        }
    }
})
def criar_usuario():
    dados = request.json
    nome = dados.get('name')
    email = dados.get('email')
    senha = dados.get('password')
    
    if not nome or not email or not senha:
        return {"error": "Campos 'name', 'email' e 'password' são obrigatórios"}, 400

    resposta = UsuarioService.criar_usuario(nome, email, senha)
    
    if 'erro' in resposta:
        return jsonify(resposta), 400
    
    user_id = resposta['usuario']['id']
    
    # Cria o board padrão
    board = BoardService.criar_board(user_id, 'Meu Board Padrão')
    
    return jsonify({
        'mensagem': 'Usuário criado com sucesso',
        'usuario': resposta['usuario'],
        'board': board
    }), 201
@usuarios_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Usuários'],
    'description': 'Rota de login para autenticação do usuário',
    'parameters': [
        {
            'name': 'usuario',
            'in': 'body',
            'type': 'object',
            'required': True,
            'properties': {
                'email': {
                    'type': 'string',
                    'description': 'E-mail do usuário'
                },
                'password': {
                    'type': 'string',
                    'description': 'Senha do usuário'
                }
            },
            'example': {
                'email': 'joao@exemplo.com',
                'password': 'senha123'
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Login bem-sucedido',
            'examples': {
                'application/json': {
                    'mensagem': 'Login bem-sucedido',
                    'token': 'exemplo_de_token_gerado_aqui'
                }
            }
        },
        '401': {
            'description': 'Credenciais inválidas',
            'examples': {
                'application/json': {'erro': 'Credenciais inválidas'}
            }
        }
    }
})
def login():
    dados = request.json
    print('Dados recebidos:', dados)
    
    email = dados.get('email') if dados else None
    senha = dados.get('password') if dados else None

    if not email or not senha:
        return jsonify({'erro': 'Campos "email" e "password" são obrigatórios'}), 400

    usuario = UsuarioService.login(email, senha)
    print('Usuário encontrado:', usuario)

    if not usuario:
        return jsonify({'erro': 'Credenciais inválidas'}), 401

    if not isinstance(usuario, dict) or not all(key in usuario for key in ['id', 'name', 'email']):
        return jsonify({'erro': 'Erro no formato dos dados retornados'}), 500

    try:
        token = AuthService.gerar_token(usuario['id'])
    except Exception as e:
        return jsonify({'erro': f'Erro ao gerar o token: {str(e)}'}), 500

    return jsonify({
        'mensagem': 'Login bem-sucedido',
        'token': token
    }), 200


@usuarios_bp.route('/usuarios', methods=['GET'])
@token_required
@swag_from({
    'tags': ['Usuários'],
    'description': 'Retorna os dados do usuário logado com o board e tarefas associados',
    'security': [{'Bearer': []}],
    'responses': {
        '200': {
            'description': 'Usuário encontrado com board, tarefas e labels associadas',
            'examples': {
                'application/json': {
                    'usuario': {
                        'id': 1, 
                        'name': 'João', 
                        'email': 'joao@exemplo.com', 
                        'board': {
                            'id': 1, 
                            'name': 'Meu Board Padrão',
                            'tarefas': [
                                {'id': 1, 'title': 'Tarefa 1', 'description': '...', 'status': 'toDo', 'labels': [{'id': 1, 'name': 'Urgente', 'hex_color': '#FF0000'}]},
                                {'id': 2, 'title': 'Tarefa 2', 'description': '...', 'status': 'doing', 'labels': []}
                            ]
                        },
                        'labels': [{'id': 1, 'name': 'Urgente', 'hex_color': '#FF0000'}, {'id': 2, 'name': 'Pessoal', 'hex_color': '#00FF00'}]
                    }
                }
            }
        },
        '404': {
            'description': 'Usuário ou board não encontrado',
            'examples': {
                'application/json': {'erro': 'Usuário ou board não encontrado'}
            }
        },
        '401': {
            'description': 'Token ausente ou inválido',
            'examples': {
                'application/json': {'erro': 'Token de autenticação não fornecido'}
            }
        }
    }
})

def buscar_usuario_logado(user_id):
    usuario = UsuarioService.buscar_usuario_por_id(user_id)

    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404

    board_com_tarefas = BoardService.buscar_board_com_tarefas_por_usuario(user_id)

    if not board_com_tarefas:
        return jsonify({'erro': 'Board não encontrado'}), 404

    # Buscar as labels do usuário usando LabelService (já retorna os detalhes completos)
    labels = LabelService.buscar_labels_por_usuario(user_id)

    usuario_dict = {
            'id': usuario['id'],
            'name': usuario['name'],
            'email': usuario['email'],
            'board': board_com_tarefas,
            'labels': labels # Agora inclui ID, nome e hex_color
        }

    return jsonify({'usuario': usuario_dict}), 200

@usuarios_bp.route('/usuarios/todos', methods=['GET'])
@swag_from({
    'tags': ['Usuários'],
    'description': 'Retorna todos os usuários registrados com seus boards, tarefas e labels associados.',
    'responses': {
        '200': {
            'description': 'Lista de todos os usuários detalhada',
            'examples': {
                'application/json': [
                    {
                        'id': 1,
                        'name': 'João',
                        'email': 'joao@exemplo.com',
                        'board': {
                            'id': 1,
                            'name': 'Meu Board Padrão',
                            'tarefas': [
                                {'user_task_id': 1, 'title': 'Tarefa A', 'description': '...', 'status': 'toDo', 'labels': [{'id': 1, 'name': 'Urgente', 'hex_color': '#FF0000'}]},
                                {'user_task_id': 2, 'title': 'Tarefa B', 'description': '...', 'status': 'doing', 'labels': []}
                            ]
                        },
                        'labels': [{'id': 1, 'name': 'Prioridade', 'hex_color': '#FF0000'}]
                    },
                    {
                        'id': 2,
                        'name': 'Maria',
                        'email': 'maria@exemplo.com',
                        'board': {
                            'id': 2,
                            'name': 'Board da Maria',
                            'tarefas': []
                        },
                        'labels': []
                    }
                ]
            }
        },
        '404': {
            'description': 'Nenhum usuário encontrado',
            'examples': {
                'application/json': {'mensagem': 'Nenhum usuário encontrado!'}
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
def buscar_todos_usuarios():
    try:
        # Este método precisaria ser adaptado no UsuarioService para buscar todos os detalhes,
        # incluindo labels detalhadas para cada usuário.
        # Por enquanto, vou manter a chamada existente e apenas atualizar o exemplo do Swagger.
        usuarios = UsuarioService.buscar_todos_usuarios_detalhado() # Manter esta chamada
        if usuarios:
            return jsonify(usuarios), 200
        else:
            return jsonify({"mensagem": "Nenhum usuário encontrado!"}), 404
    except Exception as e:
        print(f"Erro ao buscar todos os usuários: {e}")
        return jsonify({"erro": "Erro interno do servidor!"}), 500