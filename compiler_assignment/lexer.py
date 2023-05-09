class Token:
    def __init__(self, token_type, lexeme):
        # Store the token type and lexeme as instance variables
        self.token_type = token_type
        self.lexeme = lexeme

    def __str__(self):
        # Return a string representation of the token
        return f"{self.token_type}({self.lexeme})"

###########################################################################################################################################

# Define Lexer class
class Lexer:
            
    # Dictionary of keywords and their corresponding token types
    KEYWORDS = {
        "if": "IF",
        "else": "ELSE",
        "while": "WHILE",
        "for": "FOR",
        "return": "RETURN",
        "fun": "FUNCTION_DEF",
        "true": "BOOLEAN_LITERAL_TRUE",
        "false": "BOOLEAN_LITERAL_FALSE",
        "not": "LOGICAL_OPERATOR", 
        "__read": "READ_STATEMENT",
        "__print": "PRINT_STATEMENT",
        "__delay": "DELAY_STATEMENT", 
        "__randi": "RANDI_STATEMENT",
        "__width": "PAD_WIDTH", 
        "__height": "PAD_HEIGHT", 
        'let': 'LET',
        "__pixelr": "PIXELR_STATEMENT",
        "__pixel": "PIXEL_STATEMENT",
        'int': 'TYPE_INT',
        'bool': 'TYPE_BOOL',
        'float': 'TYPE_FLOAT',
        'colour': 'TYPE_COLOUR',
        '->': 'FUNCTION_ARROW'
    }
    
    def __init__(self, source_code):
        # Store the source code and initialize other class attributes
        self.source_code = source_code
        self.transition_table = self.build_transition_table()
        self.current_state = 0
        self.position = 0
        self.open_quote = None

    # Define a method for the transition table
    def build_transition_table(self):
        transition_table = {}

        # Define the states and input characters
        states = range(32)
        input_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*/%=<>!#()[]{},.;:'\" \t\n"

        # Initialize all transitions to -1
        for state in states:
            for char in input_characters:
                transition_table[(state, char)] = -1

        # Transitions for identifiers
        for char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            transition_table[(0, char)] = 1
        for char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
            transition_table[(1, char)] = 1
            
        transition_table[(0, '_')] = 1
        transition_table[(1, '_')] = 1

        # Transitions for integer literals
        for char in "0123456789":
            transition_table[(0, char)] = 2
            transition_table[(2, char)] = 2

        # Transitions for operators
        operators = "+-*%"
        for op in operators:
            transition_table[(0, op)] = 3

        # Transitions for division and comments
        transition_table[(0, '/')] = 3
        transition_table[(3, '/')] = 22  # Start of single-line comment
        transition_table[(3, '*')] = 24  # Start of multi-line comment
        transition_table[(3, '=')] = 23  # Division assignment operator (e.g. /=)
        
        # Transitions for single-line comments
        transition_table[(22, '\n')] = 37  # End of single-line comment

        for char in input_characters:
            if char != '\n':
                transition_table[(22, char)] = 22
                
        # Transitions for multi-line comments
        transition_table[(24, '*')] = 25
        transition_table[(25, '/')] = 37  # End of multi-line comment

        for char in input_characters:
            if char != '*' and char != '/':
                transition_table[(24, char)] = 24
                transition_table[(25, char)] = 24

        # Transitions for delimiters
        delimiters = "(){},.;[]"
        for delimiter in delimiters:
            transition_table[(0, delimiter)] = 4

        # Transitions for relational operators
        transition_table[(0, '<')] = 9
        transition_table[(9, '=')] = 10
        transition_table[(0, '>')] = 11
        transition_table[(11, '=')] = 12
        transition_table[(0, '=')] = 5
        transition_table[(5, '=')] = 6
        transition_table[(0, '!')] = 7
        transition_table[(7, '=')] = 8

        # Transitions for logical operators
        transition_table[(0, 'a')] = 15
        transition_table[(15, 'n')] = 16
        transition_table[(16, 'd')] = 18
        transition_table[(0, 'o')] = 17
        transition_table[(17, 'r')] = 18

        # Transitions for string literals
        transition_table[(0, '"')] = 19
        for char in input_characters:
            if char == '"':
                transition_table[(19, char)] = 20
            else:
                transition_table[(19, char)] = 19
                transition_table[(20, char)] = 20

        for char in input_characters:
            if char != '*' and char != '/':
                transition_table[(25, char)] = 25
                transition_table[(26, char)] = 25
                
        # Transitions for quotes        
        transition_table[(0, "'")] = 21
        for char in input_characters:
            if char == "'":
                transition_table[(21, char)] = 19
            else:
                transition_table[(21, char)] = 21
                transition_table[(19, char)] = 19

        # Transitions for boolean literals
        transition_table[(0, 't')] = 28
        transition_table[(28, 'r')] = 29
        transition_table[(29, 'u')] = 30
        transition_table[(30, 'e')] = 31

        # Transitions for 'false' keyword
        transition_table[(0, 'f')] = 25
        transition_table[(25, 'a')] = 26
        transition_table[(26, 'l')] = 27
        transition_table[(27, 's')] = 28
        transition_table[(28, 'e')] = 29
        
        # Transitions for assignment and equality operators
        transition_table[(0, '=')] = 5
        transition_table[(5, '=')] = 6
        
        # Transitions for arrays and dictionaries
        transition_table[(0, '[')] = 38
        transition_table[(0, '{')] = 39
        transition_table[(38, ']')] = 40
        transition_table[(39, '}')] = 41

        # Transitions for function calls
        transition_table[(0, '(')] = 45
        transition_table[(0, ')')] = 46
        
        # Transitions for colon
        transition_table[(0, ':')] = 41         

        # Transitions for whitespace
        for char in " \t\n":
            transition_table[(0, char)] = 37
            transition_table[(37, char)] = 37
        
        # Transitions for __read statement
        transition_table[(0, '_')] = 61  
        transition_table[(61, '_')] = 62
        transition_table[(62, 'r')] = 63
        transition_table[(63, 'e')] = 64
        transition_table[(64, 'a')] = 65
        transition_table[(65, 'd')] = 66
        
        # Transitions for __randi statement
        transition_table[(63, 'a')] = 67
        transition_table[(67, 'n')] = 68
        transition_table[(68, 'd')] = 69
        transition_table[(69, 'i')] = 70
        
        # Transitions for __print statement
        transition_table[(0, '_')] = 61  
        transition_table[(61, '_')] = 62
        transition_table[(62, 'p')] = 67 
        transition_table[(67, 'r')] = 68
        transition_table[(68, 'i')] = 69
        transition_table[(69, 'n')] = 70
        transition_table[(70, 't')] = 71

        # Transitions for __pixel & __pixelr 
        transition_table[(0, '_')] = 61
        transition_table[(61, '_')] = 62
        transition_table[(62, 'p')] = 67
        transition_table[(67, 'i')] = 68
        transition_table[(68, 'x')] = 69
        transition_table[(69, 'e')] = 70
        transition_table[(70, 'l')] = 72
        transition_table[(72, 'r')] = 74

        # Transitions for __delay statement
        transition_table[(0, '_')] = 61  
        transition_table[(61, '_')] = 62
        transition_table[(62, 'd')] = 63
        transition_table[(63, 'e')] = 64
        transition_table[(64, 'l')] = 65
        transition_table[(65, 'a')] = 66
        transition_table[(66, 'y')] = 67
        
        # Transitions for __width statement
        transition_table[(0, '_')] = 61  
        transition_table[(61, '_')] = 62
        transition_table[(62, 'w')] = 65
        transition_table[(65, 'i')] = 66
        transition_table[(66, 'd')] = 67
        transition_table[(67, 't')] = 68
        transition_table[(68, 'h')] = 69
        
         # Transitions for __height statement
        transition_table[(0, '_')] = 61  
        transition_table[(61, '_')] = 62
        transition_table[(62, 'h')] = 63
        transition_table[(63, 'e')] = 64
        transition_table[(64, 'i')] = 65
        transition_table[(65, 'g')] = 66
        transition_table[(66, 'h')] = 67
        transition_table[(67, 't')] = 68

        # Transitions for float literals
        for char in "0123456789":
            transition_table[(0, char)] = 2
            transition_table[(2, char)] = 2

        transition_table[(2, '.')] = 73
        for char in "0123456789":
            transition_table[(73, char)] = 124
            transition_table[(124, char)] = 124

        transition_table[(73, '.')] = 123
        transition_table[(123, '0123456789')] = 124
        transition_table[(124, '0123456789')] = 124

        # Transitions for colour literals
        transition_table[(0, '#')] = 54
        for char in "0123456789abcdefABCDEF":
            transition_table[(54, char)] = 55
            transition_table[(55, char)] = 56
            transition_table[(56, char)] = 57
            transition_table[(57, char)] = 58
            transition_table[(58, char)] = 59
            transition_table[(59, char)] = 60
            
        # Transitions for bool      
        transition_table[(0, 'b')] = 82
        transition_table[(82, 'o')] = 83
        transition_table[(83, 'o')] = 84
        transition_table[(84, 'l')] = 85

        # Transitions for colour      
        transition_table[(0, 'c')] = 86
        transition_table[(86, 'o')] = 87
        transition_table[(87, 'l')] = 88
        transition_table[(88, 'o')] = 89
        transition_table[(89, 'u')] = 90
        transition_table[(90, 'r')] = 91
        
        # Transitions for if and else
        transition_table[(0, 'i')] = 109
        transition_table[(109, 'f')] = 110
        transition_table[(0, 'e')] = 111
        transition_table[(111, 'l')] = 112
        transition_table[(112, 's')] = 113
        transition_table[(113, 'e')] = 114
        
        # Transitions for int
        transition_table[(0, 'i')] = 109
        transition_table[(109, 'n')] = 110
        transition_table[(110, 't')] = 111

        # Transitions for float 
        transition_table[(0, 'f')] = 100
        transition_table[(100, 'l')] = 101
        transition_table[(101, 'o')] = 102
        transition_table[(102, 'a')] = 103
        transition_table[(103, 't')] = 104 

        # Transitions for false
        transition_table[(100, 'a')] = 105
        transition_table[(105, 'l')] = 106
        transition_table[(106, 's')] = 107
        transition_table[(107, 'e')] = 108

        # For loop transitions
        transition_table[(100, 'o')] = 111
        transition_table[(111, 'r')] = 112
        
        # Transitions for function definitions
        transition_table[(100, 'u')] = 101
        transition_table[(101, 'n')] = 102
        transition_table[(102, '(')] = 103
        transition_table[(106, '')] = 104
        transition_table[(104, ')')] = 105
        transition_table[(105, '')] = 106
        transition_table[(1, '-')] = 200
        transition_table[(200, '>')] = 201

        return transition_table

