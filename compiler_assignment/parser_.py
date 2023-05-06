from lexer import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self.symbol_table = {}
        
###########################################################################################################################################

    def parse(self):
        program = []
        while self.current_index < len(self.tokens):
            program.append(self.parse_statement())
        return program
    
###########################################################################################################################################

    def parse_statement(self):
        if self.match("PIXELR_STATEMENT"):
            return self.parse_pixelr_statement()
        elif self.match("PIXEL_STATEMENT"):
            return self.parse_pixel_statement()
        elif self.check("TYPE_INT", "TYPE_BOOL", "TYPE_FLOAT", "TYPE_COLOUR"):
            return self.parse_declaration()
        elif self.match("IDENTIFIER") and self.match("ASSIGNMENT_OPERATOR"):
            identifier = self.previous().lexeme
            value = self.parse_expression()
            self.expect("SEMICOLON")
            return ("ASSIGNMENT", identifier, value)
        elif self.match("IF"):
            return self.parse_if()
        elif self.match("ELSE"):
            return self.parse_if()
        elif self.match("FUNCTION_DEF"):
            return self.parse_function_definition()
        elif self.match("IDENTIFIER") and self.check("OPEN_PAREN"):
            func_call = self.parse_function_call()
            self.expect("SEMICOLON")
            return func_call
        elif self.match("RETURN"):
            value = self.parse_expression()
            self.expect("SEMICOLON")
            return ("RETURN", value)
        elif self.match("PRINT_STATEMENT"):
            expression = self.parse_expression()
            self.expect("SEMICOLON")
            return ("PRINT", expression)
        elif self.match("DELAY_STATEMENT"):
            expression = self.parse_expression()
            self.expect("SEMICOLON")
            return ("DELAY", expression)
        elif self.match("PAD_WIDTH"):
            expression = self.parse_expression()
            self.expect("SEMICOLON")
            return ("WIDTH", expression)
        elif self.match("PAD_HEIGHT"):
            expression = self.parse_expression()
            self.expect("SEMICOLON")
            return ("HEIGHT", expression)
        elif self.match("READ_STATEMENT"):
            return self.parse_read_call()
        elif self.match("RANDI_STATEMENT"):
            return self.parse_randi_call()
        elif self.match("LET"):
            return self.parse_let_declaration()
        elif self.match("FOR"):
            return self.parse_for_statement()
        elif self.match("WHILE"):
            return self.parse_while_statement()
        else:
            raise ParserError(f"Invalid statement at token {self.tokens[self.current_index]}")

###########################################################################################################################################

    def parse_block(self):
        self.match("LEFT_BRACE")  # Use string "LEFT_BRACE" instead of Token.LEFT_BRACE

        block = []

        while not self.check("RIGHT_BRACE"):
            block.append(self.parse_statement())

        self.expect("RIGHT_BRACE")

        return ("BLOCK", block)
    
    def assignment(self):
        self.eat("ASSIGNMENT")
        return self.expression()
    
###########################################################################################################################################
    
    def parse_let_declaration(self):
        self.expect("IDENTIFIER")
        identifier = self.previous().lexeme

        # Check for existing declarations and raise an error if the identifier is already in use
        if identifier in self.symbol_table:
            raise ParserError(f"Variable '{identifier}' is already declared")

        self.expect("COLON")
        self.expect("TYPE_INT", "TYPE_BOOL", "TYPE_FLOAT", 'TYPE_COLOUR')
        var_type = self.previous().token_type

        self.expect("ASSIGNMENT_OPERATOR")
        value = self.parse_expression()
        self.expect("SEMICOLON")

        # Add the variable to the symbol table
        self.symbol_table[identifier] = var_type

        return ("DECLARATION", var_type, identifier, value)

