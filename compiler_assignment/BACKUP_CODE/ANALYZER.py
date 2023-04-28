from lexer import *
from parser_ import *

###########################################################################################################################################

class SemanticError(Exception):
    pass

###########################################################################################################################################

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def add(self, name, data_type):
        if name in self.scopes[-1]:
            raise SemanticError(f"Variable '{name}' is already declared in the current scope.")
        self.scopes[-1][name] = data_type

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def update(self, name, data_type):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = data_type
                return
        raise SemanticError(f"Variable '{name}' not found in any scope.")
    
###########################################################################################################################################

class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = SymbolTable()
    
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit(self, node):
        pass

    #---------------------------------------------------------------------------------------------------------------------------------------

    def generic_visit(self, node):
        pass
                
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_DECLARATION(self, node):
        pass
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_ASSIGNMENT(self, node):
        pass
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_LITERAL(self, node):
        pass
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_VARIABLE(self, node):
        pass
    
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_STATEMENT_BLOCK(self, node):
        pass
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_BINARY_EXPRESSION(self, node):
        pass
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_IF(self, node):
        pass
            
    #---------------------------------------------------------------------------------------------------------------------------------------

    # Add more visit methods for other nodes as needed
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
###########################################################################################################################################

# Usage:
source_code = """
let x: int = 5 * 20 + 5;
"""

try:
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    semantic_analyzer = SemanticAnalyzer(ast)
    for node in ast:
        semantic_analyzer.visit(node)
    
    print("Semantic analysis completed successfully.")

except LexerError as e:
    print(f"Error: {e}")
except ParserError as e:
    print(f"Error: {e}")
except SemanticError as e:
    print(f"Error: {e}")