###########################################################################################################################################

    # Get the next token from the source code
    def get_next_char(self):
        if self.position < len(self.source_code):
            # Get the character at the current position in the source code
            char = self.source_code[self.position]

            # Check if an open quote is present and if the current character is an escape character
            if self.open_quote and char == "\\":
                # Move to the next character
                self.position += 1
                # Get the next character if present, else set it to None
                next_char = self.source_code[self.position] if self.position < len(self.source_code) else None
                # Check the escape sequence and replace the character with the corresponding value
                if next_char in ['\\', '\"', '\'']:
                    char = next_char
                elif next_char == 'n':
                    char = '\n'
                else:
                    # Raise an exception if an invalid escape sequence is encountered
                    raise InvalidEscapeSequenceError(f"\\{next_char}")

            # Increment the position to move to the next character
            self.position += 1
            return char
        else:
            # Return None if the end of the source code has been reached
            return None

###########################################################################################################################################    

    def get_token(self):
        # Initialize an empty lexeme and longest_match string
        lexeme = ""
        longest_match = ""

        while True:
            # Get the next character from the source code
            char = self.get_next_char()

            # If there are no more characters, return the final token if there is one
            if char is None:
                if lexeme:
                    token_type = self.get_token_type_from_state(self.current_state, longest_match)
                    if token_type:
                        return Token(token_type, longest_match)
                    else:
                        raise InvalidTokenError(longest_match)
                return None

            # Check for quotes and handle quoted strings
            if char in ["\"", "\'"]:
                if self.open_quote == char and self.current_state in [19, 20, 21]:
                    lexeme += char
                    token_type = self.get_token_type_from_state(self.current_state, longest_match)
                    if token_type:
                        token = Token(token_type, longest_match)
                        self.current_state = 0
                        self.open_quote = None
                        longest_match = ""
                        return token
                    else:
                        raise InvalidTokenError(longest_match)
                elif self.open_quote is None:
                    self.open_quote = char
                    longest_match = lexeme

            # Get the next state based on the current state and the current character
            next_state = self.transition_table.get((self.current_state, char), -1)

            # If there is no next state, handle the final token if there is one
            if next_state == -1:
                if self.current_state == 0:
                    if longest_match:
                        token_type = self.get_token_type_from_state(self.current_state, longest_match)
                        if token_type:
                            token = Token(token_type, longest_match)
                            self.position -= 1
                            self.current_state = 0
                            self.open_quote = None
                            longest_match = ""
                            return token
                        else:
                            raise InvalidTokenError(longest_match)
                    else:
                        raise UnexpectedCharacterError(char)
                else:
                    token_type = self.get_token_type_from_state(self.current_state, longest_match)
                    if token_type:
                        token = Token(token_type, longest_match)
                        self.position -= 1
                        self.current_state = 0
                        self.open_quote = None
                        longest_match = ""
                        return token
                    else:
                        raise InvalidTokenError(longest_match)
            else:
                # Update the current state and lexeme with the new character
                self.current_state = next_state
                lexeme += char

                # Update the longest_match if there is a valid token type
                token_type = self.get_token_type_from_state(self.current_state, lexeme)
                if token_type:
                    longest_match = lexeme

