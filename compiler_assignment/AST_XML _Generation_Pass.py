from lexer import *
from parser_ import *

class ASTVisitor:
    def __init__(self):
        self.indentation_level = 0
        
    def visit_program(self, program):
        pass
    
    def visit_assignment(self, assignment):
        pass
    
    def visit_function_call(self, function_call):
        pass
    
    def visit_if(self, if_statement):
        pass
    
    def visit_condition(self, condition):
        pass
    
    def visit_expression(self, expression):
        pass
    
    def visit_term(self, term):
        pass
    
    def visit_factor(self, factor):
        pass
    
    def visit_block(self, block):
        pass
    
    def visit_function_definition(self, function_definition):
        pass
    
    def visit_read_call(self, read_call):
        pass
    
    def visit_return(self, return_statement):
        pass
    
    def visit_print(self, print_statement):
        pass
    
    def visit_identifier(self, identifier):
        pass
    
    def visit_integer_literal(self, integer_literal):
        pass
    
    def visit_float_literal(self, float_literal):
        pass
    
    def visit_boolean_literal(self, boolean_literal):
        pass
    
    def visit_string_literal(self, string_literal):
        pass
    
    def visit_color_literal(self, color_literal):
        pass
    
    def print_xml(self, ast):
        pass

# PixArLang program
source_code = """
x =10;
"""

try:
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    print("\nLexer:\n")
    for token in tokens:
        print(token)

    parser = Parser(tokens)
    parsed_program = parser.parse()
    print("\n" + "-"*100)
    print("\nParsed program:\n")
    print(parsed_program)

    # Generate XML representation of AST
    visitor = ASTVisitor()
    visitor.print_xml(parsed_program)
    
except LexerError as e:
    print(f"Error: {e}")
except ParserError as e:
    print(f"Error: {e}")

print("\n" + "-"*100)