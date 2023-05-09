# Import all definitions from the lexer and parser code
from lexer import *
from parser_ import *

###########################################################################################################################################

class SemanticError(Exception):
    pass

###########################################################################################################################################

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]
    
    # Enters a new scope
    def enter_scope(self):
        self.scopes.append({})

    # Exits the current scope
    def exit_scope(self):
        self.scopes.pop()
        
    # Adds a new scope (redundant with enter_scope)
    def push_scope(self):
        self.scopes.append({})

    # Removes the current scope (redundant with exit_scope)
    def pop_scope(self):
        self.scopes.pop()

    # Adds a new variable to the current scope
    def add(self, name, data_type):
        if name in self.scopes[-1]:
            raise SemanticError(f"Variable '{name}' is already declared in the current scope.")
        self.scopes[-1][name] = data_type

    # Looks up a variable in the symbol table
    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    # Updates the data type of a variable
    def update(self, name, data_type):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = data_type
                return
        raise SemanticError(f"Variable '{name}' not found in any scope.")
    
    # Returns the data type of an expression
    def get_type(self, expr):
        if expr[0] == 'IDENTIFIER':
            return self.lookup(expr[1])
        elif expr[0] == 'INTEGER_LITERAL':
            return 'int'
        elif expr[0] == 'FLOAT_LITERAL':
            return 'float'
        elif expr[0] == 'STRING_LITERAL':
            return 'string'
        elif expr[0] == 'COLOR_LITERAL':
            return 'colour'
        else:
            return None
    
###########################################################################################################################################

