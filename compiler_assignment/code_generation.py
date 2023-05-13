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
        self.variables = {} 
        
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
        self.visit(expression)  
        self.code.append("push 1")
        self.code.append("alloc")

        self.code.append(f"push {self.frame_offset}")
        self.code.append("push 0")
        self.code.append("st")

        self.variables[name] = self.frame_offset

        self.frame_offset += 1
        
    #---------------------------------------------------------------------------------------------------------------------------------------

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
        self.code.append(f"push {int(value)}")  
        
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
        
    def visit_WIDTH(self, node):
        _, width_node = node
        self.visit(width_node)  
        self.code.append("width")
        
    def visit_HEIGHT(self, node):
        _, width_node = node
        self.visit(width_node)  
        self.code.append("height")
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_READ_STATEMENT(self, node):
        _, arguments = node
        x, y = arguments

        self.visit(x)
        self.visit(y)

        self.code.append("read")
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_IDENTIFIER(self, node):
        _, name = node
        var_offset = self.get_var_offset(name)

        self.code.append(f"push {var_offset}")
        self.code.append("push 0")
        self.code.append("ld")
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_RANDI_STATEMENT(self, node):
        _, expression = node
        self.visit(expression)
        self.code.append("irnd")
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_RELATIONAL_OPERATOR(self, node):
        _, left_expr, right_expr = node

        # Determine the operator
        if left_expr[0] == "IDENTIFIER" and right_expr[0] == "INTEGER_LITERAL":
            operator = ">"
        elif left_expr[0] == "INTEGER_LITERAL" and right_expr[0] == "IDENTIFIER":
            operator = "<"
        else:
            raise CodeGenerationError(f"Unsupported relational operator between {left_expr[0]} and {right_expr[0]}.")

        # Visit the left and right expressions
        self.visit(left_expr)
        self.visit(right_expr)

        # Add the appropriate operation to the code based on the operator
        if operator == "<":
            self.code.append("lt")
        elif operator == "<=":
            self.code.append("le")
        elif operator == ">":
            self.code.append("gt")
        elif operator == ">=":
            self.code.append("ge")
        elif operator == "==":
            self.code.append("eq")
        elif operator == "!=":
            self.code.append("neq")
        else:
            raise CodeGenerationError(f"Unsupported relational operator '{operator}'.")

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_WHILE(self, node):
        _, condition, body = node

        self.code.append(".WHILE_START")  # label for start of the loop

        # evaluate the condition
        self.visit(condition)

        # based on condition, jump to end of loop if condition is false
        self.code.append("cjmp .WHILE_END")

        # generate code for the body of the loop
        self.visit(body)  # this line is changed

        # jump back to start of loop
        self.code.append("jmp .WHILE_START")

        self.code.append(".WHILE_END")  # label for end of the loop
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_BLOCK(self, node):
        _, statements = node
        for statement in statements:
            self.visit(statement)
            
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_IF(self, node):
        _, condition, if_block, *else_block = node

        # Visit the condition
        self.visit(condition)
            
        # Add some code to check the result of the condition
        # and skip the IF block if the condition is false
        self.code.append("cjmp .ELSE")

        # Visit the IF block
        self.visit(if_block)

        # Add some code to jump over the ELSE block
        # if the IF block was executed
        self.code.append("jmp .ENDIF")

        # Visit the ELSE block (this will only happen if the condition was false)
        if else_block:
            self.visit(else_block[0])  # else_block is a list now, access its first (and only) element
            
        self.code.append(".ENDIF")
        
    # todo else
    def visit_ELSE(self, node):
        _, _, else_block = node

        # This label will be jumped to if the condition in the IF statement was false
        self.code.append(".ELSE")

        # Visit the ELSE block
        self.visit(else_block)

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_FUNCTION_DEF(self, node):
        _, function_name, parameters, return_type, body = node

        # Generate a label for the function name
        self.code.append(f".{function_name}")

        # Add parameters to the variable environment and adjust the frame offset
        for parameter in parameters:
            name, type_ = parameter
            self.variables[name] = self.frame_offset
            self.frame_offset += 1

        # Generate code for the function body
        self.visit(body)

        # Add a return statement if not already present in the body
        if body[-1][0] != "RETURN":
            self.code.append("ret")

    def visit_RETURN(self, node):
        _, expression = node
        if expression is not None:
            # Generate code to load the value of the returned variable onto the stack
            name = expression[1]
            var_offset = self.get_var_offset(name)
            self.code.append(f"push {var_offset}")
            self.code.append("push 0")
            self.code.append("ld")

        self.code.append("ret")

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    # ToDo For loop 
    
    
    #---------------------------------------------------------------------------------------------------------------------------------------

    def generate(self):
        for node in self.ast:
            self.visit(node)
        
        self.code.append("ret")

        return "\n".join(self.code)
    
###########################################################################################################################################

# Usage:
source_code = '''
for (let x: int = 0; x < 10; x = x + 1) {
  __print("hello");
}
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