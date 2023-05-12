from lexer import *
from parser_ import *
from semantic_analyser import *

class CodeGenerationError(Exception):
    pass

###########################################################################################################################################

class PixIRCodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.code = []
        self.frame_offset = 0
        self.variables = {}  
    
    def visit(self, node):
        method_name = f"visit_{node[0]}"
        method = getattr(self, method_name, None)
        if method is None:
            raise CodeGenerationError(f"No visit method for node type: {node[0]}")
        method(node)

    def get_var_offset(self, name):
        if name not in self.variables:
            self.variables[name] = self.frame_offset
            self.frame_offset += 1
        return self.variables[name]

    def generate(self):
        for node in self.ast:
            self.visit(node)
        return self.code    
    
    # Visit methods for each node type... 

    def visit_ASSIGNMENT(self, node):
        _, name, expression = node
        self.visit(expression)  

        var_offset = self.get_var_offset(name)

        self.code.append(f"push {var_offset}")
        self.code.append("push 0")  
        self.code.append("st") 
        
    #--------------------------------------------------------------------------------------------------------------------------------------- 

    def visit_PLUS(self, node):
        self.visit(node[1])  
        self.visit(node[2]) 
        self.code.append("add") 
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_MUL(self, node):
        self.visit(node[1])  
        self.visit(node[2])  
        self.code.append("mul") 
        
    #--------------------------------------------------------------------------------------------------------------------------------------- 
    
    def visit_VARIABLE(self, node):
        _, name = node
        var_offset = self.get_var_offset(name)
        
        self.code.append(f"push {var_offset}")
        self.code.append("push 0")  
        self.code.append("ld") 
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_DECLARATION(self, node):
        _, name, _, expression = node
        self.visit(expression)

        var_offset = self.get_var_offset(name)

        self.code.append(f"push {var_offset}")
        self.code.append("push 0")
        self.code.append("st")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_INTEGER_LITERAL(self, node):
        _, value = node
        self.code.append(f"push {value}")  
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
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
    print("\n".join(pixir_code))
    print("\n" + "-" * 100)

except LexerError as e:
    print(f"Error: {e}")
except ParserError as e:
    print(f"Error: {e}")
except SemanticError as e:
    print(f"Error: {e}")
except CodeGenerationError as e:
    print(f"Error: {e}")