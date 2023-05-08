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
        
    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
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
        self.ast = ast
        self.symbol_table = SymbolTable()
    
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit(self, node):
        if isinstance(node, tuple):
            method_name = f'visit_{node[0]}'
            visitor = getattr(self, method_name, self.generic_visit)
            return visitor(node)
        else:
            raise SemanticError(f"Unsupported node type '{type(node).__name__}'.")

    #---------------------------------------------------------------------------------------------------------------------------------------

    def generic_visit(self, node):
        raise SemanticError(f"No visit method implemented for node type '{node[0]}'.")
     
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_DECLARATION(self, node):
        _, data_type, name, expression = node

        try:
            self.symbol_table.add(name, data_type)
        except SemanticError as e:
            print(f"Error: {e}")

        self.visit(expression)

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_ASSIGNMENT(self, node):
        _, name, expression = node
        data_type = self.symbol_table.lookup(name)

        if data_type is None:
            raise SemanticError(f"Variable '{name}' not declared.")

        expr_type = self.visit(expression)
        if data_type != expr_type:
            raise SemanticError(f"Type mismatch in assignment to variable '{name}'.")
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_LITERAL(self, node):
        _, value = node
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
        left_type = self.visit(node[1])
        right_type = self.visit(node[2])
        
        if left_type != 'int' or right_type != 'int':
            raise SemanticError("Operands of '+' operator must be of type 'int'.")
        
        return 'int'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_MUL(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")

        return left_type
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_IDENTIFIER(self, node):
        _, name = node
        data_type = self.symbol_table.lookup(name)
        if data_type is None:
            raise SemanticError(f"Variable '{name}' not declared.")
        return data_type

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_LITERAL(self, node):
        _, value = node
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
        _, name = node
        data_type = self.symbol_table.lookup(name)
        if data_type is None:
            raise SemanticError(f"Variable '{name}' not declared.")
        return data_type
    
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_STATEMENT_BLOCK(self, node):
        _, statements = node
        self.symbol_table.enter_scope()
        for statement in statements:
            self.visit(statement)
        self.symbol_table.exit_scope()
            
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_BINARY_EXPRESSION(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")

        # You can add additional type checking based on the specific operator used
        # For example, if your language has specific rules for using different types with different operators

        return left_type
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_NEGATIVE(self, node):
        _, expr = node
        expr_type = self.visit(expr)
        if expr_type != 'int':
            raise SemanticError("Operand of '-' operator must be of type 'int'.")
        return 'int'
    
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_DIV(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        if left_type != 'float' or right_type != 'float':
            raise SemanticError("Operands of '/' operator must be of type 'float'.")
        
        return 'float'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_MOD(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        if left_type != 'int' or right_type != 'int':
            raise SemanticError("Operands of '%' operator must be of type 'int'.")
        
        return 'int'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_LESS_THAN(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")

        if left_type not in ['int', 'float']:
            raise SemanticError("Operands of '<' operator must be of numeric type.")
        
        return 'bool'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_GREATER_THAN(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")

        if left_type not in ['int', 'float']:
            raise SemanticError("Operands of '>' operator must be of numeric type.")
        
        return 'bool'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_LESS_THAN_EQUAL(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")

        if left_type not in ['int', 'float']:
            raise SemanticError("Operands of '<=' operator must be of numeric type.")
        
        return 'bool'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_GREATER_THAN_EQUAL(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")

        if left_type not in ['int', 'float']:
            raise SemanticError("Operands of '>=' operator must be of numeric type.")
        
        return 'bool'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_EQUAL(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")
        
        return 'bool'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_NOT_EQUAL(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        if left_type != right_type:
            raise SemanticError("Type mismatch in binary expression.")
        
        return 'bool'
    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_LOGICAL_AND(self, node):
        _, left, right = node
        left_type = self.visit(left)
        right_type = self.visit(right)

        if left_type != 'bool' or right_type != 'bool':
            raise SemanticError("Operands of '&&' operator must be of type 'bool'.")
        
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
        _, expression = node
        self.visit(expression)
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_DELAY(self, node):
        _, delay_time = node
        if not isinstance(delay_time[1], int):
            raise SemanticError(f"Delay time must be an integer.")
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_WIDTH(self, node):
        _, expression = node
        expr_type = self.visit(expression)
        if expr_type != 'int':
            raise SemanticError("Argument of 'WIDTH' instruction must be of type 'int'.")
        
    def visit_HEIGHT(self, node):
        _, expression = node
        expr_type = self.visit(expression)
        if expr_type != 'int':
            raise SemanticError("Argument of 'HEIGHT' instruction must be of type 'int'.")
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_READ_STATEMENT(self, node):
        variables = node[1]
        for var in variables:
            if self.symbol_table.lookup(var[1]) is None:
                raise SemanticError(f"Variable '{var[1]}' not declared.")
            
    #---------------------------------------------------------------------------------------------------------------------------------------
            
    def visit_RANDI_STATEMENT(self, node):
        _, variable = node
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
        condition, block = node[1], node[2]
        self.visit(condition)
        self.symbol_table.push_scope()
        self.visit(block)
        self.symbol_table.pop_scope()
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_RELATIONAL_OPERATOR(self, node):
        left_operand = node[1][0]
        right_operand = node[1][1]
        left_type = self.symbol_table.get_type(left_operand)
        right_type = self.symbol_table.get_type(right_operand)
        if left_type != right_type:
            raise SemanticError(f"Type mismatch in relational operator '{node[0]}': {left_type} vs {right_type}")
        
    #---------------------------------------------------------------------------------------------------------------------------------------        

    def visit_BLOCK(self, node):
        self.symbol_table.push_scope()
        for statement in node[1]:
            self.visit(statement)
        self.symbol_table.pop_scope()
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_IF(self, node):
        if len(node) == 4:
            _, condition, true_block, else_node = node
        elif len(node) == 3:
            _, condition, true_block = node
            else_node = None
        else:
            raise ValueError("Invalid IF node structure")

        self.visit(condition)
        self.symbol_table.enter_scope()
        self.visit(true_block)
        self.symbol_table.exit_scope()

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
        _, expression = node
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

# Open the file and read the contents into a string
with open(filename, 'r') as file:
    source_code = file.read()

try:
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    print("\n" + "-"*100+"\n\nAST: \n")
    print(ast)

    semantic_analyzer = SemanticAnalyzer(ast)
    for node in ast:
        semantic_analyzer.visit(node)
    
    print("\nSemantic analysis completed successfully!")

except LexerError as e:
    print(f"Error: {e}")
except ParserError as e:
    print(f"Error: {e}")
except SemanticError as e:
    print(f"Error: {e}")
    
print("\n" + "-"*100)