class Token:
    def __init__(self, token_type, lexeme):
        self.token_type = token_type
        self.lexeme = lexeme
    def __str__(self):
        return f"{self.token_type}({self.lexeme})"
class Lexer:       
    KEYWORDS = {"if": "IF", "else": "ELSE", "while": "WHILE", "for": "FOR", "return": "RETURN", "fun": "FUNCTION_DEF", "true": "BOOLEAN_TRUE", "false": "BOOLEAN_FALSE", "not": "LOGICAL_OP", "let": "LET","__read": "READ", "__print": "PRINT", "__delay": "DELAY","__randi": "RANDI", "__width": "WIDTH", "__height": "HEIGHT","__pixelr": "PIXELR", "__pixel": "PIXEL", "->": "FUNC_ARROW","int": "TYPE_INT", "bool": "TYPE_BOOL", "float": "TYPE_FLOAT","colour": "TYPE_COLOUR"}
    def __init__(self, source_code):
        self.source_code = source_code
        self.transition_table = self.build_transition_table()
        self.current_state = 0
        self.position = 0
        self.open_quote = None
    def build_transition_table(self):
        transition_table = {}
        states = range(32)
        input_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*/%=<>!#()[]{},.;:'\" \t\n"
        for state in states:
            for char in input_characters:
                transition_table[(state, char)] = -1
        for char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            transition_table[(0, char)] = 1
        for char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
            transition_table[(1, char)] = 1
        transition_table[(0, '_')] = 1
        transition_table[(1, '_')] = 1
        for char in "0123456789":
            transition_table[(0, char)] = 2
            transition_table[(2, char)] = 2
        operators = "+-*%"
        for op in operators:
            transition_table[(0, op)] = 3
        transition_table[(0, '/')] = 3
        transition_table[(3, '/')] = 22  
        transition_table[(3, '*')] = 24  
        transition_table[(3, '=')] = 23  
        transition_table[(22, '\n')] = 37  
        for char in input_characters:
            if char != '\n':
                transition_table[(22, char)] = 22
        transition_table[(24, '*')] = 25
        transition_table[(25, '/')] = 37  
        for char in input_characters:
            if char != '*' and char != '/':
                transition_table[(24, char)] = 24
                transition_table[(25, char)] = 24
        delimiters = "(){},.;[]"
        for delimiter in delimiters:
            transition_table[(0, delimiter)] = 4
        transition_table[(0, '<')] = 9
        transition_table[(9, '=')] = 10
        transition_table[(0, '>')] = 11
        transition_table[(11, '=')] = 12
        transition_table[(0, '=')] = 5
        transition_table[(5, '=')] = 6
        transition_table[(0, '!')] = 7
        transition_table[(7, '=')] = 8
        transition_table[(0, 'a')] = 15
        transition_table[(15, 'n')] = 16
        transition_table[(16, 'd')] = 18
        transition_table[(0, 'o')] = 17
        transition_table[(17, 'r')] = 18
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
        transition_table[(0, "'")] = 21
        for char in input_characters:
            if char == "'":
                transition_table[(21, char)] = 19
            else:
                transition_table[(21, char)] = 21
                transition_table[(19, char)] = 19
        transition_table[(0, 't')] = 28
        transition_table[(28, 'r')] = 29
        transition_table[(29, 'u')] = 30
        transition_table[(30, 'e')] = 31
        transition_table[(0, 'f')] = 25
        transition_table[(25, 'a')] = 26
        transition_table[(26, 'l')] = 27
        transition_table[(27, 's')] = 28
        transition_table[(28, 'e')] = 29
        transition_table[(0, '=')] = 5
        transition_table[(5, '=')] = 6
        transition_table[(0, '[')] = 38
        transition_table[(0, '{')] = 39
        transition_table[(38, ']')] = 40
        transition_table[(39, '}')] = 41
        transition_table[(0, '(')] = 45
        transition_table[(0, ')')] = 46
        transition_table[(0, ':')] = 41         
        for char in " \t\n":
            transition_table[(0, char)] = 37
            transition_table[(37, char)] = 37
        transition_table[(0, '_')] = 61  
        transition_table[(61, '_')] = 62
        transition_table[(62, 'r')] = 63
        transition_table[(63, 'e')] = 64
        transition_table[(64, 'a')] = 65
        transition_table[(65, 'd')] = 66
        transition_table[(63, 'a')] = 67
        transition_table[(67, 'n')] = 68
        transition_table[(68, 'd')] = 69
        transition_table[(69, 'i')] = 70
        transition_table[(0, '_')] = 61  
        transition_table[(61, '_')] = 62
        transition_table[(62, 'p')] = 67 
        transition_table[(67, 'r')] = 68
        transition_table[(68, 'i')] = 69
        transition_table[(69, 'n')] = 70
        transition_table[(70, 't')] = 71
        transition_table[(0, '_')] = 61
        transition_table[(61, '_')] = 62
        transition_table[(62, 'p')] = 67
        transition_table[(67, 'i')] = 68
        transition_table[(68, 'x')] = 69
        transition_table[(69, 'e')] = 70
        transition_table[(70, 'l')] = 72
        transition_table[(72, 'r')] = 74
        transition_table[(0, '_')] = 61  
        transition_table[(61, '_')] = 62
        transition_table[(62, 'd')] = 63
        transition_table[(63, 'e')] = 64
        transition_table[(64, 'l')] = 65
        transition_table[(65, 'a')] = 66
        transition_table[(66, 'y')] = 67
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
        transition_table[(0, '#')] = 54
        for char in "0123456789abcdefABCDEF":
            transition_table[(54, char)] = 55
            transition_table[(55, char)] = 56
            transition_table[(56, char)] = 57
            transition_table[(57, char)] = 58
            transition_table[(58, char)] = 59
            transition_table[(59, char)] = 60
        transition_table[(0, 'b')] = 82
        transition_table[(82, 'o')] = 83
        transition_table[(83, 'o')] = 84
        transition_table[(84, 'l')] = 85
        transition_table[(0, 'c')] = 86
        transition_table[(86, 'o')] = 87
        transition_table[(87, 'l')] = 88
        transition_table[(88, 'o')] = 89
        transition_table[(89, 'u')] = 90
        transition_table[(90, 'r')] = 91
        transition_table[(0, 'i')] = 109
        transition_table[(109, 'f')] = 110
        transition_table[(0, 'e')] = 111
        transition_table[(111, 'l')] = 112
        transition_table[(112, 's')] = 113
        transition_table[(113, 'e')] = 114
        transition_table[(0, 'i')] = 109
        transition_table[(109, 'n')] = 110
        transition_table[(110, 't')] = 111
        transition_table[(0, 'f')] = 100
        transition_table[(100, 'l')] = 101
        transition_table[(101, 'o')] = 102
        transition_table[(102, 'a')] = 103
        transition_table[(103, 't')] = 104 
        transition_table[(100, 'a')] = 105
        transition_table[(105, 'l')] = 106
        transition_table[(106, 's')] = 107
        transition_table[(107, 'e')] = 108
        transition_table[(100, 'o')] = 111
        transition_table[(111, 'r')] = 112
        transition_table[(100, 'u')] = 101
        transition_table[(101, 'n')] = 102
        transition_table[(102, '(')] = 103
        transition_table[(106, '')] = 104
        transition_table[(104, ')')] = 105
        transition_table[(105, '')] = 106
        transition_table[(1, '-')] = 200
        transition_table[(200, '>')] = 201
        return transition_table
    def get_next_char(self):
        if self.position < len(self.source_code):
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
            self.position += 1
            return char
        else:
            return None    
    def get_token(self):
        lexeme = ""
        longest_match = ""
        while True:
            char = self.get_next_char()
            if char is None:
                if lexeme:
                    token_type = self.get_token_type_from_state(self.current_state, longest_match)
                    if token_type:
                        return Token(token_type, longest_match)
                    else:
                        raise InvalidTokenError(longest_match)
                return None
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
            next_state = self.transition_table.get((self.current_state, char), -1)
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
                self.current_state = next_state
                lexeme += char
                token_type = self.get_token_type_from_state(self.current_state, lexeme)
                if token_type:
                    longest_match = lexeme
    def get_token_type_from_state(self, state, lexeme):
        state_to_token_type = {1: Lexer.KEYWORDS.get(lexeme, "IDENTIFIER"),
            2: 'INTEGER_LITERAL',
            3: {
                '+': 'PLUS',
                '-': 'MINUS',
                '*': 'MUL',
                '/': 'DIV',
                '%': 'MOD',
            }.get(lexeme, 'OPERATOR'),
            4: {
                '(': 'LEFT_PAREN',
                ')': 'RIGHT_PAREN',
                '{': 'LEFT_BRACE',
                '}': 'RIGHT_BRACE',
                '[': 'LEFT_BRACKET',
                ']': 'RIGHT_BRACKET',
                ',': 'COMMA',
                '.': 'DOT',
                ';': 'SEMICOLON',
            }.get(lexeme, 'DELIMITER'),
            5: 'ASSIGNMENT_OPERATOR',
            6: 'EQUALITY_OPERATOR',
            8: 'RELATIONAL_OPERATOR',
            9: 'RELATIONAL_OPERATOR',
            10: 'RELATIONAL_OPERATOR',
            11: 'RELATIONAL_OPERATOR',
            12: 'RELATIONAL_OPERATOR',
            13: 'RELATIONAL_OPERATOR',
            16: 'LOGICAL_OPERATOR',
            18: 'LOGICAL_OPERATOR',
            19: 'STRING_LITERAL',
            20: 'STRING_LITERAL',
            21: 'STRING_LITERAL',
            22: 'SINGLE_LINE_COMMENT',
            24: 'MULTI_LINE_COMMENT',
            27: 'BLOCK_COMMENT',
            31: 'BOOLEAN_LITERAL_TRUE' if lexeme.lower() == 'true' else None,
            108: 'BOOLEAN_LITERAL_FALSE' if lexeme.lower() == 'false' else None,
            37: 'WHITESPACE',
            38: 'ARRAY_INDEX',
            39: 'LEFT_BRACE' if lexeme == '{' else 'RIGHT_BRACE' if lexeme == '}' else 'DICTIONARY',
            41: 'COLON',
            42: 'FUNCTION_DEF',
            43: 'FUNCTION_DEF',
            44: 'FUNCTION_DEF',
            45: 'OPEN_PAREN',
            46: 'CLOSE_PAREN',
            60: 'COLOR_LITERAL',
            66: 'READ_STATEMENT',
            67: 'DELAY_STATEMENT',
            68: 'PAD_HEIGHT',
            69: 'PAD_WIDTH',
            70: 'RANDI_STATEMENT',
            71: 'PRINT_STATEMENT',
            72: 'PIXEL_STATEMENT',
            73: 'FLOAT_LITERAL' if lexeme.endswith(';') else None,
            74: 'PIXELR_STATEMENT',
            85: 'TYPE_BOOL',
            91: 'TYPE_COLOUR',
            102: 'FUNCTION_DEF',
            103: 'OPEN_PAREN',
            104: 'TYPE_FLOAT',
            105: 'CLOSE_PAREN',
            106: 'WHITESPACE',
            110: 'IF',
            111: 'TYPE_INT',
            112: 'FOR',
            113: 'TYPE_FLOAT',
            114: 'ELSE',
            124: 'FLOAT_LITERAL',
            201: 'FUNCTION_ARROW',}
        return state_to_token_type.get(state, None)
    def tokenize(self):
        tokens = []
        while True:
            token = self.get_token()
            if token is None or token.token_type == "END":
                break
            if token.token_type not in ["WHITESPACE", "SINGLE_LINE_COMMENT", "BLOCK_COMMENT"]:
                tokens.append(token)
        return tokens
    def lex_identifier_or_keyword(self):
        while self.is_alphanumeric(self.peek()):
            self.advance()
        text = self.source[self.start:self.current]
        token_type = Lexer.KEYWORDS.get(text, "IDENTIFIER")
        self.add_token(token_type, text)
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