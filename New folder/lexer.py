class Token:
    def __init__(self, token_type, lexeme):
        self.token_type = token_type
        self.lexeme = lexeme

    def __str__(self):
        return f"{self.token_type}({self.lexeme})"
    
###########################################################################################################################################

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.transition_table = self.build_transition_table()
        self.current_state = 0
        self.position = 0

    def build_transition_table(self):
        transition_table = {}
    
        states = range(14)  # Update the number of states to match your DFA
        input_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*/%=<>!#&|()[]{},.;:'\" \t\n"
        
        for state in states:
            for char in input_characters:
                transition_table[(state, char)] = -1

        # Transitions for identifiers
        for char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            transition_table[(0, char)] = 1
        for char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
            transition_table[(1, char)] = 1

        # Transitions for integer literals
        for char in "0123456789":
            transition_table[(0, char)] = 2
            transition_table[(2, char)] = 2

        # Transitions for operators
        operators = "+-*/%"
        for op in operators:
            transition_table[(0, op)] = 3

        # Transitions for delimiters
        delimiters = "(){},.;"
        for delimiter in delimiters:
            transition_table[(0, delimiter)] = 4

        # Transitions for relational operators
        transition_table[(0, '=')] = 5
        transition_table[(5, '=')] = 6

        transition_table[(0, '!')] = 7
        transition_table[(7, '=')] = 8

        transition_table[(0, '<')] = 9
        transition_table[(9, '=')] = 10

        transition_table[(0, '>')] = 11
        transition_table[(11, '=')] = 12

        # Transitions for whitespace
        for char in " \t\n":
            transition_table[(0, char)] = 13
            transition_table[(13, char)] = 13

        return transition_table

###########################################################################################################################################

    def get_next_char(self):
        if self.position < len(self.source_code):
            # Get the character at the current position in the source code
            char = self.source_code[self.position]
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
                    return Token("END", lexeme)
                return None

            next_state = self.transition_table.get((self.current_state, char), -1)

            if next_state == -1:
                if self.current_state == 0:
                    raise Exception(f"Lexical error: Unexpected character '{char}'")
                else:
                    token_type = self.get_token_type_from_state(self.current_state)
                    if token_type:
                        token = Token(token_type, lexeme)
                        self.position -= 1
                        self.current_state = 0
                        return token
                    else:
                        raise Exception(f"Lexical error: Invalid token '{lexeme}'")
            else:
                self.current_state = next_state
                lexeme += char
    
###########################################################################################################################################

    def get_token_type_from_state(self, state):
        # This function returns the token type for a given accepting state
        # Update the conditions with the appropriate ones for your language

        if state == 1:
            return "IDENTIFIER"
        elif state == 2:
            return "INTEGER_LITERAL"
        elif state == 3:
            return "OPERATOR"
        elif state == 4:
            return "DELIMITER"
        elif state == 6:
            return "EQUAL"
        elif state == 8:
            return "NOT_EQUAL"
        elif state == 9:
            return "LESS_THAN"
        elif state == 10:
            return "LESS_EQUAL"
        elif state == 11:
            return "GREATER_THAN"
        elif state == 12:
            return "GREATER_EQUAL"
        elif state == 13:
            return "WHITESPACE"
        else:
            return None

    def tokenize(self):
        tokens = []
        while True:
            token = self.get_token()
            if token is None or token.token_type == "END":
                break
            if token.token_type != "WHITESPACE":  # Exclude whitespace tokens
                tokens.append(token)
        return tokens
    
###########################################################################################################################################

# Usage:
source_code = "10+17;"
lexer = Lexer(source_code)
tokens = lexer.tokenize()

# Print tokens in a readable format
for token in tokens:
    print(token)