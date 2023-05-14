# Import all definitions from the lexer, parser and semantic_analyser code
from lexer import *
from parser_ import *
from semantic_analyser import *

# Custom exception class for code generation errors
class CodeGenerationError(Exception):
    def __init__(self, message="An error occurred during code generation."):
        self.message = message
        super().__init__(self.message)

class PixIRCodeGenerator:
    def __init__(self, ast):
        # The abstract syntax tree to be traversed
        self.ast = ast
        # List of generated code lines
        self.code = []
        # Offset to track the relative position of variables in memory
        self.frame_offset = 0
        # Dictionary to store variables and their corresponding offsets
        self.variables = {} 
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit(self, node):
        # Check if the node is a tuple. If so, it's a node we can visit.
        if isinstance(node, tuple):
            # Generate method name for visiting this node type
            method_name = f'visit_{node[0]}'
            # Try to get the method from the current instance, if it doesn't exist, use generic_visit method
            visitor = getattr(self, method_name, self.generic_visit)
            # Call the method and return its result
            return visitor(node)
        else:
            # If the node is not a tuple, raise an error indicating the node type is unsupported
            raise CodeGenerationError(f"Unsupported node type '{type(node).__name__}'.")
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def generic_visit(self, node):
        # If a specific visit method for a node type is not implemented, this method is called.
        # Raise an error indicating the node type is unsupported.
        raise CodeGenerationError(f"No visit method implemented for node type '{node[0]}'.")
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def get_var_offset(self, name):
        # Check if the variable has been declared
        if name not in self.variables:
            # If not, raise an error
            raise CodeGenerationError(f"Variable '{name}' has not been declared.")
        # If the variable has been declared, return its offset
        return self.variables[name]
    
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_DECLARATION(self, node):
        # Unpack the node, which contains the data type, name and expression of the variable to be declared
        _, data_type, name, expression = node
        
        # Visit the expression node to evaluate its value
        self.visit(expression)
        
        # Generate PixIR code to allocate memory for the variable
        self.code.append("push 1")
        self.code.append("alloc")

        # Generate PixIR code to store the evaluated value in the allocated memory
        self.code.append(f"push {self.frame_offset}")
        self.code.append("push 0")
        self.code.append("st")

        # Save the frame offset of the declared variable in the variables dictionary
        self.variables[name] = self.frame_offset

        # Increment the frame offset for the next variable
        self.frame_offset += 1
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_ASSIGNMENT(self, node):
        # Unpack the node, which contains the name and expression of the variable to be assigned
        _, name, expression = node
        
        # Visit the expression node to evaluate its value
        self.visit(expression)

        # Get the frame offset of the variable to be assigned
        var_offset = self.get_var_offset(name)

        # Generate PixIR code to store the evaluated value in the memory location of the variable
        self.code.append(f"push {var_offset}")
        self.code.append("push 0")
        self.code.append("st")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_PLUS(self, node):
        # Visit the nodes of the operands of the plus operation to evaluate their values
        self.visit(node[1])
        self.visit(node[2])

        # Generate PixIR code to perform the addition operation
        self.code.append("add")

    def visit_MUL(self, node):
        # Visit the nodes of the operands of the multiplication operation to evaluate their values
        self.visit(node[1])
        self.visit(node[2])

        # Generate PixIR code to perform the multiplication operation
        self.code.append("mul")

    #---------------------------------------------------------------------------------------------------------------------------------------    
    
    def visit_VARIABLE(self, node):
        # Unpack the node, which contains the name of the variable
        _, name = node
        
        # Get the frame offset of the variable
        var_offset = self.get_var_offset(name)

        # Generate PixIR code to load the value of the variable from memory
        self.code.append(f"push {var_offset}")
        self.code.append("push 0")
        self.code.append("ld")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_INTEGER_LITERAL(self, node):
        # Unpack the node, which contains the integer value
        _, value = node
        
        # Generate PixIR code to push the integer value onto the stack
        self.code.append(f"push {value}")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_FLOAT_LITERAL(self, node):
        # Unpack the node, which contains the float value
        _, value = node
        
        # Generate PixIR code to push the float value onto the stack
        self.code.append(f"push {value}")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_BOOLEAN_LITERAL(self, node):
        # Unpack the node, which contains the boolean value
        _, value = node
        
        # Generate PixIR code to push the boolean value (converted to an integer) onto the stack
        self.code.append(f"push {int(value)}")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_COLOR_LITERAL(self, node):
        # Unpack the node, which contains the color value
        _, value = node
        
        # Generate PixIR code to push the color value onto the stack
        self.code.append(f"push {value}")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_STRING_LITERAL(self, node):
        # Unpack the node, which contains the string value
        _, value = node
        
        # Encode the string value into a comma-separated string of ordinal values
        encoded_string = ",".join(str(ord(char)) for char in value)
        
        # Generate PixIR code to push the encoded string onto the stack
        self.code.append(f'push "{encoded_string}"')
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_PRINT(self, node):
        # Unpack the node, which contains the expression to be printed
        _, expression = node
        
        # Visit the expression node to evaluate its value
        self.visit(expression)
        
        # Generate PixIR code to print the evaluated value
        self.code.append("print")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_DELAY(self, node):
        # Unpack the node, which contains the delay node
        _, delay_node = node
        
        # Visit the delay node to evaluate its value
        self.visit(delay_node)
        
        # Generate PixIR code to perform a delay operation
        self.code.append("delay")

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_PIXEL_STATEMENT(self, node):
        # Unpack the node, which contains arguments for the pixel statement
        _, arguments = node
        x, y, color = arguments

        # Visit the nodes for x, y, and color to evaluate their values
        self.visit(x)     
        self.visit(y)     
        self.visit(color)

        # Generate PixIR code to perform a pixel operation
        self.code.append("pixel")

    def visit_PIXELR_STATEMENT(self, node):
        # Unpack the node, which contains arguments for the pixelr statement
        _, arguments = node
        x, y, color, radius, end_color = arguments

        # Visit the nodes for x, y, color, radius, and end_color to evaluate their values
        self.visit(x)
        self.visit(y)
        self.visit(color)
        self.visit(radius)
        self.visit(end_color)

        # Generate PixIR code to perform a pixelr operation
        self.code.append("pixelr")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_WIDTH(self, node):
        # Unpack the node, which contains the width node
        _, width_node = node
        self.visit(width_node)  # Visit the width node to evaluate its value

        # Generate PixIR code to perform a width operation
        self.code.append("width")
        
    def visit_HEIGHT(self, node):
        # Unpack the node, which contains the height node
        _, height_node = node
        self.visit(height_node)  # Visit the height node to evaluate its value

        # Generate PixIR code to perform a height operation
        self.code.append("height")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_READ_STATEMENT(self, node):
        # Unpack the node, which contains arguments for the read statement
        _, arguments = node
        x, y = arguments

        # Visit the nodes for x and y to evaluate their values
        self.visit(x)
        self.visit(y)

        # Generate PixIR code to perform a read operation
        self.code.append("read")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_IDENTIFIER(self, node):
        # Unpack the node, which contains the name of the identifier
        _, name = node
        var_offset = self.get_var_offset(name)

        # Generate PixIR code to load the value of the identifier from memory
        self.code.append(f"push {var_offset}")
        self.code.append("push 0")
        self.code.append("ld")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_RANDI_STATEMENT(self, node):
        # Unpack the node, which contains the expression for the randi statement
        _, expression = node
        self.visit(expression)  # Visit the expression node to evaluate its value

        # Generate PixIR code to perform a randi operation
        self.code.append("irnd")
            
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_RELATIONAL_OPERATOR(self, node):
        # Unpack the node, which contains the left and right expressions for the relational operator
        _, left_expr, right_expr = node

        # Determine the type of the operator based on the types of the left and right expressions
        if left_expr[0] == "IDENTIFIER" and right_expr[0] == "INTEGER_LITERAL":
            operator = ">"
        elif left_expr[0] == "INTEGER_LITERAL" and right_expr[0] == "IDENTIFIER":
            operator = "<"
        else:
            raise CodeGenerationError(f"Unsupported relational operator between {left_expr[0]} and {right_expr[0]}.")

        # Visit the left and right expression nodes to evaluate their values
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
        # Unpack the node, which contains the condition and body for the while loop
        _, condition, body = node

        # Generate PixIR code to mark the start of the loop
        self.code.append(".WHILE_START")  

        # Visit the condition node to evaluate its value
        self.visit(condition)

        # Generate PixIR code to jump to the end of the loop if the condition is false
        self.code.append("cjmp .WHILE_END")

        # Visit the body node to generate PixIR code for the body of the loop
        self.visit(body)

        # Generate PixIR code to jump back to the start of the loop
        self.code.append("jmp .WHILE_START")

        # Generate PixIR code to mark the end of the loop
        self.code.append(".WHILE_END")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_BLOCK(self, node):
        # Unpack the node, which contains the statements for the block
        _, statements = node

        # Visit each statement node to generate PixIR code for each statement
        for statement in statements:
            self.visit(statement)
            
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_IF(self, node):
        # Unpack the node, which contains the condition, if block, and else block for the if statement
        _, condition, if_block, *else_block = node

        # Visit the condition node to evaluate its value
        self.visit(condition)

        # Generate PixIR code to jump to the else block if the condition is false
        self.code.append("cjmp .ELSE")

        # Visit the if block node to generate PixIR code for the if block
        self.visit(if_block)

        # Generate PixIR code to jump to the end of the if statement if the if block was executed
        self.code.append("jmp .ENDIF")

        # If there is an else block, visit the else block node to generate PixIR code for the else block
        if else_block:
            self.visit(else_block[0])

        # Generate PixIR code to mark the end of the if statement
        self.code.append(".ENDIF")
        
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
        # Loop over each node in the abstract syntax tree (AST)
        for node in self.ast:
            # Call the visit method to generate PixIR code for each node
            self.visit(node)
        
        # Append the 'ret' instruction to the end of the code to mark the end of the program
        self.code.append("ret")

        # Join all the PixIR code lines with new line characters and return the result
        return "\n".join(self.code)
    
###########################################################################################################################################

# Usage:

# Specify the name of the file
filename = 'input.txt'

# Open the file and read the contents into a string
with open(filename, 'r') as file:
    source_code = file.read()

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