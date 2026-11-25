# Controle de Estoque e EPIs

API em **Python (FastAPI)** com banco **SQLite** para controle de materiais e EPIs,
registro de retiradas por funcionário e gestão de demandas de serviço.

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Abra http://127.0.0.1:8000/docs para testar todas as rotas.

Dados de exemplo (opcional), depois de rodar a API uma vez:

```bash
python -c "import sqlite3; c=sqlite3.connect('estoque.db'); c.executescript(open('seed.sql', encoding='utf-8').read()); c.commit()"
```

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

## Tecnologias

Python · FastAPI · SQLite · SQL (triggers e views)
