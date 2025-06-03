from flask import Flask, request, jsonify, render_template
from main import processar_query
import os
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                sql_query = file.read().decode('utf-8')
            else:
                sql_query = request.form.get('sql_text', '')
        else:
            sql_query = request.form.get('sql_text', '')
        
        if not sql_query:
            return jsonify({'error': 'Nenhuma consulta SQL fornecida'}), 400
        
        if not re.search(r'^\s*SELECT\s+', sql_query, re.IGNORECASE):
            return jsonify({
                'error': 'A consulta SQL deve começar com SELECT',
                'original_query': sql_query
            }), 400
        
        spark_sql, pyspark = processar_query(sql_query)
        
        if pyspark.startswith("# Erro:"):
            return jsonify({
                'error': pyspark.replace("# Erro: ", ""),
                'spark_sql': spark_sql,
                'pyspark': pyspark,
                'original_query': sql_query
            }), 400
        
        return jsonify({
            'spark_sql': spark_sql,
            'pyspark': pyspark,
            'original_query': sql_query
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    if not os.path.exists('static'):
        os.makedirs('static')
        
    app.run(debug=True)