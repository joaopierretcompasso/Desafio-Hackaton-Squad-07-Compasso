document.addEventListener('DOMContentLoaded', function() {
    // Elementos da interface
    const sqlInput = document.getElementById('sql-input');
    const fileInput = document.getElementById('file-input');
    const loadFileBtn = document.getElementById('load-file-btn');
    const clearBtn = document.getElementById('clear-btn');
    const convertBtn = document.getElementById('convert-btn');
    const sparkSqlOutput = document.getElementById('spark-sql-output');
    const pysparkOutput = document.getElementById('pyspark-output');
    const statusBar = document.getElementById('status-bar');
    
    // Exemplo de consulta SQL válida
    sqlInput.placeholder = "Digite sua consulta SQL aqui ou carregue um arquivo...\n\nExemplo:\nSELECT coluna1, coluna2\nFROM tabela\nWHERE condição";

    // Evento para carregar arquivo
    loadFileBtn.addEventListener('click', function() {
        fileInput.click();
    });

    // Evento quando um arquivo é selecionado
    fileInput.addEventListener('change', function(e) {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            const reader = new FileReader();
            
            reader.onload = function(e) {
                sqlInput.value = e.target.result;
                updateStatus(`Arquivo carregado: ${file.name}`, 'normal');
            };
            
            reader.onerror = function() {
                updateStatus('Erro ao ler o arquivo', 'error');
            };
            
            reader.readAsText(file);
        }
    });

    // Evento para limpar a entrada
    clearBtn.addEventListener('click', function() {
        sqlInput.value = '';
        sparkSqlOutput.textContent = '';
        pysparkOutput.textContent = '';
        fileInput.value = '';
        updateStatus('Entrada limpa', 'normal');
        hljs.highlightAll();
    });

    // Evento para converter SQL
    convertBtn.addEventListener('click', function() {
        const sqlQuery = sqlInput.value.trim();
        
        if (!sqlQuery) {
            updateStatus('Erro: Nenhuma consulta SQL fornecida', 'error');
            return;
        }
        
        updateStatus('Convertendo...', 'normal');
        
        // Preparar dados para envio
        const formData = new FormData();
        
        // Se tiver um arquivo selecionado, envie o arquivo
        if (fileInput.files && fileInput.files[0]) {
            formData.append('file', fileInput.files[0]);
        } else {
            // Caso contrário, envie o texto do textarea
            formData.append('sql_text', sqlQuery);
        }
        
        // Enviar requisição para o servidor
        fetch('/convert', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na requisição');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Exibir resultados
            sparkSqlOutput.textContent = data.spark_sql;
            pysparkOutput.textContent = data.pyspark;
            
            // Aplicar highlight de sintaxe
            hljs.highlightAll();
            
            updateStatus('Conversão concluída com sucesso', 'success');
        })
        .catch(error => {
            updateStatus(`Erro: ${error.message}`, 'error');
            console.error('Erro:', error);
        });
    });

    // Função para atualizar a barra de status
    function updateStatus(message, type = 'normal') {
        statusBar.textContent = message;
        
        // Remover classes anteriores
        statusBar.classList.remove('error', 'success');
        
        // Adicionar classe apropriada
        if (type === 'error') {
            statusBar.classList.add('error');
        } else if (type === 'success') {
            statusBar.classList.add('success');
        }
    }
    
    // Adicionar exemplo de consulta SQL válida
    document.getElementById('sql-input').value = `SELECT t1.col1, COUNT(t2.col2) as count
FROM t1
JOIN t2 ON t1.id = t2.id
GROUP BY t1.col1
HAVING COUNT(t2.col2) > 10
ORDER BY t1.col1 DESC
LIMIT 5`;

    // Inicializar highlight.js
    hljs.highlightAll();
});