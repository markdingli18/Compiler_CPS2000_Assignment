from lexer import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        
###########################################################################################################################################

    def parse(self):
        program = []
        while self.current_index < len(self.tokens):
            program.append(self.parse_statement())
        return program
    
###########################################################################################################################################

    def parse_statement(self):
        if self.match("IDENTIFIER") and self.match("ASSIGNMENT_OPERATOR"):
            identifier = self.previous().lexeme
            value = self.parse_expression()
            self.expect("SEMICOLON")
            return ("ASSIGNMENT", identifier, value)
        elif self.match("IF"):
            return self.parse_if()
        else:
            raise ParserError(f"Invalid statement at token {self.tokens[self.current_index]}")
        
###########################################################################################################################################

    def parse_if(self):
        self.expect("IF")
        condition = self.parse_expression()
        self.expect("COLON")

        statements = []
        while not self.match("ELIF") and not self.match("ELSE"):
            statements.append(self.parse_statement())

        if self.match("ELIF"):
            else_branch = self.parse_if()
        elif self.match("ELSE"):
            self.expect("COLON")
            else_statements = []
            while self.current_index < len(self.tokens):
                else_statements.append(self.parse_statement())
            else_branch = ("ELSE", else_statements)
        else:
            else_branch = None

        return ("IF", condition, statements, else_branch)
    
###########################################################################################################################################

    def parse_expression(self):
        left = self.parse_term()

        while self.match("PLUS") or self.match("MINUS") or self.match("MUL") or self.match("DIV") or self.match("MOD"):
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

    def parse_factor(self):
        if self.match("IDENTIFIER"):
            return ("IDENTIFIER", self.previous().lexeme)
        elif self.match("INTEGER_LITERAL"):
            return ("INTEGER_LITERAL", int(self.previous().lexeme))
        elif self.match("OPEN_PAREN"):
            expr = self.parse_expression()
            self.expect("CLOSE_PAREN")
            return expr
        else:
            raise ParserError(f"Invalid factor at token {self.tokens[self.current_index]}")
        
###########################################################################################################################################

    def match(self, token_type):
        if self.current_index < len(self.tokens) and self.tokens[self.current_index].token_type == token_type:
            self.current_index += 1
            return True
        return False
    
###########################################################################################################################################

    def expect(self, token_type):
        if not self.match(token_type):
            raise ParserError(f"Expected '{token_type}', found '{self.tokens[self.current_index].token_type}'")
        
###########################################################################################################################################

    def previous(self):
        return self.tokens[self.current_index - 1]
    
###########################################################################################################################################

class ParserError(Exception):
    pass

###########################################################################################################################################

# Usage:
source_code = """
x = 10;
y = 5;
"""

try:
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    print("\nLexer:\n")
    for token in tokens:
        print(token)

    parser = Parser(tokens)
    parsed_program = parser.parse()
    print("\n" + "-"*100)
    print("\nParsed program:\n")
    print(parsed_program)

except LexerError as e:
    print(f"Error: {e}")
except ParserError as e:
    print(f"Error: {e}")

print("\n" + "-"*100)