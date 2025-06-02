import re
import sqlparse
from sqlparse.sql import Identifier, Function, Parenthesis, IdentifierList
from sqlparse.tokens import Keyword, DML, Wildcard, Punctuation

class ConverterPySpark:
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
                if 'AS' in cte:
                    nome, subquery = re.split(r'\s+AS\s+', cte, 1, flags=re.IGNORECASE)
                    nome = nome.strip() 
                    subquery = re.sub(r'^\(|\)$', '', subquery.strip())
                    self.ctes[nome] = ConverterPySpark(subquery)

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
                self.subqueries[alias] = ConverterPySpark(conteudo)
                return alias
            return token.value
        
        elif isinstance(token, IdentifierList):
            return ', '.join(self.parsing_expressoes(t) for t in token.get_identifiers())
        
        elif token.ttype is Wildcard:
            return "*"
        
        return token.value

    def extrai_clausulas(self):
        "Função que faz a extração dos principais tipos de query"
        clausulas = {
            'select': [], 'from': [], 'where': [], 'join': [],
            'group_by': [], 'having': [], 'order_by': [], 'limit': None
        }

        clausula_atual = None
        faz_join = False

        for token in self.parsed.tokens:
            if token.is_whitespace or isinstance(token, sqlparse.sql.Comment):
                continue

            if token.ttype is DML and token.value.upper() == 'SELECT':
                clausula_atual = 'select'

            elif token.value.upper() == 'FROM':
                clausula_atual = 'from'
                faz_join = False

            elif token.value.upper() == 'WHERE':
                clausula_atual = 'where'
                faz_join = False
            
            elif token.value.upper() == 'GROUP BY':
                clausula_atual = 'group_by'
                faz_join = False
            
            elif token.value.upper() == 'HAVING':
                clausula_atual = 'having'
                faz_join = False

            elif token.value.upper() == 'ORDER BY':
                clausula_atual = 'order_by'
                faz_join = False

            elif token.value.upper() == 'LIMIT':
                clausula_atual = 'limit'
                faz_join = False

            elif token.value.upper().startswith('JOIN'):
                clausula_atual = 'join'
                faz_join = True

            if clausula_atual:
                if clausula_atual == 'limit' and token.ttype not in (Keyword, Punctuation):
                    clausulas['limit'] = token.value

                elif faz_join or clausula_atual in ['join', 'from']:
                    clausulas[clausula_atual].append(token)

                elif clausula_atual != 'limit':
                    clausulas[clausula_atual].append(token)
        
        return clausulas

    def parsing_FROM(self, tokens):
        "Função que analisa e faz o parsing do FROM"

        if not tokens:
            return None
        
        if isinstance(tokens[0], Parenthesis):
            conteudo = tokens[0].value[1:-1].strip()
            if conteudo.upper().startswith('SELECT'):
                alias = self.gerador_alias()
                self.subqueries[alias] = ConverterPySpark(conteudo)
                return alias
        return self.parsing_expressoes(tokens[0])
    
    def parsing_JOIN(self, tokens):
        "Função que analisa e faz o parsing do JOIN"
        tipos_JOIN = []
        JOIN_atual = {'type': 'inner', 'table': None, 'condition': None}

        for token in tokens:
            valor_token_maiusculo = token.value.upper()

            if valor_token_maiusculo.startswith('LEFT'):
                JOIN_atual['type'] = 'left'
            
            elif valor_token_maiusculo.startswith('RIGHT'):
                JOIN_atual['type'] = 'right'

            elif valor_token_maiusculo.startswith('FULL'):
                JOIN_atual['type'] = 'full'

            elif valor_token_maiusculo.startswith('CROSS'):
                JOIN_atual['type'] = 'cross'

            if isinstance(token, Identifier):
                JOIN_atual['table'] = self.parsing_expressoes(token)

            if isinstance(token, Parenthesis) or valor_token_maiusculo.startswith('ON'):
                condicao = token.value[4:] if valor_token_maiusculo.startswith('ON') else token.value[1:-1]
                JOIN_atual['condition'] = condicao.strip()
                tipos_JOIN.append(JOIN_atual.copy())
                JOIN_atual = {'type': 'inner', 'table': None, 'condition': None}

        return tipos_JOIN
    
    def parsing_SELECT(self, tokens):
        "Função que analisa e faz o parsing do SELECT"
        expressoes = []
        for token in tokens:
            if isinstance(token, IdentifierList):
                for subtoken in token.get_identifiers():
                    expr = self.parsing_expressoes(subtoken)
                    expressoes.append(expr)
            else: 
                expr = self.parsing_expressoes(token)
                expressoes.append(expr)

        return expressoes
    
    def construtor(self, clausulas):
        "Função que constrói a query SQL, no formato PySpark desejado"

        # Obtém a tabela principal
        clausula_from = self.parsing_FROM(clausulas['from'])
        if not clausula_from:
            return "# Erro: Não foi possível identificar a tabela FROM"
            
        nome_tabela = clausula_from.split()[-1] if ' ' in clausula_from else clausula_from
        nome_df = f"{nome_tabela.lower()}_df"

        # Inicia a cadeia de métodos
        cadeia = f"{nome_df} = spark.table(\"{nome_tabela}\")"

        # Resgata os JOINS
        for join in self.parsing_JOIN(clausulas['join']):
            tabela = join['table'].split()[-1] if ' ' in join['table'] else join['table']
            tipo_JOIN = join['type']
            condicao = join['condition']
            cadeia += f".join({tabela.lower()}_df, \"{condicao}\", \"{tipo_JOIN}\")"

        # Resgata WHERE
        if clausulas['where']:
            expressao_where = ' AND '.join(self.parsing_expressoes(t) for t in clausulas['where'])
            cadeia += f".filter(\"{expressao_where}\")"

        # Resgata GROUP BY com funções de agregação
        if clausulas['group_by']:
            group_by_colunas = [self.parsing_expressoes(t) for t in clausulas['group_by']]
            string_group_by = ', '.join([f'\"{coluna}\"' for coluna in group_by_colunas])
            cadeia += f".groupBy({string_group_by})"

            expressoes_select = self.parsing_SELECT(clausulas['select'])
            expressoes_agregacao = [expr for expr in expressoes_select if '(' in expr]
            if expressoes_agregacao:
                string_agregacao = ', '.join([f'F.expr(\"{expr}\")' for expr in expressoes_agregacao])
                cadeia += f".agg({string_agregacao})"

        # SELECT simples
        if not clausulas['group_by'] and clausulas['select']:
            expressoes_select = self.parsing_SELECT(clausulas['select'])
            string_select = ', '.join([f'\"{expr.split(" AS ")[0].strip()}\"' for expr in expressoes_select])
            cadeia += f".select({string_select})"   

        # Resgata HAVING
        if clausulas['having']:
            expressao_having = ' AND '.join(self.parsing_expressoes(t) for t in clausulas['having'])
            cadeia += f".filter(\"{expressao_having}\")"

        # Resgata ORDER BY
        if clausulas['order_by']:
            expressao_order_by = ', '.join(self.parsing_expressoes(t) for t in clausulas['order_by'])
            if 'DESC' in expressao_order_by.upper():
                coluna = re.sub(r'\s+DESC', '', expressao_order_by, flags=re.IGNORECASE).strip()
                cadeia += f".orderBy(\"{coluna}\", ascending=False)"
            else:
                coluna = re.sub(r'\s+ASC', '', expressao_order_by, flags=re.IGNORECASE).strip()
                cadeia += f".orderBy(\"{coluna}\")"

        # Resgata LIMIT
        if clausulas['limit']:
            cadeia += f".limit({clausulas['limit']})"

        return cadeia
    
    def tradutor(self):
        "Função que chama funções (reduntante, sabemos)"
        "Então, retorna a query SQL no formato PySpark desejado, encadeado corretamente"

        clausulas = self.extrai_clausulas()
        return self.construtor(clausulas)