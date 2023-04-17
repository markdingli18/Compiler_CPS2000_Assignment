class Token:
    def __init__(self, token_type, lexeme):
        self.token_type = token_type
        self.lexeme = lexeme

    def __str__(self):
        return f"{self.token_type}({self.lexeme})"

###########################################################################################################################################

class Lexer:
            
    KEYWORDS = {
        "if": "IF",
        "else": "ELSE",
        "elif": "ELIF",
        "while": "WHILE",
        "for": "FOR",
        "return": "RETURN",
        "def": "FUNCTION_DEF",
        "true": "BOOLEAN_LITERAL",
        "false": "BOOLEAN_LITERAL",
        "not": "LOGICAL_OPERATOR", 
        "__read": "READ_STATEMENT",
        "__print": "PRINT_STATEMENT", 
    }
    
    def __init__(self, source_code):
        self.source_code = source_code
        self.transition_table = self.build_transition_table()
        self.current_state = 0
        self.position = 0
        self.open_quote = None

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

        # Transitions for 'false' boolean literal
        transition_table[(0, 'f')] = 32
        transition_table[(32, 'a')] = 33
        transition_table[(33, 'l')] = 34
        transition_table[(34, 's')] = 35
        transition_table[(35, 'e')] = 36
        
        # Transitions for assignment and equality operators
        transition_table[(0, '=')] = 5
        transition_table[(5, '=')] = 6
        
        # Transitions for arrays and dictionaries
        transition_table[(0, '[')] = 38
        transition_table[(0, '{')] = 39
        transition_table[(38, ']')] = 40
        transition_table[(39, '}')] = 41
        
        # Transitions for function definitions
        transition_table[(0, 'd')] = 42
        transition_table[(42, 'e')] = 43
        transition_table[(43, 'f')] = 44

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
        
        # Transitions for __print statement
        transition_table[(0, '_')] = 61  
        transition_table[(61, '_')] = 62
        transition_table[(62, 'p')] = 67  # Updated transition
        transition_table[(67, 'r')] = 68
        transition_table[(68, 'i')] = 69
        transition_table[(69, 'n')] = 70
        transition_table[(70, 't')] = 71
        
        # Transitions for float literals
        for char in "0123456789":
            transition_table[(0, char)] = 2
            transition_table[(2, char)] = 2
            
        # Transitions for colour literals
        transition_table[(0, '#')] = 54
        for char in "0123456789abcdefABCDEF":
            transition_table[(54, char)] = 55
            transition_table[(55, char)] = 56
            transition_table[(56, char)] = 57
            transition_table[(57, char)] = 58
            transition_table[(58, char)] = 59
            transition_table[(59, char)] = 60

        transition_table[(2, '.')] = 23
        for char in "0123456789":
            transition_table[(23, char)] = 24
            transition_table[(24, char)] = 24

        return transition_table

###########################################################################################################################################

    def get_next_char(self):
        if self.position < len(self.source_code):
            # Get the character at the current position in the source code
            char = self.source_code[self.position]

            if self.open_quote and char == "\\":
                self.position += 1
                next_char = self.source_code[self.position] if self.position < len(self.source_code) else None
                if next_char in ['\\', '\"', '\'']:
                    char = next_char
                elif next_char == 'n':
                    char = '\n'
                else:
                    raise InvalidEscapeSequenceError(f"\\{next_char}")

            # Increment the position to move to the next character
            self.position += 1
            return char
        else:
            # Return None if the end of the source code has been reached
            return None

###########################################################################################################################################    

    def get_token(self):
        lexeme = ""

        while True:
            char = self.get_next_char()

            if char is None:
                if lexeme:
                    token_type = self.get_token_type_from_state(self.current_state, lexeme)
                    if token_type:
                        return Token(token_type, lexeme)
                    else:
                        raise InvalidTokenError(lexeme)
                return None

            if char in ["\"", "\'"] and self.open_quote == char and self.current_state in [19, 20, 21]:
                lexeme += char
                token_type = self.get_token_type_from_state(self.current_state, lexeme)
                if token_type:
                    token = Token(token_type, lexeme)
                    self.current_state = 0
                    self.open_quote = None
                    return token
                else:
                    raise InvalidTokenError(lexeme)
            else:
                next_state = self.transition_table.get((self.current_state, char), -1)

                if self.open_quote is None and (char == '"' or char == "'"):
                    self.open_quote = char

                if next_state == -1:
                    if self.current_state == 0:
                        raise UnexpectedCharacterError(char)
                    else:
                        token_type = self.get_token_type_from_state(self.current_state, lexeme)
                        if token_type:
                            token = Token(token_type, lexeme)
                            self.position -= 1
                            self.current_state = 0
                            self.open_quote = None
                            return token
                        else:
                            raise InvalidTokenError(lexeme)
                else:
                    self.current_state = next_state
                    lexeme += char

###########################################################################################################################################

    def get_token_type_from_state(self, state, lexeme):
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
        elif state == 24:
            return 'FLOAT_LITERAL'
        elif state == 27:
            return 'BLOCK_COMMENT'
        elif state == 28:
            return 'BOOLEAN_LITERAL'
        elif state == 31:
            return 'BOOLEAN_LITERAL'
        elif state == 36:
            return 'BOOLEAN_LITERAL'
        elif state == 37:
            return 'WHITESPACE'
        elif state == 38:
            return 'ARRAY_INDEX'
        elif state == 39:
            if lexeme == '{':
                return 'DICTIONARY_START'
            elif lexeme == '}':
                return 'DICTIONARY_END'
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
        elif state == 53:
            return 'PRINT_STATEMENT'
        elif state == 60:
            return 'COLOR_LITERAL'
        elif state == 66:
            return 'READ_STATEMENT'
        elif state == 71:
            return 'PRINT_STATEMENT'
        else:
            return None

###########################################################################################################################################

    def tokenize(self):
        tokens = []
        while True:
            token = self.get_token()
            if token is None or token.token_type == "END":
                break
            if token.token_type not in ["WHITESPACE", "SINGLE_LINE_COMMENT", "BLOCK_COMMENT"]:
                tokens.append(token)
        return tokens

###########################################################################################################################################

    def lex_identifier_or_keyword(self):
        while self.is_alphanumeric(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]
        token_type = Lexer.KEYWORDS.get(text, "IDENTIFIER")
        self.add_token(token_type, text)


###########################################################################################################################################

class LexerError(Exception):
    pass

class UnexpectedCharacterError(LexerError):
    def __init__(self, char):
        self.char = char
        super().__init__(f"Unexpected character '{char}'")

class InvalidTokenError(LexerError):
    def __init__(self, token):
        self.token = token
        super().__init__(f"Invalid token '{token}'")

class InvalidEscapeSequenceError(LexerError):
    def __init__(self, sequence):
        self.sequence = sequence
        super().__init__(f"Invalid escape sequence '{sequence}'")

###########################################################################################################################################

# Usage:
source_code = """
__print("jejejej");
"""

#try:
#    lexer = Lexer(source_code)
#    tokens = lexer.tokenize()
#    for token in tokens:
#        print(token)
#except LexerError as e:
#    print(f"Error: {e}")