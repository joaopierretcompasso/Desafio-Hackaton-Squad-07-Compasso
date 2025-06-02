# 🚀 SparkMigrator

O **SparkMigrator** é uma ferramenta desenvolvida em Python que lê queries SQL, interpreta seus componentes (como SELECT, WHERE, FROM) e transforma essas consultas em comandos PySpark ou SparkSQL.

Ele é ideal para ajudar na **migração de sistemas que usam SQL tradicional para ambientes com Spark**, facilitando o trabalho de analistas de dados, engenheiros e cientistas de dados.

---

## 📌 Objetivo

Transformar consultas SQL simples em:

- **Código PySpark**
- **Consultas Spark SQL**
- **Saídas em arquivos CSV**

---

## 🧠 Como Funciona

1. 📥 **Entrada**: o usuário fornece um arquivo `.sql` com a consulta desejada.
2. 🔍 **Interpretação**: o programa usa a biblioteca `sqlparse` para dividir a consulta em partes (SELECT, WHERE, etc).
3. ⚙️ **Tradução**: a consulta é convertida para uma estrutura interna Python.
4. 🧪 **Geração**: o programa gera código PySpark ou Spark SQL a partir da estrutura interna.
5. 💾 **Saída**: os dados processados são salvos em arquivos `.csv`.

---

## 🗂️ Estrutura do Projeto

sparkMigrator/
├── src/
│ ├── leitura_sql/ # Código que entende SQL
│ ├── tradutor/ # Código que gera PySpark ou Spark SQL
│ └── cli/ # Código da interface de terminal
├── tests/ # Testes automáticos (pytest)
│ ├── test_leitura_sql.py
│ ├── test_tradutor.py
│ └── test_dados_csv.py
├── dados/ # Arquivos CSV simulados (ex: funcionarios.csv)
├── main.py # Ponto de entrada do programa
├── requirements.txt # Dependências do projeto
└── README.md # Este arquivo



---

## 🧪 Como Rodar os Testes

1. Instale as dependências:
```bash
pip install -r requirements.txt

🛠️ Tecnologias Usadas
Python 3.10+

PySpark

Pandas

SQLParse

Jinja2

Argparse

Pytest


📝 Exemplo de Uso

python main.py --input exemplo.sql


📚 Como Contribuir
Se quiser colaborar com este projeto:

Faça um fork

Crie uma branch: git checkout -b minha-contribuicao

Commit suas alterações: git commit -m 'Minha melhoria'

Envie um push: git push origin minha-contribuicao

Abra um pull request 🧡

👨‍💻 Autoria
Este projeto foi desenvolvido por Squad 7 - Hackaton com o objetivo de explorar soluções de migração de SQL para Spark com foco em aprendizado prático, testes e automação.

#não gerei a licença 
