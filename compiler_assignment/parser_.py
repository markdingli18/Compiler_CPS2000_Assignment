# Import all definitions from the lexer code
from lexer import *

class Parser:
    def __init__(self, tokens):
        # Initialize the Parser object with a list of tokens
        self.tokens = tokens
        # Initialize the current index to zero
        self.current_index = 0
        # Initialize an empty dictionary to store symbol table information
        self.symbol_table = {}
        
###########################################################################################################################################

    def parse(self):
        # Initialize an empty list to store the program statements
        program = []
        # Parse each statement until the end of the token list is reached
        while self.current_index < len(self.tokens):
            # Append the parsed statement to the program list
            program.append(self.parse_statement())
        # Return the completed program list
        return program
    
###########################################################################################################################################

    def parse_statement(self):
        # Parses a single statement and returns the corresponding AST node based on the type of statement
        if self.match("PIXELR_STATEMENT"):
            return self.parse_pixelr_statement()
        elif self.match("PIXEL_STATEMENT"):
            return self.parse_pixel_statement()
        elif self.check("TYPE_INT", "TYPE_BOOL", "TYPE_FLOAT", "TYPE_COLOUR"):
            # Parse variable declaration
            return self.parse_declaration()
        elif self.match("IDENTIFIER") and self.match("ASSIGNMENT_OPERATOR"):
            # Parse variable assignment
            identifier = self.previous().lexeme
            value = self.parse_expression()
            self.expect("SEMICOLON")
            return ("ASSIGNMENT", identifier, value)
        elif self.match("IF"):
            # Parse if statement
            return self.parse_if()
        elif self.match("ELSE"):
            # Parse else statement
            return self.parse_if()
        elif self.match("FUNCTION_DEF"):
            # Parse function definition
            return self.parse_function_definition()
        elif self.match("IDENTIFIER") and self.check("OPEN_PAREN"):
            # Parse function call
            func_call = self.parse_function_call()
            self.expect("SEMICOLON")
            return func_call
        elif self.match("RETURN"):
            # Parse return statement
            value = self.parse_expression()
            self.expect("SEMICOLON")
            return ("RETURN", value)
        elif self.match("PRINT_STATEMENT"):
            # Parse print statement
            expression = self.parse_expression()
            self.expect("SEMICOLON")
            return ("PRINT", expression)
        elif self.match("DELAY_STATEMENT"):
            # Parse delay statement
            expression = self.parse_expression()
            self.expect("SEMICOLON")
            return ("DELAY", expression)
        elif self.match("PAD_WIDTH"):
            # Parse pad width statement
            expression = self.parse_expression()
            self.expect("SEMICOLON")
            return ("WIDTH", expression)
        elif self.match("PAD_HEIGHT"):
            # Parse pad height statement
            expression = self.parse_expression()
            self.expect("SEMICOLON")
            return ("HEIGHT", expression)
        elif self.match("READ_STATEMENT"):
            # Parse read statement
            return self.parse_read_call()
        elif self.match("RANDI_STATEMENT"):
            # Parse randi statement
            return self.parse_randi_call()
        elif self.match("LET"):
            # Parse let statement
            return self.parse_let_declaration()
        elif self.match("FOR"):
            # Parse for statement
            return self.parse_for_statement()
        elif self.match("WHILE"):
            # Parse while statement
            return self.parse_while_statement()
        else:
            raise ParserError(f"Invalid statement at token {self.tokens[self.current_index]}")

###########################################################################################################################################

    # Parse a block of statements enclosed in braces
    def parse_block(self):
        # Match the left brace token to enter the block
        self.match("LEFT_BRACE")

        # Initialize an empty list to store statements in the block
        block = []

        # Parse statements in the block until the right brace token is found
        while not self.check("RIGHT_BRACE"):
            block.append(self.parse_statement())

        # Match the right brace token to exit the block
        self.expect("RIGHT_BRACE")

        # Return the block as a tuple
        return ("BLOCK", block)
    
    def assignment(self):
        self.eat("ASSIGNMENT")

        # Parse the expression on the right side of the assignment operator
        return self.expression()

###########################################################################################################################################
    
    def parse_let_declaration(self):
        # Expect an identifier for the variable name
        self.expect("IDENTIFIER")
        identifier = self.previous().lexeme

        # Check for existing declarations and raise an error if the identifier is already in use
        if identifier in self.symbol_table:
            raise ParserError(f"Variable '{identifier}' is already declared")

        # Expect a colon to denote the variable type
        self.expect("COLON")

        # Expect a type keyword for the variable type
        self.expect("TYPE_INT", "TYPE_BOOL", "TYPE_FLOAT", 'TYPE_COLOUR')
        var_type = self.previous().token_type

        # Expect an assignment operator to assign a value to the variable
        self.expect("ASSIGNMENT_OPERATOR")

        # Parse the expression on the right side of the assignment operator
        value = self.parse_expression()

        # Expect a semicolon to terminate the statement
        self.expect("SEMICOLON")

        # Add the variable to the symbol table
        self.symbol_table[identifier] = var_type

        # Return a tuple containing the declaration information
        return ("DECLARATION", var_type, identifier, value)

