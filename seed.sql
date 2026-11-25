-- Dados de exemplo (opcional): sqlite3 estoque.db < seed.sql
PRAGMA foreign_keys = ON;
INSERT INTO funcionarios (nome, matricula, setor) VALUES
    ('ALlberto Santos', '88003', 'auxiliar'),
    ('Ana Souza',    '988001', 'Operador');

INSERT INTO itens (nome, tipo, unidade, estoque_minimo, ca) VALUES
    ('Luva de raspa',       'EPI',      'par', 10, '01001'),
    ('Capacete de proteção','EPI',      'un',   5, '01002'),
    ('Parafuso 10mm',       'MATERIAL', 'un',  50, NULL);

INSERT INTO movimentacoes (item_id, tipo, quantidade, observacao) VALUES
    (1, 'ENTRADA', 30, 'Compra inicial'),
    (2, 'ENTRADA', 8,  'Compra inicial'),
    (3, 'ENTRADA', 200,'Compra inicial');

INSERT INTO demandas (titulo, descricao, responsavel_id) VALUES
    ('Troca de correia da esteira', 'Manutenção preventiva', 1);

INSERT INTO movimentacoes (item_id, funcionario_id, demanda_id, tipo, quantidade) VALUES
    (1, 1, 1, 'RETIRADA', 2),
    (3, 1, 1, 'RETIRADA', 20);
