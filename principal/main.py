from tradutorPySpark import ConverterPySpark
from tradutorSparkSQL import ConverterSparkSQL

def processar_query(query_sql):
    # Converte para SparkSQL
    conversor_sparksql = ConverterSparkSQL(query_sql)
    spark_sql = conversor_sparksql.tradutor()

    # Converte para PySpark
    conversor_pyspark = ConverterPySpark(query_sql)
    pyspark = conversor_pyspark.tradutor()

    return spark_sql, pyspark

def main():
    query_sql = """
    WITH cte AS (SELECT id FROM tabela)
    FROM t1
    JOIN t2 ON t1.id = t2.id
    GROUP BY t1.col1
    HAVING COUNT(t2.col2) > 10
    ORDER BY t1.col1 DESC
    LIMIT 5"""

    spark_sql, pyspark = processar_query(query_sql)

    print("=" * 50)
    print("Query SQL Original:")
    print("=" * 50)
    print(query_sql)

    print("=" * 50)
    print("Query SQL Convertida para SparkSQL:")
    print("=" * 50)
    print(spark_sql)

    print("=" * 50)
    print("Query SQL Convertida para PySpark:")
    print("=" * 50)
    print(pyspark)

if __name__ == "__main__":
    main()