class SemanticAnalyzer:
    def __init__(self, ast):
        # Initialize the SemanticAnalyzer with the given abstract syntax tree (AST).
        self.ast = ast
        
        # Create a new symbol table for semantic analysis.
        self.symbol_table = SymbolTable()
    
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit(self, node):
        # If the node is a tuple, use the first element to determine the method name to be called
        if isinstance(node, tuple):
            method_name = f'visit_{node[0]}'
            # Get the appropriate method and call it, using generic_visit as a fallback
            visitor = getattr(self, method_name, self.generic_visit)
            return visitor(node)
        else:
            # If the node is not a tuple, it is not supported
            raise SemanticError(f"Unsupported node type '{type(node).__name__}'.")

    # Raises a SemanticError indicating that no method has been implemented for the node type
    def generic_visit(self, node):
        raise SemanticError(f"No visit method implemented for node type '{node[0]}'.")
    
    # Visits a declaration node and adds the variable to the symbol table
    def visit_DECLARATION(self, node):
        # Get the data type, name, and expression from the node
        _, data_type, name, expression = node

        try:
            # Add the variable to the symbol table
            self.symbol_table.add(name, data_type)
        except SemanticError as e:
            # If the variable is already declared, raise an error
            print(f"Error: {e}")

        # Visit the expression
        self.visit(expression)

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_ASSIGNMENT(self, node):
        _, name, expression = node
        data_type = self.symbol_table.lookup(name)

        # Check if the variable is declared in the symbol table
        if data_type is None:
            raise SemanticError(f"Variable '{name}' not declared.")

        # Check if the expression type matches the declared type of the variable
        expr_type = self.visit(expression)
        if data_type != expr_type:
            raise SemanticError(f"Type mismatch in assignment to variable '{name}'.")

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_LITERAL(self, node):
        _, value = node
        
        # Determine the type of the literal node and return it
        if isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, bool):
            return 'bool'
        else:
            raise SemanticError(f"Unsupported literal type '{type(value).__name__}'.")
    
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_PLUS(self, node):
        # Get the types of the left and right operands of the '+' operator
        left_type = self.visit(node[1])
        right_type = self.visit(node[2])
        
        # Check if the operands are of type 'int'
        if left_type != 'int' or right_type != 'int':
            raise SemanticError("Operands of '+' operator must be of type 'int'.")
        
        # Return the resulting type
        return 'int'

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_MUL(self, node):
        _, left, right = node
        # Get the types of the left and right operands of the '*' operator
        left_type = self.visit(left)
        right_type = self.visit(right)

        # Check if the operands are of the same type
        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")

        # Return the resulting type
        return left_type

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_IDENTIFIER(self, node):
        _, name = node
        # Look up the data type of the identifier in the symbol table
        data_type = self.symbol_table.lookup(name)
        if data_type is None:
            raise SemanticError(f"Variable '{name}' not declared.")
        # Return the data type
        return data_type

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_LITERAL(self, node):
        # Extract the value from the literal node
        _, value = node
        
        # Determine the type of the literal based on its Python type
        if isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, bool):
            return 'bool'
        else:
            raise SemanticError(f"Unsupported literal type '{type(value).__name__}'.")
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_VARIABLE(self, node):
        # Extract the name of the variable from the node
        _, name = node
        
        # Look up the variable in the symbol table
        data_type = self.symbol_table.lookup(name)
        
        # Raise an error if the variable is not found
        if data_type is None:
            raise SemanticError(f"Variable '{name}' not declared.")
        
        # Return the data type of the variable
        return data_type
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_STATEMENT_BLOCK(self, node):
        # Extract the list of statements from the node
        _, statements = node
        
        # Enter a new scope in the symbol table
        self.symbol_table.enter_scope()
        
        # Visit each statement in the block
        for statement in statements:
            self.visit(statement)
        
        # Exit the scope in the symbol table
        self.symbol_table.exit_scope()
            
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_BINARY_EXPRESSION(self, node):
        # Retrieve left and right expression types
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        # Check for type mismatch
        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")

        # Return the type of the left expression (as all valid expressions must have the same type)
        return left_type
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_NEGATIVE(self, node):
        # Retrieve expression type
        _, expr = node
        expr_type = self.visit(expr)

        # Check that expression is of type 'int'
        if expr_type != 'int':
            raise SemanticError("Operand of '-' operator must be of type 'int'.")

        # Return 'int' as the type of the negative expression will always be 'int'
        return 'int'
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_DIV(self, node):
        # Retrieve left and right expression types
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        # Check that both left and right expressions are of type 'float'
        if left_type != 'float' or right_type != 'float':
            raise SemanticError("Operands of '/' operator must be of type 'float'.")

        # Return 'float' as the type of the expression will always be 'float'
        return 'float'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_MOD(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        # Check if operands are of type 'int'
        if left_type != 'int' or right_type != 'int':
            raise SemanticError("Operands of '%' operator must be of type 'int'.")
        
        # Return the resulting type of the operation
        return 'int'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_LESS_THAN(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        # Check if the operands have the same type and if it's numeric
        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")
        if left_type not in ['int', 'float']:
            raise SemanticError("Operands of '<' operator must be of numeric type.")
        
        # Return the resulting type of the operation
        return 'bool'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_GREATER_THAN(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        # Check if the operands have the same type and if it's numeric
        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")
        if left_type not in ['int', 'float']:
            raise SemanticError("Operands of '>' operator must be of numeric type.")
        
        # Return the resulting type of the operation
        return 'bool'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_LESS_THAN_EQUAL(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        # check for type compatibility
        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")

        # check if both operands are numeric
        if left_type not in ['int', 'float']:
            raise SemanticError("Operands of '<=' operator must be of numeric type.")
        
        return 'bool'

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_GREATER_THAN_EQUAL(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        # check for type compatibility
        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")

        # check if both operands are numeric
        if left_type not in ['int', 'float']:
            raise SemanticError("Operands of '>=' operator must be of numeric type.")
        
        return 'bool'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_EQUAL(self, node):
        # Extract the left and right expressions
        _, left, right = node
        
        # Get the types of the left and right expressions
        left_type = self.visit(left)
        right_type = self.visit(right)

        # Check for a type mismatch between the left and right expressions
        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")
        
        # Return the boolean type
        return 'bool'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_NOT_EQUAL(self, node):
        # Extract the left and right expressions
        _, left, right = node
        
        # Get the types of the left and right expressions
        left_type = self.visit(left)
        right_type = self.visit(right)

        # Check for a type mismatch between the left and right expressions
        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")
        
        # Return the boolean type
        return 'bool'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_LOGICAL_AND(self, node):
        # Extract the left and right expressions
        _, left, right = node
        
        # Get the types of the left and right expressions
        left_type = self.visit(left)
        right_type = self.visit(right)

        # Check that the left and right expressions are both of type bool
        if left_type != 'bool' or right_type != 'bool':
            raise SemanticError("Operands of '&&' operator must be of type 'bool'.")
        
        # Return the boolean type
        return 'bool'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_FLOAT_LITERAL(self, node):
        return 'float'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_BOOLEAN_LITERAL(self, node):
        return 'bool'

    #---------------------------------------------------------------------------------------------------------------------------------------
   
    def visit_INTEGER_LITERAL(self, node):
        return 'int' 
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_COLOR_LITERAL(self, node):
        return 'color'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_STRING_LITERAL(self, node):
        return 'str'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_PRINT(self, node):
        # get the expression to print
        _, expression = node

        # evaluate the expression
        self.visit(expression)
            
    #---------------------------------------------------------------------------------------------------------------------------------------
            
    def visit_DELAY(self, node):
        # get the delay time
        _, delay_time = node

        # ensure the delay time is an integer
        if not isinstance(delay_time[1], int):
            raise SemanticError(f"Delay time must be an integer.")
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_WIDTH(self, node):
        _, expression = node
        # visit the expression to determine its type
        expr_type = self.visit(expression)
        # check if the type is 'int'
        if expr_type != 'int':
            # if not, raise a semantic error
            raise SemanticError("Argument of 'WIDTH' instruction must be of type 'int'.")

    def visit_HEIGHT(self, node):
        _, expression = node
        # visit the expression to determine its type
        expr_type = self.visit(expression)
        # check if the type is 'int'
        if expr_type != 'int':
            # if not, raise a semantic error
            raise SemanticError("Argument of 'HEIGHT' instruction must be of type 'int'.")
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_READ_STATEMENT(self, node):
        # get the list of variables to be read
        variables = node[1]
        # check if each variable is declared in the symbol table
        for var in variables:
            if self.symbol_table.lookup(var[1]) is None:
                raise SemanticError(f"Variable '{var[1]}' not declared.")

#---------------------------------------------------------------------------------------------------------------------------------------

    def visit_RANDI_STATEMENT(self, node):
        _, variable = node
        # check if the variable is declared in the symbol table
        if self.symbol_table.lookup(variable[1]) is None:
            raise SemanticError(f"Variable '{variable[1]}' not declared.")
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_PIXEL_STATEMENT(self, node):
        for expr in node[1]:
            self.visit(expr)
        # Ensure that the arguments passed to PIXEL_STATEMENT are of correct type
        args = [self.symbol_table.get_type(expr) for expr in node[1]]
        if len(args) == 3 and args != ['int', 'int', 'int']:
            raise SemanticError(f"Incompatible argument types for PIXEL_STATEMENT: {args}, expected: ['int', 'int', 'int']")
        
    def visit_PIXELR_STATEMENT(self, node):
        for expr in node[1]:
            self.visit(expr)
        # Ensure that the arguments passed to PIXEL_STATEMENT are of correct type
        args = [self.symbol_table.get_type(expr) for expr in node[1]]
        if args != ['int', 'int', 'int', 'int', 'colour']:
            raise SemanticError(f"Incompatible argument types for PIXEL_STATEMENT: {args}, expected: ['int', 'int', 'int', 'int', 'colour']")

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_WHILE(self, node):
        # Extract the condition and block from the node
        condition, block = node[1], node[2]
        # Visit the condition expression
        self.visit(condition)
        # Enter a new scope for the block
        self.symbol_table.push_scope()
        # Visit the statements in the block
        self.visit(block)
        # Exit the scope for the block
        self.symbol_table.pop_scope()
            
    #---------------------------------------------------------------------------------------------------------------------------------------
            
    def visit_RELATIONAL_OPERATOR(self, node):
        # Extract the left and right operands from the node
        left_operand = node[1][0]
        right_operand = node[1][1]
        # Retrieve the data types of the operands from the symbol table
        left_type = self.symbol_table.get_type(left_operand)
        right_type = self.symbol_table.get_type(right_operand)
        # Check if the types of the operands match
        if left_type != right_type:
            raise SemanticError(f"Type mismatch in relational operator '{node[0]}': {left_type} vs {right_type}")
            
    #---------------------------------------------------------------------------------------------------------------------------------------        

    def visit_BLOCK(self, node):
        # Enter a new scope for the block
        self.symbol_table.push_scope()
        # Visit the statements in the block
        for statement in node[1]:
            self.visit(statement)
        # Exit the scope for the block
        self.symbol_table.pop_scope()
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_IF(self, node):
        # check if the node has the correct structure
        if len(node) == 4:
            _, condition, true_block, else_node = node
        elif len(node) == 3:
            _, condition, true_block = node
            else_node = None
        else:
            raise ValueError("Invalid IF node structure")

        # visit the condition
        self.visit(condition)
        
        # enter a new symbol table scope
        self.symbol_table.enter_scope()
        
        # visit the true block and exit the scope
        self.visit(true_block)
        self.symbol_table.exit_scope()

        # if there is an else block, enter a new scope, visit the block, and exit the scope
        if else_node:
            self.symbol_table.enter_scope()
            self.visit(else_node)
            self.symbol_table.exit_scope()
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_FUNCTION_DEF(self, node):
        _, name, params, return_type, block = node

        # Add the function to the symbol table with its name, parameters, and return type
        self.symbol_table.add(name, (params, return_type))

        # Enter a new scope
        self.symbol_table.enter_scope()

        # Add function parameters to the symbol table
        for param_name, param_type in params:
            self.symbol_table.add(param_name, param_type)

        # Visit the function block
        self.visit(block)

        # Exit the current scope
        self.symbol_table.exit_scope()
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_RETURN(self, node):
        # extract the expression to be returned from the node
        _, expression = node
        
        # visit the expression to check its  correctness
        self.visit(expression)

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_FOR(self, node):
        _, declaration_node, condition_node, update_node, block_node = node

        # Visit the declaration node and add the variable to the symbol table
        self.visit(declaration_node)
        var_name = declaration_node[2]
        self.symbol_table.add(var_name, 'int')

        # Visit the condition and update nodes
        self.visit(condition_node)
        self.visit(update_node)

        # Enter a new scope for the block
        self.symbol_table.enter_scope()

        # Visit the block nodes
        for block_stmt in block_node:
            self.visit(block_stmt)

        # Exit the scope for the block
        self.symbol_table.exit_scope()

    #---------------------------------------------------------------------------------------------------------------------------------------
    
###########################################################################################################################################

# Usage:

# Specify the name of the file
filename = 'input.txt'

# Open the file and read its contents into a string
with open(filename, 'r') as file:
    source_code = file.read()

try:
    # Tokenize the source code
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    # Parse the tokens to generate an AST
    parser = Parser(tokens)
    ast = parser.parse()

    # Print the AST for debugging purposes
    print("\n" + "-"*100+"\n\nAST: \n")
    print(ast)

    # Perform semantic analysis on the AST
    semantic_analyzer = SemanticAnalyzer(ast)
    for node in ast:
        semantic_analyzer.visit(node)
    
    # If no errors occurred during semantic analysis, print success message
    print("\nSemantic analysis completed successfully!")

except LexerError as e:
    # Catch Lexer errors and print the error message
    print(f"Error: {e}")
except ParserError as e:
    # Catch Parser errors and print the error message
    print(f"Error: {e}")
except SemanticError as e:
    # Catch Semantic errors and print the error message
    print(f"Error: {e}")
    
# Print a separator line
print("\n" + "-"*100)