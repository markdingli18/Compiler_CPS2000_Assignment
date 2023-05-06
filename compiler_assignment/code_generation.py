from lexer import *
from parser_ import *
from semantic_analyser  import *

class CodeGenerationError(Exception):
    pass

class PixIRCodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.code = []

    def visit(self, node):
        if isinstance(node, tuple):
            method_name = f'visit_{node[0]}'
            visitor = getattr(self, method_name, self.generic_visit)
            return visitor(node)
        else:
            raise CodeGenerationError(f"Unsupported node type '{type(node).__name__}'.")

    def generic_visit(self, node):
        raise CodeGenerationError(f"No visit method implemented for node type '{node[0]}'.")

    def visit_DECLARATION(self, node):
        _, data_type, name, expression = node
        expr_code = self.visit(expression)
        self.code.append(f"declare {data_type} {name} = {expr_code}")

    def visit_ASSIGNMENT(self, node):
        _, name, expression = node
        expr_code = self.visit(expression)
        self.code.append(f"{name} = {expr_code}")

    # Add visit methods for other AST node types, for example:

    def visit_PLUS(self, node):
        left_code = self.visit(node[1])
        right_code = self.visit(node[2])
        return f"{left_code} + {right_code}"
    
    def visit_INTEGER_LITERAL(self, node):
        _, value = node
        return str(value)

    # ... continue implementing visit methods for other node types

    def generate(self):
        for node in self.ast:
            self.visit(node)
        return "\n".join(self.code)
    
###########################################################################################################################################

# Usage:
source_code = '''
let x: int = 5;
'''

try:
    # Tokenization
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    # Parsing
    parser = Parser(tokens)
    ast = parser.parse()
    
    # Semantic Analysis
    semantic_analyzer = SemanticAnalyzer(ast)
    for node in ast:
        semantic_analyzer.visit(node)

    # PixIR Code Generation
    code_generator = PixIRCodeGenerator(ast)
    pixir_code = code_generator.generate()
    print("\nGenerated PixIR code:\n")
    print(pixir_code)
    print("\n"+"-"*100)

except LexerError as e:
    print(f"Error: {e}")
except ParserError as e:
    print(f"Error: {e}")
except SemanticError as e:
    print(f"Error: {e}")
except CodeGenerationError as e:
    print(f"Error: {e}")