###########################################################################################################################################

    # This method takes a state and a lexeme, and returns the corresponding token type based on the state and lexeme
    def get_token_type_from_state(self, state, lexeme):
        # Check the state and return the appropriate token type for the given lexeme
        if state == 1:
            # Check if the lexeme is a keyword
            return Lexer.KEYWORDS.get(lexeme, "IDENTIFIER")
        elif state == 2:
            return 'INTEGER_LITERAL'
        elif state == 3:
            # Distinguish between different operator types
            operator_map = {
                '+': 'PLUS',
                '-': 'MINUS',
                '*': 'MUL',
                '/': 'DIV',
                '%': 'MOD',
            }
            return operator_map.get(lexeme, 'OPERATOR')
        elif state == 4:
            # Distinguish between different delimiter types
            delimiter_map = {
                '(': 'LEFT_PAREN',
                ')': 'RIGHT_PAREN',
                '{': 'LEFT_BRACE',
                '}': 'RIGHT_BRACE',
                '[': 'LEFT_BRACKET',
                ']': 'RIGHT_BRACKET',
                ',': 'COMMA',
                '.': 'DOT',
                ';': 'SEMICOLON',
            }
            return delimiter_map.get(lexeme, 'DELIMITER')
        elif state == 5:
            return 'ASSIGNMENT_OPERATOR'
        elif state == 6:
            return 'EQUALITY_OPERATOR'
        elif state == 8:
            return 'RELATIONAL_OPERATOR'
        elif state == 9:
            return 'RELATIONAL_OPERATOR'
        elif state == 10:
            return 'RELATIONAL_OPERATOR'
        elif state == 11:
            return 'RELATIONAL_OPERATOR'
        elif state == 12:
            return 'RELATIONAL_OPERATOR'
        elif state == 13:
            return 'RELATIONAL_OPERATOR'
        elif state == 16:
            return 'LOGICAL_OPERATOR'
        elif state == 18:
            return 'LOGICAL_OPERATOR'
        elif state == 19:
            return 'STRING_LITERAL'
        elif state == 20:
            return 'STRING_LITERAL'
        elif state == 21:
            return 'STRING_LITERAL'
        elif state == 22:
            return 'SINGLE_LINE_COMMENT'
        elif state == 24:
            return 'MULTI_LINE_COMMENT'
        elif state == 27:
            return 'BLOCK_COMMENT'
        elif state == 31: 
            if lexeme.lower() == "true":
                return 'BOOLEAN_LITERAL_TRUE'
            else:
                return None
        elif state == 108:
            if lexeme.lower() == "false":
                return 'BOOLEAN_LITERAL_FALSE'
            else:
                return None
        elif state == 37:
            return 'WHITESPACE'
        elif state == 38:
            return 'ARRAY_INDEX'
        elif state == 39:
            if lexeme == '{':
                return 'LEFT_BRACE'
            elif lexeme == '}':
                return 'RIGHT_BRACE'
            else:
                return 'DICTIONARY'
        elif state == 41:
            return 'COLON'
        elif state == 42:
            return 'FUNCTION_DEF'
        elif state == 43:
            return 'FUNCTION_DEF'
        elif state == 44:
            return 'FUNCTION_DEF'
        elif state == 45:
            return 'OPEN_PAREN'
        elif state == 46:
            return 'CLOSE_PAREN'
        elif state == 60:
            return 'COLOR_LITERAL'
        elif state == 66:
            return 'READ_STATEMENT'
        elif state == 67:
            return 'DELAY_STATEMENT'
        elif state == 68:
            return 'PAD_HEIGHT'
        elif state == 69:
            return 'PAD_WIDTH'
        elif state == 70:
            return 'RANDI_STATEMENT'
        elif state == 71:
            return 'PRINT_STATEMENT'
        elif state == 72:
            return 'PIXEL_STATEMENT'
        elif state == 73:
            return 'FLOAT_LITERAL' if lexeme.endswith(';') else None
        elif state == 74:
            return 'PIXELR_STATEMENT'
        elif state == 85:
            return 'TYPE_BOOL'
        elif state == 91:
            return 'TYPE_COLOUR'
        elif state == 102:
            return 'FUNCTION_DEF'
        elif state == 103:
            return 'OPEN_PAREN'
        elif state == 104:
            return 'TYPE_FLOAT'
        elif state == 105:
            return 'CLOSE_PAREN'
        elif state == 106:
            return 'WHITESPACE'
        elif state == 110:
            return 'IF'
        elif state == 111:
            return 'TYPE_INT'
        elif state == 112:
            return 'FOR'
        elif state == 113:
            return 'TYPE_FLOAT'
        elif state == 114:
            return 'ELSE'
        elif state == 124:
            return 'FLOAT_LITERAL'
        elif state == 201:
            return 'FUNCTION_ARROW'
        else:
            return None

