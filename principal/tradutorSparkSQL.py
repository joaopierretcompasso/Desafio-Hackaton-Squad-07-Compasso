import re
import sqlparse
from sqlparse.sql import Identifier, Function, Parenthesis

class ConverterSparkSQL:
    def __init__(self, query_sql):
        self.query_sql = query_sql.strip()
        self.parsed = sqlparse.parse(self.query_sql)[0]
        self.subqueries = {}
        self.ctes = {}
        self.counter = 0
        self.extrai_ctes()

    def extrai_ctes(self):
        "Nessa função, são estraídas as Common Table Expressions (CTEs) que podem"
        "vir a estar presentes na query"
        if self.parsed.tokens and self.parsed.tokens[0].value.upper() == 'WITH':
            tokens_cte = []
            for token in self.parsed.tokens[1:]:
                if token.value.upper() == "SELECT":
                    break
                tokens_cte.append(token)

            string_ctes = ''.join(t.value for t in tokens_cte)
            for cte in re.split(r',\s*(?![^()]*\))', string_ctes):
                if ' AS ' in cte:
                    nome, subquery = re.split(r'\s+AS\s+', cte, 1, flags=re.IGNORECASE)
                    nome = nome.strip() 
                    subquery = re.sub(r'^\(|\)$', '', subquery.strip())
                    self.ctes[nome] = ConverterSparkSQL(subquery)

    def gerador_alias(self):
        "Função que gera um alias único para as sunqueries"
        "Assim facilitando seu processamento"
        alias = f"subquery_{self.counter}"
        self.counter += 1
        return alias
        
    def parsing_expressoes(self, token):
        "Função que analisa as expressões SQL mais complexas"
        if isinstance(token, Identifier):
            return token.value
        
        elif isinstance(token, Function):
            nome_funcao = token.get_name()
            parametros = ''.join(self.parsing_expressoes(t) for t in token.tokens if not t.is_whitespace)
            return f"{nome_funcao}({parametros})"
        
        elif isinstance(token, Parenthesis):
            conteudo = token.value[1:-1].strip()
            if conteudo.upper().startswith('SELECT'):
                alias = self.gerador_alias()
                self.subqueries[alias] = ConverterSparkSQL(conteudo)
                return alias
            return token.value
        
        return token.value
    
    def tradutor(self):
        "Função que traduz para string executável spark.sql"

        # Pesquisei algumas funções que não são compatíveis e então, são substituídas
        # Obviamente, são substituídas por funções que são compatíveis
        substituicoes = {
            r'\bNVL\b': 'COALESCE',
            r'\bSYSDATE\b': 'CURRENT_DATE()',
            r'\bTO_DATE\b': 'TO_DATE',
            r'\bDECODE\b': 'CASE',
            r'\bROWNUM\b': 'ROW_NUMBER() OVER (ORDER BY (SELECT_NULL))',
            r'\bTRUNC\b': 'DATE_TRUNC'
        }

        resultado = self.query_sql
        
        for padrao, substituicao in substituicoes.items():
            resultado = re.sub(padrao, substituicao, resultado, flags=re.IGNORECASE)

        # Faz o processamento das CTEs
        if self.ctes:
            string_ctes = 'WITH ' + ',\n'.join(
                f"{nome} AS ({self.ctes[nome].tradutor()})"
                for nome in self.ctes
            )
            resultado = re.sub(r'^SELECT', string_ctes + '\nSELECT', resultado, flags=re.IGNORECASE)

        for alias, subquery in self.subqueries.items():
            subquery_traduzida = subquery.tradutor()
            resultado = resultado.replace(f"({alias})", f"({subquery_traduzida})")

        return f'spark.sql("""{resultado}""")'