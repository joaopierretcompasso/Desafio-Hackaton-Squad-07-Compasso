import tkinter as tk
from tkinter import scrolledtext
from main import processar_query

class SQLConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor SQL para SparkSQL e PySpark")
        self.root.geometry("800x600")
        
        # Frame para entrada SQL
        input_frame = tk.Frame(root)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(input_frame, text="Digite sua query SQL:").pack(anchor=tk.W)
        
        self.sql_input = scrolledtext.ScrolledText(input_frame, height=10)
        self.sql_input.pack(fill=tk.BOTH, expand=True)
        
        # Botão para processar
        process_button = tk.Button(root, text="Converter", command=self.converter_sql)
        process_button.pack(pady=10)
        
        # Frame para saídas
        output_frame = tk.Frame(root)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para SparkSQL
        spark_sql_frame = tk.Frame(output_frame)
        spark_sql_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 5))
        
        tk.Label(spark_sql_frame, text="SparkSQL:").pack(anchor=tk.W)
        self.spark_sql_output = scrolledtext.ScrolledText(spark_sql_frame)
        self.spark_sql_output.pack(fill=tk.BOTH, expand=True)
        
        # Frame para PySpark
        pyspark_frame = tk.Frame(output_frame)
        pyspark_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=(5, 0))
        
        tk.Label(pyspark_frame, text="PySpark:").pack(anchor=tk.W)
        self.pyspark_output = scrolledtext.ScrolledText(pyspark_frame)
        self.pyspark_output.pack(fill=tk.BOTH, expand=True)
    
    def converter_sql(self):
        # Limpar saídas anteriores
        self.spark_sql_output.delete(1.0, tk.END)
        self.pyspark_output.delete(1.0, tk.END)
        
        # Obter a query SQL da entrada
        query_sql = self.sql_input.get(1.0, tk.END).strip()
        
        if not query_sql:
            self.spark_sql_output.insert(tk.END, "Por favor, insira uma query SQL.")
            self.pyspark_output.insert(tk.END, "Por favor, insira uma query SQL.")
            return
        
        try:
            # Processar a query usando a função existente
            spark_sql, pyspark = processar_query(query_sql)
            
            # Exibir resultados
            self.spark_sql_output.insert(tk.END, spark_sql)
            self.pyspark_output.insert(tk.END, pyspark)
        except Exception as e:
            error_msg = f"Erro ao processar a query: {str(e)}"
            self.spark_sql_output.insert(tk.END, error_msg)
            self.pyspark_output.insert(tk.END, error_msg)

def main():
    root = tk.Tk()
    app = SQLConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()