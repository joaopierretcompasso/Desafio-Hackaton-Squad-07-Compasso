from tradutorPySpark import ConverterPySpark

# Query de teste
query_sql = """
SELECT nome, salario 
FROM funcionarios 
WHERE salario > 5000 
ORDER BY salario DESC;
"""

# Converter para PySpark
conversor = ConverterPySpark(query_sql)
resultado = conversor.tradutor()

print("Query SQL Original:")
print(query_sql)
print("\nResultado PySpark:")
print(resultado)

# Imprimir as cláusulas extraídas para debug
clausulas = conversor.extrai_clausulas()
print("\nCláusulas extraídas:")
for nome, tokens in clausulas.items():
    if tokens:
        print(f"{nome}: {[t.value for t in tokens]}")