###########################################################################################################################################
    
    def parse_declaration(self):
        # Match the 'let' keyword to indicate a variable declaration
        self.match("LET")

        # Expect an identifier token after the 'let' keyword
        self.expect("IDENTIFIER")
        identifier = self.previous().lexeme

        # Check for existing declarations and raise an error if the identifier is already in use
        if identifier in self.symbol_table:
            raise ParserError(f"Variable '{identifier}' is already declared")

        # Add the variable to the symbol table with a type of 'TYPE_ANY'
        self.symbol_table[identifier] = "TYPE_ANY"

        # Expect a colon token to separate the variable name from its type
        self.expect("COLON")

        # Expect a type token after the colon
        var_type = self.tokens[self.current_index].token_type

        # If the type is 'TYPE_COLOUR', expect a color literal after the assignment operator
        if var_type == "TYPE_COLOUR":
            self.match("TYPE_COLOUR")
            self.expect("ASSIGNMENT_OPERATOR")
            self.expect("COLOR_LITERAL")
            value = ("COLOR_LITERAL", self.previous().lexeme)
        # Otherwise, expect an expression after the assignment operator
        else:
            self.match(var_type)
            self.expect("ASSIGNMENT_OPERATOR")
            value = self.parse_expression()

        # Expect a semicolon to terminate the declaration statement
        self.expect("SEMICOLON")

        # Update the variable type in the symbol table
        self.symbol_table[identifier] = var_type

        # Return a tuple with the declaration information
        return ("DECLARATION", var_type, identifier, value)

###########################################################################################################################################

    def parse_if(self):
        # Match the "IF" keyword
        self.match("IF")

        # Expect an open parenthesis and parse the condition
        self.expect("OPEN_PAREN")
        condition = self.parse_condition()
        self.expect("CLOSE_PAREN")

        # Parse the true branch of the if statement
        true_branch = self.parse_block()

        # Initialize the false branch to None
        false_branch = None

        # If an "ELSE" keyword is present, parse the false branch
        if self.check("ELSE"):
            self.match("ELSE")
            false_branch = self.parse_block()

        # Return a tuple representing the condition, true branch, and (optionally) false branch
        return ("IF", condition, true_branch, ("ELSE", false_branch)) if false_branch else ("IF", condition, true_branch)   


###########################################################################################################################################
    
    def parse_condition(self):
        # Parse the left side of the condition
        left = self.parse_logical_or()

        # Parse any additional comparison operators in the condition
        while self.match("EQUALITY_OPERATOR") or self.match("RELATIONAL_OPERATOR"):
            # Store the operator and parse the right side of the comparison
            op = self.previous().token_type
            right = self.parse_logical_or()

            # Combine the left and right sides of the comparison with the operator
            left = (op, left, right)

        # Return the fully-parsed condition
        return left
    
###########################################################################################################################################

    def parse_logical_or(self):
        # Parse the left operand
        left = self.parse_logical_and()

        # Parse subsequent right operands while the current token is a logical OR operator
        while self.match("LOGICAL_OR"):
            # Get the operator and parse the next operand
            op = self.previous().token_type
            right = self.parse_logical_and()
            
            # Combine the left and right operands with the logical OR operator
            left = (op, left, right)

        # Return the resulting expression
        return left
    
###########################################################################################################################################

    def parse_logical_and(self):
        # Parse the left operand
        left = self.parse_comparison()

        # Parse subsequent right operands while the current token is a logical AND operator
        while self.match("LOGICAL_AND"):
            # Get the operator and parse the next operand
            op = self.previous().token_type
            right = self.parse_comparison()

            # Combine the left and right operands with the logical AND operator
            left = (op, left, right)

        # Return the resulting expression
        return left

###########################################################################################################################################

    def parse_expression(self):
        left = self.parse_term()

        # Keep parsing and combining terms as long as there are operators
        while self.match("PLUS") or self.match("MINUS") or self.match("MUL") or self.match("DIV") or self.match("MOD") or self.match("EQUALITY_OPERATOR") or self.match("RELATIONAL_OPERATOR") or self.match("LOGICAL_OPERATOR"):
            op = self.previous().token_type
            right = self.parse_term()
            left = (op, left, right)

        return left

###########################################################################################################################################

    def parse_term(self):
        left = self.parse_factor()

        # Keep parsing and combining factors as long as there are operators
        while self.match("EQUALITY_OPERATOR") or self.match("RELATIONAL_OPERATOR") or self.match("LOGICAL_OPERATOR"):
            op = self.previous().token_type
            right = self.parse_factor()
            left = (op, left, right)

        return left
    
