import pytest
import sys
import os
from pathlib import Path

# Adiciona o diretório principal ao path para importar o módulo
sys.path.append(str(Path(__file__).parent.parent))

from principal.tradutorPySpark import ConverterPySpark

@pytest.fixture
def consulta_simples():
    """Fixture que fornece uma consulta SQL simples."""
    return "SELECT nome, idade FROM usuarios WHERE idade > 18"

@pytest.fixture
def consulta_com_join():
    """Fixture que fornece uma consulta SQL com JOIN."""
    return """
    SELECT u.nome, p.valor
    FROM usuarios u
    JOIN pedidos p ON u.id = p.usuario_id
    WHERE p.valor > 100
    """

@pytest.fixture
def consulta_com_group_by():
    """Fixture que fornece uma consulta SQL com GROUP BY e funções de agregação."""
    return """
    SELECT categoria, COUNT(*) as total, AVG(valor) as media
    FROM produtos
    GROUP BY categoria
    HAVING COUNT(*) > 5
    """

@pytest.fixture
def consulta_com_order_limit():
    """Fixture que fornece uma consulta SQL com ORDER BY e LIMIT."""
    return """
    SELECT nome, preco
    FROM produtos
    WHERE estoque > 0
    ORDER BY preco DESC
    LIMIT 10
    """

@pytest.fixture
def consulta_com_cte():
    """Fixture que fornece uma consulta SQL com Common Table Expression (CTE)."""
    return """
    WITH produtos_caros AS (
        SELECT id, nome, preco 
        FROM produtos 
        WHERE preco > 1000
    )
    SELECT p.nome, p.preco 
    FROM produtos_caros p
    ORDER BY p.preco DESC
    """

def test_tradutor_consulta_simples(consulta_simples):
    """Testa a tradução de uma consulta SQL simples para PySpark."""
    conversor = ConverterPySpark(consulta_simples)
    resultado = conversor.tradutor()
    
    # Verifica se o resultado é uma string
    assert isinstance(resultado, str), "O resultado deve ser uma string"
    
    # Verifica se o resultado contém spark.table
    assert 'spark.table(' in resultado, "O resultado deve conter spark.table"
    
    # Verifica se contém o método select
    assert '.select(' in resultado, "O resultado deve conter o método select"
    
    # Verifica se os campos estão presentes no resultado
    assert 'nome' in resultado, "O resultado deve incluir o campo nome"
    assert 'idade' in resultado, "O resultado deve incluir o campo idade"

def test_tradutor_com_join(consulta_com_join):
    """Testa a tradução de uma consulta SQL com JOIN para PySpark."""
    conversor = ConverterPySpark(consulta_com_join)
    resultado = conversor.tradutor()
    
    # Verifica se o resultado contém o método join
    assert '.join(' in resultado, "O resultado deve conter o método join"
    
    # Verifica se contém o método select
    assert '.select(' in resultado, "O resultado deve conter o método select"
    
    # Verifica se os campos estão presentes no resultado
    assert 'u.nome' in resultado, "O resultado deve incluir o campo u.nome"
    assert 'p.valor' in resultado, "O resultado deve incluir o campo p.valor"

def test_tradutor_com_group_by(consulta_com_group_by):
    """Testa a tradução de uma consulta SQL com GROUP BY para PySpark."""
    conversor = ConverterPySpark(consulta_com_group_by)
    resultado = conversor.tradutor()
    
    # Verifica se o resultado contém o método groupBy
    assert '.groupBy(' in resultado, "O resultado deve conter o método groupBy"
    
    # Verifica se contém o método agg para as funções de agregação
    assert '.agg(' in resultado, "O resultado deve conter o método agg para as funções de agregação"
    
    # Verifica se as funções de agregação estão presentes
    assert 'COUNT(*)' in resultado, "O resultado deve conter a expressão COUNT(*)"
    assert 'AVG(valor)' in resultado, "O resultado deve conter a expressão AVG(valor)"

def test_tradutor_com_order_limit(consulta_com_order_limit):
    """Testa a tradução de uma consulta SQL com ORDER BY e LIMIT para PySpark."""
    conversor = ConverterPySpark(consulta_com_order_limit)
    resultado = conversor.tradutor()
    
    # Verifica se o resultado é uma string
    assert isinstance(resultado, str), "O resultado deve ser uma string"
    
    # Verifica se o resultado contém spark.table
    assert 'spark.table(' in resultado, "O resultado deve conter spark.table"
    
    # Verifica se contém o método orderBy
    assert '.orderBy(' in resultado, "O resultado deve conter o método orderBy"
    
    # Verifica se contém o método limit
    assert '.limit(' in resultado, "O resultado deve conter o método limit"

def test_tradutor_com_cte(consulta_com_cte):
    """Testa a tradução de uma consulta SQL com CTE para PySpark."""
    conversor = ConverterPySpark(consulta_com_cte)
    resultado = conversor.tradutor()
    
    # Verifica se o resultado é uma string
    assert isinstance(resultado, str), "O resultado deve ser uma string"
    
    # Verifica se o resultado contém spark.table
    assert 'spark.table(' in resultado, "O resultado deve conter spark.table"
    
    # Verifica se contém o método orderBy
    assert '.orderBy(' in resultado, "O resultado deve conter o método orderBy"
    
    # Verifica se contém o método select
    assert '.select(' in resultado, "O resultado deve conter o método select"

def test_extrai_ctes(consulta_com_cte):
    """Testa se as CTEs são extraídas corretamente."""
    conversor = ConverterPySpark(consulta_com_cte)
    
    # Verifica se o dicionário de CTEs existe
    assert hasattr(conversor, 'ctes'), "O conversor deve ter um atributo 'ctes'"
    
    # Verifica se o método extrai_ctes existe
    assert hasattr(conversor, 'extrai_ctes'), "O conversor deve ter um método 'extrai_ctes'"
    
    # Verifica se a CTE foi extraída
    assert len(conversor.ctes) > 0, "Pelo menos uma CTE deve ser extraída da consulta"
    
    # Verifica se o primeiro objeto CTE é uma instância de ConverterPySpark
    cte_name = list(conversor.ctes.keys())[0]
    assert isinstance(conversor.ctes[cte_name], ConverterPySpark), "A CTE extraída deve ser uma instância de ConverterPySpark"

def test_gerador_alias():
    """Testa se o gerador de alias cria aliases únicos."""
    conversor = ConverterPySpark("SELECT * FROM tabela")
    
    alias1 = conversor.gerador_alias()
    alias2 = conversor.gerador_alias()
    
    # Verifica se os aliases são diferentes
    assert alias1 != alias2, "Os aliases gerados devem ser únicos e diferentes entre si"
    
    # Verifica o formato dos aliases
    assert alias1.startswith('subquery_'), "O alias deve começar com o prefixo 'subquery_'"
    assert alias2.startswith('subquery_'), "O alias deve começar com o prefixo 'subquery_'"