from lexer import *
from parser_ import *
from semantic_analyser  import *

class CodeGenerationError(Exception):
    pass

###########################################################################################################################################

class PixIRCodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.code = []
        self.frame_offset = 0
        self.variables = {}  # a dictionary to keep track of variables and their frame offsets
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit(self, node):
        if isinstance(node, tuple):
            method_name = f'visit_{node[0]}'
            visitor = getattr(self, method_name, self.generic_visit)
            return visitor(node)
        else:
            raise CodeGenerationError(f"Unsupported node type '{type(node).__name__}'.")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def generic_visit(self, node):
        raise CodeGenerationError(f"No visit method implemented for node type '{node[0]}'.")
    
    #---------------------------------------------------------------------------------------------------------------------------------------

    def get_var_offset(self, name):
        if name not in self.variables:
            raise CodeGenerationError(f"Variable '{name}' has not been declared.")
        return self.variables[name]
    
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_DECLARATION(self, node):
        _, data_type, name, expression = node
        self.visit(expression)  # generates the code for the expression and adds it to self.code

        # Allocate space for new variable
        self.code.append("push 1")
        self.code.append("alloc")

        # Store the value of the expression in the variable
        self.code.append(f"push {self.frame_offset}")
        self.code.append("push 0")
        self.code.append("st")

        # Add the variable to our dictionary
        self.variables[name] = self.frame_offset

        self.frame_offset += 1
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_ASSIGNMENT(self, node):
        _, name, expression = node
        self.visit(expression)  # generates the code for the expression and adds it to self.code

        # Assuming you have a way to get the frame offset of a variable
        var_offset = self.get_var_offset(name)  # you need to implement this method

        self.code.append(f"push {var_offset}")
        self.code.append("push 0")
        self.code.append("st")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_PLUS(self, node):
        self.visit(node[1])  # generates the code for the left expression and adds it to self.code
        self.visit(node[2])  # generates the code for the right expression and adds it to self.code
        self.code.append("add")
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_MUL(self, node):
        self.visit(node[1])  # generates the code for the left expression and adds it to self.code
        self.visit(node[2])  # generates the code for the right expression and adds it to self.code
        self.code.append("mul")

    #---------------------------------------------------------------------------------------------------------------------------------------    
    
    def visit_VARIABLE(self, node):
        _, name = node
        var_offset = self.get_var_offset(name)

        # Load the value of the variable onto the stack
        self.code.append(f"push {var_offset}")
        self.code.append("push 0")
        self.code.append("ld")
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_INTEGER_LITERAL(self, node):
        _, value = node
        self.code.append(f"push {value}")
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_FLOAT_LITERAL(self, node):
        _, value = node
        self.code.append(f"push {value}")
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_BOOLEAN_LITERAL(self, node):
        _, value = node
        self.code.append(f"push {int(value)}")  # convert boolean to int (True -> 1, False -> 0)
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_COLOR_LITERAL(self, node):
        _, value = node
        self.code.append(f"push {value}")
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_STRING_LITERAL(self, node):
        _, value = node
        encoded_string = ",".join(str(ord(char)) for char in value)
        self.code.append(f'push "{encoded_string}"')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_PRINT(self, node):
        _, expression = node
        self.visit(expression)
        self.code.append("print")
   
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_DELAY(self, node):
        _, delay_node = node
        self.visit(delay_node) 
        self.code.append("delay")

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_PIXEL_STATEMENT(self, node):
        _, arguments = node
        x, y, color = arguments

        self.visit(x)     
        self.visit(y)     
        self.visit(color) 

        self.code.append("pixel")
        
    def visit_PIXELR_STATEMENT(self, node):
        _, arguments = node
        x, y, color, radius, end_color = arguments

        self.visit(x)
        self.visit(y)
        self.visit(color)
        self.visit(radius)
        self.visit(end_color)

        self.code.append("pixelr")

    #---------------------------------------------------------------------------------------------------------------------------------------

    # ... continue implementing visit methods for other node types
    
    #---------------------------------------------------------------------------------------------------------------------------------------

    def generate(self):
        for node in self.ast:
            self.visit(node)
        
        # Add a return statement at the end of the function
        self.code.append("ret")

        return "\n".join(self.code)
    
###########################################################################################################################################

# Usage:
source_code = '''
let w: colour = #FF0000;
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