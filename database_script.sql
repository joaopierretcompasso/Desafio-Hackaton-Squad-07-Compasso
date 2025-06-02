
CREATE DATABASE empresa;

-- Criação das tabelas
CREATE TABLE departamentos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    localizacao VARCHAR(100) NOT NULL
);

CREATE TABLE funcionarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cargo VARCHAR(100) NOT NULL,
    salario DECIMAL(10, 2) NOT NULL,
    ativo BOOLEAN NOT NULL,
    departamento_id INT REFERENCES departamentos(id)
);

CREATE TABLE projetos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    departamento_id INT REFERENCES departamentos(id)
);

CREATE TABLE alocacoes (
    id SERIAL PRIMARY KEY,
    funcionario_id INT REFERENCES funcionarios(id),
    projeto_id INT REFERENCES projetos(id),
    horas_semanais INT NOT NULL
);

CREATE TABLE avaliacoes (
    id SERIAL PRIMARY KEY,
    funcionario_id INT REFERENCES funcionarios(id),
    projeto_id INT REFERENCES projetos(id),
    nota INT NOT NULL,
    comentario TEXT
);

-- Inserção de dados nas tabelas
INSERT INTO departamentos (nome, localizacao) VALUES
('Recursos Humanos', 'São Paulo'),
('Desenvolvimento', 'Rio de Janeiro'),
('Marketing', 'Curitiba');

INSERT INTO funcionarios (nome, cargo, salario, ativo, departamento_id) VALUES
('Alice', 'Analista', 5000.00, TRUE, 1),
('Bob', 'Desenvolvedor', 7000.00, TRUE, 2),
('Carlos', 'Gerente', 9000.00, TRUE, 1),
('Diana', 'Desenvolvedor', 6500.00, TRUE, 2),
('Eva', 'Analista', 4800.00, FALSE, 3);

INSERT INTO projetos (nome, descricao, departamento_id) VALUES
('Projeto Alpha', 'Desenvolvimento de sistema X', 2),
('Projeto Beta', 'Campanha de marketing Y', 3),
('Projeto Gamma', 'Reestruturação de RH', 1);

INSERT INTO alocacoes (funcionario_id, projeto_id, horas_semanais) VALUES
(1, 3, 20),
(2, 1, 30),
(3, 3, 10),
(4, 1, 25),
(5, 2, 15);

INSERT INTO avaliacoes (funcionario_id, projeto_id, nota, comentario) VALUES
(1, 3, 8, 'Bom desempenho'),
(2, 1, 9, 'Excelente trabalho'),
(3, 3, 7, 'Precisa melhorar'),
(4, 1, 8, 'Bom desempenho'),
(5, 2, 6, 'Desempenho razoável');