###########################################################################################################################################
    
    def parse_declaration(self):
        self.match("LET")
        self.expect("IDENTIFIER")
        identifier = self.previous().lexeme

        # Check for existing declarations and raise an error if the identifier is already in use
        if identifier in self.symbol_table:
            raise ParserError(f"Variable '{identifier}' is already declared")

        # Add the variable to the symbol table
        self.symbol_table[identifier] = "TYPE_ANY"

        self.expect("COLON")
        var_type = self.tokens[self.current_index].token_type

        if var_type == "TYPE_COLOUR":
            self.match("TYPE_COLOUR")
            self.expect("ASSIGNMENT_OPERATOR")
            self.expect("COLOR_LITERAL")
            value = ("COLOR_LITERAL", self.previous().lexeme)
        else:
            self.match(var_type)
            self.expect("ASSIGNMENT_OPERATOR")
            value = self.parse_expression()

        self.expect("SEMICOLON")
        return ("DECLARATION", var_type, identifier, value)

###########################################################################################################################################

    def parse_if(self):
        self.match("IF")
        self.expect("OPEN_PAREN")
        condition = self.parse_condition()
        self.expect("CLOSE_PAREN")
        true_branch = self.parse_block()
        false_branch = None

        if self.check("ELSE"):
            self.match("ELSE")
            false_branch = self.parse_block()

        return ("IF", condition, true_branch, ("ELSE", false_branch)) if false_branch else ("IF", condition, true_branch)

###########################################################################################################################################
    
    def parse_condition(self):
        left = self.parse_logical_or()

        while self.match("EQUALITY_OPERATOR") or self.match("RELATIONAL_OPERATOR"):
            op = self.previous().token_type
            right = self.parse_logical_or()
            left = (op, left, right)

        return left
    
###########################################################################################################################################

    def parse_logical_or(self):
        left = self.parse_logical_and()

        while self.match("LOGICAL_OR"):
            op = self.previous().token_type
            right = self.parse_logical_and()
            left = (op, left, right)

        return left
    
###########################################################################################################################################

    def parse_logical_and(self):
        left = self.parse_comparison()

        while self.match("LOGICAL_AND"):
            op = self.previous().token_type
            right = self.parse_comparison()
            left = (op, left, right)

        return left

###########################################################################################################################################

    def parse_expression(self):
        left = self.parse_term()

        while self.match("PLUS") or self.match("MINUS") or self.match("MUL") or self.match("DIV") or self.match("MOD") or self.match("EQUALITY_OPERATOR") or self.match("RELATIONAL_OPERATOR") or self.match("LOGICAL_OPERATOR"):
            op = self.previous().token_type
            right = self.parse_term()
            left = (op, left, right)

        return left

###########################################################################################################################################

    def parse_term(self):
        left = self.parse_factor()

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

        while not self.check("CLOSE_PAREN"):
            if len(parameters) > 0:
                self.expect("COMMA")
            self.expect("IDENTIFIER")
            param_name = self.previous().lexeme
            if self.match("COLON"):
                param_type = self.tokens[self.current_index].token_type
                self.match(param_type)
                parameters.append((param_name, param_type))
            else:
                parameters.append(param_name)

        self.expect("CLOSE_PAREN")
        
        # Add these lines to handle the "->" syntax and return type
        if self.match("MINUS") and self.match("RELATIONAL_OPERATOR"):
            return_type = self.tokens[self.current_index].token_type
            self.match(return_type)
        else:
            return_type = None

        body = self.parse_block()
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
        if self.match("IDENTIFIER"):
            if self.check("OPEN_PAREN"):
                if self.previous().lexeme == "__read":
                    return self.parse_read_call()
                else:
                    return self.parse_function_call()
            else:
                return ("IDENTIFIER", self.previous().lexeme)
        elif self.match("INTEGER_LITERAL"):
            return ("INTEGER_LITERAL", int(self.previous().lexeme))
        elif self.match("FLOAT_LITERAL"):
            return ("FLOAT_LITERAL", float(self.previous().lexeme))
        elif self.match("BOOLEAN_LITERAL_TRUE") or self.match("BOOLEAN_LITERAL_FALSE"):
            return ("BOOLEAN_LITERAL", self.previous().token_type == "BOOLEAN_LITERAL_TRUE")
        elif self.match("STRING_LITERAL"):
            return ("STRING_LITERAL", self.previous().lexeme)
        elif self.match("OPEN_PAREN"):
            expr = self.parse_expression()
            self.expect("CLOSE_PAREN")
            return expr
        elif self.match("COLOR_LITERAL"):
            return ("COLOR_LITERAL", self.previous().lexeme)
        elif self.match("READ_STATEMENT"):
            return self.parse_read_call()
        else:
            raise ParserError(f"Invalid factor at token {self.tokens[self.current_index]}")
        
