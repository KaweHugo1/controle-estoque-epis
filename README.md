# Controle de Estoque e EPIs

Sistema para controle de materiais e EPIs, com registro de retiradas por funcionário
e gestão de demandas de serviço. Possui API em **Python (FastAPI)**, banco **SQLite**
e tela web em **HTML, CSS e JavaScript**.

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate        # Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

- Tela web: http://127.0.0.1:8000
- Documentação interativa da API: http://127.0.0.1:8000/docs

Dados de exemplo (opcional), depois de rodar a API uma vez:

```bash
python -c "import sqlite3; c=sqlite3.connect('estoque.db'); c.executescript(open('seed.sql', encoding='utf-8').read()); c.commit()"
```

## Funcionalidades

- Cadastro de materiais e EPIs (com número do CA)
- Cadastro de funcionários
- Registro de entrada, retirada e devolução, informando quem pegou e para qual demanda
- Demandas de serviço com acompanhamento de status
- Alerta de estoque baixo
- Histórico de movimentações com filtros por funcionário, item e demanda

## Rotas principais

| Método | Rota | Descrição |
|---|---|---|
| POST/GET | `/funcionarios` | Cadastrar e listar funcionários |
| POST/GET | `/itens` | Cadastrar e listar materiais e EPIs |
| GET | `/itens/estoque-baixo` | Itens abaixo do estoque mínimo |
| POST/GET | `/demandas` | Criar e listar demandas de serviço |
| PATCH | `/demandas/{id}/status` | Atualizar o status da demanda |
| POST | `/movimentacoes` | Registrar entrada, retirada ou devolução |
| GET | `/movimentacoes` | Histórico (filtros: funcionário, item, demanda) |

## Regras de negócio (garantidas pelo banco)

- Não permite retirar mais do que existe em estoque
- Toda retirada exige um funcionário
- O estoque é atualizado automaticamente a cada movimentação

## Estrutura do projeto

```
main.py            rotas da API
schemas.py         modelos de entrada e saída
database.py        conexão com o SQLite
schema.sql         tabelas, triggers e views
seed.sql           dados de exemplo
static/index.html  tela web
```

## Tecnologias

Python · FastAPI · SQLite · SQL (triggers e views) · HTML, CSS e JavaScript
