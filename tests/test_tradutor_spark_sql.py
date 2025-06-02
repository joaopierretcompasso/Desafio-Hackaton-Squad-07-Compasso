import pytest
import sys
import os
from pathlib import Path

# Adiciona o diretório principal ao path para importar o módulo
sys.path.append(str(Path(__file__).parent.parent))

from principal.tradutorSparkSQL import ConverterSparkSQL

@pytest.fixture
def consulta_simples():
    """Fixture que fornece uma consulta SQL simples."""
    return "SELECT nome, idade FROM usuarios WHERE idade > 18"

@pytest.fixture
def consulta_com_funcoes():
    """Fixture que fornece uma consulta SQL com funções que precisam ser convertidas."""
    return "SELECT nome, NVL(email, 'sem email') FROM usuarios WHERE data_registro > SYSDATE - 30"

@pytest.fixture
def consulta_com_cte():
    """Fixture que fornece uma consulta SQL com Common Table Expression (CTE)."""
    return """
    WITH usuarios_ativos AS (
        SELECT id, nome, email 
        FROM usuarios 
        WHERE status = 'ativo'
    )
    SELECT u.nome, u.email 
    FROM usuarios_ativos u
    JOIN pedidos p ON u.id = p.usuario_id
    """

@pytest.fixture
def consulta_com_subquery():
    """Fixture que fornece uma consulta SQL com subquery."""
    return """
    SELECT nome, email
    FROM usuarios
    WHERE id IN (SELECT usuario_id FROM pedidos WHERE valor > 1000)
    """

def test_tradutor_consulta_simples(consulta_simples):
    """Testa a tradução de uma consulta SQL simples."""
    conversor = ConverterSparkSQL(consulta_simples)
    resultado = conversor.tradutor()
    
    # Verifica se o resultado é uma string
    assert isinstance(resultado, str), "O resultado deve ser uma string"
    
    # Verifica se o resultado começa com spark.sql
    assert resultado.startswith('spark.sql('), "O resultado deve começar com spark.sql("
    assert resultado.endswith(')'), "O resultado deve terminar com ) para formar uma consulta Spark válida"

def test_tradutor_funcoes_substituidas(consulta_com_funcoes):
    """Testa se as funções incompatíveis são substituídas corretamente."""
    conversor = ConverterSparkSQL(consulta_com_funcoes)
    resultado = conversor.tradutor()
    
    # Verifica se o resultado é uma string
    assert isinstance(resultado, str), "O resultado deve ser uma string"
    
    # Verifica se o resultado contém spark.sql
    assert resultado.startswith('spark.sql('), "O resultado deve começar com spark.sql("
    
    # Verifica se NVL foi substituído por COALESCE (case insensitive)
    assert 'NVL' not in resultado.upper(), "A função NVL deve ser substituída e não deve aparecer no resultado"
    assert 'COALESCE' in resultado.upper(), "A função NVL deve ser substituída por COALESCE no resultado"
    
    # Verifica se SYSDATE foi substituído por CURRENT_DATE() (case insensitive)
    assert 'SYSDATE' not in resultado.upper(), "A função SYSDATE deve ser substituída e não deve aparecer no resultado"
    assert 'CURRENT_DATE()' in resultado.upper(), "A função SYSDATE deve ser substituída por CURRENT_DATE() no resultado"

def test_extrai_ctes(consulta_com_cte):
    """Testa se as CTEs são extraídas corretamente."""
    conversor = ConverterSparkSQL(consulta_com_cte)
    
    # Verifica se o dicionário de CTEs existe
    assert hasattr(conversor, 'ctes'), "O conversor deve ter um atributo 'ctes'"
    
    # Verifica se o método extrai_ctes existe
    assert hasattr(conversor, 'extrai_ctes'), "O conversor deve ter um método 'extrai_ctes'"
    
    # Verifica se a CTE foi extraída
    assert len(conversor.ctes) > 0, "Pelo menos uma CTE deve ser extraída da consulta"
    
    # Verifica se o primeiro objeto CTE é uma instância de ConverterSparkSQL
    cte_name = list(conversor.ctes.keys())[0]
    assert isinstance(conversor.ctes[cte_name], ConverterSparkSQL), "A CTE extraída deve ser uma instância de ConverterSparkSQL"