###########################################################################################################################################

    def parse_comparison(self):
        left = self.parse_expression()

        while self.match("EQUALITY_OPERATOR") or self.match("RELATIONAL_OPERATOR"):
            op = self.previous().token_type
            right = self.parse_expression()
            left = (op, left, right)

        return left
    
###########################################################################################################################################

    def parse_while_statement(self):
        self.match("WHILE")
        self.expect("OPEN_PAREN")
        condition = self.parse_condition()
        self.expect("CLOSE_PAREN")
        body = self.parse_block()
        return ("WHILE", condition, body)

###########################################################################################################################################
    
    def parse_read_call(self):
        function_name = self.previous().lexeme
        self.expect("OPEN_PAREN")
        identifiers = []
        identifiers.append(self.parse_expression())
        while self.match("COMMA"):
            identifiers.append(self.parse_expression())
        self.expect("CLOSE_PAREN")
        self.expect("SEMICOLON")
        return ("READ_STATEMENT", identifiers)
    
###########################################################################################################################################
  
    def parse_randi_call(self):
        function_name = self.previous().lexeme
        self.expect("OPEN_PAREN")
        argument = self.parse_expression()
        self.expect("CLOSE_PAREN")
        self.expect("SEMICOLON")
        return ("RANDI_STATEMENT", argument)

###########################################################################################################################################
    
    def parse_pixel_statement(self):
        pixel_function_name = self.previous().lexeme
        arguments = []

        self.expect("OPEN_PAREN")

        while not self.check("CLOSE_PAREN"):
            if len(arguments) > 0:
                self.expect("COMMA")
            arguments.append(self.parse_expression())

        self.expect("CLOSE_PAREN")
        self.expect("SEMICOLON")

        return ("PIXEL_STATEMENT", arguments)

    def parse_pixelr_statement(self):
        pixel_function_name = self.previous().lexeme
        arguments = []

        self.expect("OPEN_PAREN")

        while not self.check("CLOSE_PAREN"):
            if len(arguments) > 0:
                self.expect("COMMA")
            arguments.append(self.parse_expression())

        self.expect("CLOSE_PAREN")
        self.expect("SEMICOLON")

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
        if self.current_index < len(self.tokens) and self.tokens[self.current_index].token_type == token_type:
            self.current_index += 1
            return True
        return False
    
###########################################################################################################################################

    def expect(self, *token_types):
        if not any(self.match(token_type) for token_type in token_types):
            if self.current_index < len(self.tokens):
                found_token_type = self.tokens[self.current_index].token_type
            else:
                found_token_type = "EOF"
            raise ParserError(f"Expected one of {', '.join(token_types)}, found '{found_token_type}'")

###########################################################################################################################################

    def check(self, *token_types):
        return self.current_index < len(self.tokens) and self.tokens[self.current_index].token_type in token_types
    
###########################################################################################################################################

    def previous(self):
        return self.tokens[self.current_index - 1]
    
###########################################################################################################################################

class ParserError(Exception):
    pass

###########################################################################################################################################

# Usage:
source_code = """
let x: int = 5;
"""

#try:
#    lexer = Lexer(source_code)
#    tokens = lexer.tokenize()
#    print("\nLexer:\n")
#    for token in tokens:
#        print(token)
#
#    parser = Parser(tokens)
#    parsed_program = parser.parse()
#    print("\n" + "-"*100)
#    print("\nParsed program:\n")
#    print(parsed_program)
#
#except LexerError as e:
#    print(f"Error: {e}")
#except ParserError as e:
#    print(f"Error: {e}")
#
#print("\n" + "-"*100)