###########################################################################################################################################

    def parse_function_definition(self):
        self.expect("IDENTIFIER")
        function_name = self.previous().lexeme
        self.expect("OPEN_PAREN")
        parameters = []

        # Parse the function parameters
        while not self.check("CLOSE_PAREN"):
            if len(parameters) > 0:
                self.expect("COMMA")
            self.expect("IDENTIFIER")
            param_name = self.previous().lexeme

            # Check if a type annotation is present for the parameter
            if self.match("COLON"):
                param_type = self.tokens[self.current_index].token_type
                self.match(param_type)
                parameters.append((param_name, param_type))
            else:
                parameters.append(param_name)

        self.expect("CLOSE_PAREN")
        
        # Check if a return type annotation is present
        if self.match("MINUS") and self.match("RELATIONAL_OPERATOR"):
            return_type = self.tokens[self.current_index].token_type
            self.match(return_type)
        else:
            return_type = None

        # Parse the function body
        body = self.parse_block()

        # Return a tuple representing the function definition
        return ("FUNCTION_DEF", function_name, parameters, return_type, body)
    
    def parse_function_call(self):
        function_name = self.previous().lexeme
        self.expect("OPEN_PAREN")
        arguments = []

        while not self.check("CLOSE_PAREN"):
            if len(arguments) > 0:
                self.expect("COMMA")
            arguments.append(self.parse_expression())

        self.expect("CLOSE_PAREN")
        return ("FUNCTION_CALL", function_name, arguments)

###########################################################################################################################################

    def parse_factor(self):
        # Parse an identifier
        if self.match("IDENTIFIER"):
            # Check if it's a function call
            if self.check("OPEN_PAREN"):
                # Check if it's the read function
                if self.previous().lexeme == "__read":
                    return self.parse_read_call()
                else:
                    return self.parse_function_call()
            else:
                return ("IDENTIFIER", self.previous().lexeme)
        # Parse an integer literal
        elif self.match("INTEGER_LITERAL"):
            return ("INTEGER_LITERAL", int(self.previous().lexeme))
        # Parse a float literal
        elif self.match("FLOAT_LITERAL"):
            return ("FLOAT_LITERAL", float(self.previous().lexeme))
        # Parse a boolean literal
        elif self.match("BOOLEAN_LITERAL_TRUE") or self.match("BOOLEAN_LITERAL_FALSE"):
            return ("BOOLEAN_LITERAL", self.previous().token_type == "BOOLEAN_LITERAL_TRUE")
        # Parse a string literal
        elif self.match("STRING_LITERAL"):
            return ("STRING_LITERAL", self.previous().lexeme)
        # Parse an expression in parentheses
        elif self.match("OPEN_PAREN"):
            expr = self.parse_expression()
            self.expect("CLOSE_PAREN")
            return expr
        # Parse a color literal
        elif self.match("COLOR_LITERAL"):
            return ("COLOR_LITERAL", self.previous().lexeme)
        # Parse a read statement
        elif self.match("READ_STATEMENT"):
            return self.parse_read_call()
        else:
            raise ParserError(f"Invalid factor at token {self.tokens[self.current_index]}")
        
###########################################################################################################################################

    def parse_comparison(self):
        # Parse the left side of the comparison
        left = self.parse_expression()

        # Continue parsing the right side of the comparison as long as there are more comparison operators
        while self.match("EQUALITY_OPERATOR") or self.match("RELATIONAL_OPERATOR"):
            # Get the comparison operator
            op = self.previous().token_type
            
            # Parse the right side of the comparison
            right = self.parse_expression()
            
            # Combine the left and right sides of the comparison with the operator
            left = (op, left, right)

        # Return the comparison expression
        return left

    ###########################################################################################################################################

    def parse_while_statement(self):
        # Match the 'while' keyword
        self.match("WHILE")
        
        # Parse the condition expression inside the parentheses
        self.expect("OPEN_PAREN")
        condition = self.parse_condition()
        self.expect("CLOSE_PAREN")
        
        # Parse the block of statements inside the loop body
        body = self.parse_block()
        
        # Return the while loop expression
        return ("WHILE", condition, body)

###########################################################################################################################################
    
    def parse_read_call(self):
        function_name = self.previous().lexeme
        
        # Parse the argument(s) to the read function
        self.expect("OPEN_PAREN")
        identifiers = []
        identifiers.append(self.parse_expression())
        while self.match("COMMA"):
            identifiers.append(self.parse_expression())
        self.expect("CLOSE_PAREN")
        
        # Make sure the statement ends with a semicolon
        self.expect("SEMICOLON")
        
        # Return a tuple representing the read statement
        return ("READ_STATEMENT", identifiers)

    