def test_tradutor_com_cte(consulta_com_cte):
    """Testa a tradução de uma consulta com CTE."""
    conversor = ConverterSparkSQL(consulta_com_cte)
    resultado = conversor.tradutor()
    
    # Verifica se o resultado é uma string
    assert isinstance(resultado, str), "O resultado deve ser uma string"
    
    # Verifica se o resultado contém spark.sql
    assert resultado.startswith('spark.sql('), "O resultado deve começar com spark.sql("
    
    # Verifica se o resultado contém a definição da CTE (case insensitive)
    assert 'WITH' in resultado.upper(), "O resultado deve conter a palavra-chave WITH"
    assert 'AS' in resultado.upper(), "O resultado deve conter a palavra-chave AS para definição de CTE"

def test_tradutor_com_subquery(consulta_com_subquery):
    """Testa a tradução de uma consulta com subquery."""
    conversor = ConverterSparkSQL(consulta_com_subquery)
    resultado = conversor.tradutor()
    
    # Verifica se o resultado é uma string
    assert isinstance(resultado, str), "O resultado deve ser uma string"
    
    # Verifica se o resultado contém spark.sql
    assert resultado.startswith('spark.sql('), "O resultado deve começar com spark.sql("
    
    # Verifica se a subquery está presente no resultado (verificando partes essenciais)
    assert 'IN' in resultado.upper(), "A consulta deve conter a palavra-chave IN"
    assert 'SELECT' in resultado.upper(), "A consulta deve conter a palavra-chave SELECT"
    assert 'usuario_id' in resultado.lower(), "A subconsulta deve conter o campo usuario_id"
    assert 'pedidos' in resultado.lower(), "A subconsulta deve conter a tabela pedidos"
    assert 'valor > 1000' in resultado, "A subconsulta deve conter a condição valor > 1000"

def test_gerador_alias():
    """Testa se o gerador de alias cria aliases únicos."""
    conversor = ConverterSparkSQL("SELECT * FROM tabela")
    
    alias1 = conversor.gerador_alias()
    alias2 = conversor.gerador_alias()
    
    # Verifica se os aliases são diferentes
    assert alias1 != alias2, "Os aliases gerados devem ser únicos e diferentes entre si"
    
    # Verifica o formato dos aliases
    assert alias1.startswith('subquery_'), "O alias deve começar com o prefixo 'subquery_'"
    assert alias2.startswith('subquery_'), "O alias deve começar com o prefixo 'subquery_'"

def test_multiplas_substituicoes():
    """Testa múltiplas substituições em uma única consulta."""
    consulta = "SELECT NVL(nome, 'Desconhecido'), TRUNC(data), TO_DATE(texto, 'YYYY-MM-DD') FROM tabela WHERE data > SYSDATE"
    conversor = ConverterSparkSQL(consulta)
    resultado = conversor.tradutor()
    
    # Verifica se o resultado é uma string
    assert isinstance(resultado, str), "O resultado deve ser uma string"
    
    # Verifica se o resultado contém spark.sql
    assert resultado.startswith('spark.sql('), "O resultado deve começar com spark.sql("
    
    # Verifica todas as substituições (case insensitive)
    assert 'NVL' not in resultado.upper(), "A função NVL deve ser substituída no resultado"
    assert 'COALESCE' in resultado.upper(), "A função NVL deve ser substituída por COALESCE"
    assert 'SYSDATE' not in resultado.upper(), "A função SYSDATE deve ser substituída no resultado"
    assert 'CURRENT_DATE()' in resultado.upper(), "A função SYSDATE deve ser substituída por CURRENT_DATE()"
    assert 'TO_DATE' in resultado.upper(), "A função TO_DATE deve ser mantida no resultado"