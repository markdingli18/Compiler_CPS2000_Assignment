# Digits

DIGITS = '0123456789'

# Error

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.file_name}, line {self.pos_start.line + 1}\n'
        result += '\n'.join(self.string_with_arrows().split('\n')[1:])
        return result
    
    def string_with_arrows(self):
        result = ''
        line = self.pos_start.line_text()
        result += line + '\n'
        result += ' ' * (self.pos_start.column) + '^'
        return result
        
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end,'Illegal Character', details)

    def as_string(self):
        return super().as_string()
    
class Position:
    def __init__(self, index, line, column, file_name, file_text):
        self.index = index
        self.line = line
        self.column = column
        self.file_name = file_name
        self.file_text = file_text
    
    def advance(self, current_char):
        self.index += 1
        self.column += 1
        
        if current_char == '\n':
            self.line += 1
            self.column = 0
            
        return self
    
    def copy(self):
        return Position(self.index, self.line, self.column, self.file_name, self.file_text)
    
    def line_text(self):
        eol = self.file_text.find('\n', self.index)
        if eol == -1:
            eol = len(self.file_text)
        line_start = self.file_text.rfind('\n', 0, self.index) + 1
        return self.file_text[line_start:eol]

# TOKENS
TOKEN_TYPE_INT = 'INT'
TOKEN_TYPE_FLOAT = 'FLOAT'
TOKEN_TYPE_PLUS = 'PLUS'
TOKEN_TYPE_MINUS = 'MINUS'
TOKEN_TYPE_MUL = 'MUL'
TOKEN_TYPE_DIV = 'DIV'
TOKEN_TYPE_LEFTPAR = 'LEFTPAR'
TOKEN_TYPE_RIGHTPAR = 'RIGHTPAR'

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
        
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    
# LEXER
class Lexer:
    def __init__(self, file_name, text):
        self.text = text
        self.file_name = file_name
        self.pos = Position(-1, 0, -1, file_name, text)
        self.current_char = None
        self.advance()
        
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None
        
    def make_tokens(self):
        tokens = []
        
        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TOKEN_TYPE_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TOKEN_TYPE_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TOKEN_TYPE_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TOKEN_TYPE_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TOKEN_TYPE_LEFTPAR))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TOKEN_TYPE_RIGHTPAR))
                self.advance()
            else:
                # return error if character is not found
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos,"'" + char + "'")
                
        return tokens, None
    
    def make_number(self):
        num_str = ''
        dot_count = 0
        
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char =='.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
                
        if dot_count ==0:
            return Token(TOKEN_TYPE_INT, int(num_str))
        else:
            return Token(TOKEN_TYPE_FLOAT, float(num_str))
        
# RUN

def run(file_name, text):
    lexer= Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    
    return tokens, error