###########################################################################################################################################
  
    def parse_randi_call(self):
        function_name = self.previous().lexeme
        
        # Parse the argument to the randi function
        self.expect("OPEN_PAREN")
        argument = self.parse_expression()
        self.expect("CLOSE_PAREN")
        
        # Make sure the statement ends with a semicolon
        self.expect("SEMICOLON")
        
        # Return a tuple representing the randi statement
        return ("RANDI_STATEMENT", argument)

###########################################################################################################################################
    
    def parse_pixel_statement(self):
        pixel_function_name = self.previous().lexeme
        arguments = []

        # Parse the function arguments
        self.expect("OPEN_PAREN")
        while not self.check("CLOSE_PAREN"):
            if len(arguments) > 0:
                self.expect("COMMA")
            arguments.append(self.parse_expression())
        self.expect("CLOSE_PAREN")
        self.expect("SEMICOLON")

        # Return a tuple with the function name and its arguments
        return ("PIXEL_STATEMENT", arguments)

    def parse_pixelr_statement(self):
        pixel_function_name = self.previous().lexeme
        arguments = []

        # Parse the function arguments
        self.expect("OPEN_PAREN")
        while not self.check("CLOSE_PAREN"):
            if len(arguments) > 0:
                self.expect("COMMA")
            arguments.append(self.parse_expression())
        self.expect("CLOSE_PAREN")
        self.expect("SEMICOLON")

        # Return a tuple with the function name and its arguments
        return ("PIXELR_STATEMENT", arguments)
    
###########################################################################################################################################

    def parse_for_statement(self):
        self.match("FOR")
        self.expect("OPEN_PAREN")

        # Parse initialization (declaration or assignment)
        if self.match("LET"):
            if self.check("IDENTIFIER"):
                initialization = self.parse_declaration()
            else:
                raise ParserError(f"Invalid variable name in for loop at token {self.tokens[self.current_index]}")
        elif self.match("IDENTIFIER") and self.match("ASSIGNMENT_OPERATOR"):
            identifier = self.previous().lexeme
            value = self.parse_expression()
            self.expect("SEMICOLON")
            initialization = ("ASSIGNMENT", identifier, value)
        else:
            raise ParserError(f"Invalid initialization in for loop at token {self.tokens[self.current_index]}")

        # Parse condition
        condition = self.parse_condition()
        self.expect("SEMICOLON")

        # Parse update
        if self.match("IDENTIFIER") and self.match("ASSIGNMENT_OPERATOR"):
            identifier = self.previous().lexeme
            value = self.parse_expression()
            update = ("ASSIGNMENT", identifier, value)
        else:
            raise ParserError(f"Invalid update in for loop at token {self.tokens[self.current_index]}")

        self.expect("CLOSE_PAREN")

        # Parse body
        body = self.parse_block()

        return ("FOR", initialization, condition, update, body)

###########################################################################################################################################

    def match(self, token_type):
        # Check if the current token matches the expected token type, and advance the current index if it does
        if self.current_index < len(self.tokens) and self.tokens[self.current_index].token_type == token_type:
            self.current_index += 1
            return True
        return False

###########################################################################################################################################

    def expect(self, *token_types):
        # Check if the next token matches any of the expected token types
        if not any(self.match(token_type) for token_type in token_types):
            if self.current_index < len(self.tokens):
                found_token_type = self.tokens[self.current_index].token_type
            else:
                found_token_type = "EOF"
            raise ParserError(f"Expected one of {', '.join(token_types)}, found '{found_token_type}'")

###########################################################################################################################################

    def check(self, *token_types):
        # Check if the next token matches any of the expected token types
        return self.current_index < len(self.tokens) and self.tokens[self.current_index].token_type in token_types

###########################################################################################################################################

    def previous(self):
        # Return the previous token from the list of tokens
        return self.tokens[self.current_index - 1]
    
###########################################################################################################################################

class ParserError(Exception):
    pass

###########################################################################################################################################

# Usage:

# Specify the name of the file
filename = 'input.txt'

# Open the file and read the contents into a string
with open(filename, 'r') as file:
    source_code = file.read()
    
# Attempt to tokenize and parse the source code
#try:
#    # Tokenize the source code
#    lexer = Lexer(source_code)
#    tokens = lexer.tokenize()#

#    # Parse the tokens into an abstract syntax tree
#    parser = Parser(tokens)
#    parsed_program = parser.parse()#

#    # Print the parsed program
#    print("\n" + "-"*100)
#    print("\nParsed program:\n")
#    print(parsed_program)#

## Catch and report lexer errors
#except LexerError as e:
#    print(f"Error: {e}")#

## Catch and report parser errors
#except ParserError as e:
#    print(f"Error: {e}")#

#print("\n" + "-"*100)