###########################################################################################################################################

    def tokenize(self):
        # Initialize an empty list to hold the tokens
        tokens = []

        while True:
            # Get the next token from the source code
            token = self.get_token()

            # If there are no more tokens or if the current token is the "END" token, stop processing
            if token is None or token.token_type == "END":
                break

            # Ignore whitespace, single-line comments, and block comments
            if token.token_type not in ["WHITESPACE", "SINGLE_LINE_COMMENT", "BLOCK_COMMENT"]:
                # Add the token to the list of tokens
                tokens.append(token)

        # Return the list of tokens
        return tokens

###########################################################################################################################################

    def lex_identifier_or_keyword(self):
        # Keep advancing the current position while the current character is alphanumeric
        while self.is_alphanumeric(self.peek()):
            self.advance()

        # Get the text of the identifier or keyword
        text = self.source[self.start:self.current]

        # If the text is a keyword, set the token type to the keyword, otherwise set it to "IDENTIFIER"
        token_type = Lexer.KEYWORDS.get(text, "IDENTIFIER")

        # Add the token to the list of tokens
        self.add_token(token_type, text)

###########################################################################################################################################

class LexerError(Exception):
    pass

class UnexpectedCharacterError(LexerError):
    def __init__(self, char):
        # Initialize the exception with the unexpected character
        self.char = char
        super().__init__(f"Unexpected character '{char}'")

class InvalidTokenError(LexerError):
    def __init__(self, token):
        # Initialize the exception with the invalid token
        self.token = token
        super().__init__(f"Invalid token '{token}'")

class InvalidEscapeSequenceError(LexerError):
    def __init__(self, sequence):
        # Initialize the exception with the invalid escape sequence
        self.sequence = sequence
        super().__init__(f"Invalid escape sequence '{sequence}'")

###########################################################################################################################################

# Usage:

# Specify the name of the file
#filename = 'input.txt'
#
## Open the file and read the contents into a string
#with open(filename, 'r') as file:
#    source_code = file.read()
#
## Tokenize the source code using the Lexer class
#try:
#    lexer = Lexer(source_code)
#    print("\n" + "-"*100)
#    print("\nLexer:\n")
#    tokens = lexer.tokenize()
#
#    # Print each token in the list of tokens
#    for token in tokens:
#        print(token)
#
## If there is a LexerError, print an error message
#except LexerError as e:
#    print(f"Error: {e}")
#
#print("\n" + "-"*100)