# API To-Do Kanban

Esta é a documentação para rodar a API do sistema To-Do Kanban localmente.

## Visão Geral

A API To-Do Kanban permite a gestão de usuários, boards, tarefas e labels associadas.

## Requisitos

Para rodar esta aplicação, você precisará ter instalado:

* Python 3.x
* Pip (gerenciador de pacotes do Python)

## Configuração do Ambiente

Siga os passos abaixo para configurar e rodar a API:

### 1. Clonar o Repositório (se aplicável)

Se o seu código estiver em um repositório Git, clone-o para a sua máquina local:

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd <nome_da_pasta_do_projeto>
```
### 2. Criar e Ativar um Ambiente Virtual

É uma boa prática criar um ambiente virtual para isolar as dependências do projeto. No seu terminal, execute:

#### No Windows:

```bash
python -m venv venv
.\venv\Scripts\activate
```

### No macOs/Linux
```
python -m venv venv
source venv/bin/activate
```
### 3. Instale as dependências

```
pip install Flask Flask-Cors PyJWT flasgger
```

## Se tiver requeriments.py
```
pip install -r requirements.txt
```

# To-do-kanban-Frontend

Aplicação frontend do sistema To-Do Kanban.

## Requisitos

Antes de iniciar, certifique-se de ter instalado em sua máquina:

- [Node.js](https://nodejs.org/)  
- [npm](https://www.npmjs.com/) (gerenciador de pacotes que já vem com o Node)  
- [Yarn](https://yarnpkg.com/) (opcional, mas recomendado)

## Configuração do Ambiente

Siga os passos abaixo para rodar o projeto localmente:

### 1. Clonar o Repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd to-do-kanban-frontend
cd app-vue
```

## Rode o comando para baixar as dependências
``` 
yarn install
```

