from lexer import *
from parser_ import *

class ASTXMLGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.indent_level = 0
        
###########################################################################################################################################

    def visit(self, node):
        method_name = f"visit_{node[0]}"
        visit_method = getattr(self, method_name, self.generic_visit)
        return visit_method(node)
    
    def generic_visit(self, node):
        raise NotImplementedError(f"Visit method for node type {node[0]} not implemented.")
    
###########################################################################################################################################
    
    # Visit methods for all AST node types
    
    def visit_PROGRAM(self, node):
        print('<Program>')
        self.indent_level += 1
        for child in node[1:]:
            self.visit(child)
        self.indent_level -= 1
        print('</Program>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_DECLARATION(self, node):
        self.indent()
        print(f'<Decl type="{node[1]}" identifier="{node[2]}">')
        self.indent_level += 1

        if len(node) > 3:
            self.visit(node[3])

        self.indent_level -= 1
        self.indent()
        print('</Decl>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_INTEGER_LITERAL(self, node):
        self.indent()
        print(f'<IntegerLiteral value="{node[1]}" />')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_BINARY_EXPRESSION(self, node):
        self.indent()
        print(f'<BinaryExpression operator="{node[1]}">')
        self.indent_level += 1

        self.visit(node[2])  # Visit left operand
        self.visit(node[3])  # Visit right operand

        self.indent_level -= 1
        self.indent()
        print('</BinaryExpression>')
        
    def visit_PLUS(self, node):
        self.indent()
        print(f'<BinaryExpression operator="+">')
        self.indent_level += 1

        self.visit(node[1])  # Visit left operand
        self.visit(node[2])  # Visit right operand

        self.indent_level -= 1
        self.indent()
        print('</BinaryExpression>')
        
    def visit_MUL(self, node):
        self.indent()
        print(f'<BinaryExpression operator="*">')
        self.indent_level += 1

        self.visit(node[1])  # Visit left operand
        self.visit(node[2])  # Visit right operand

        self.indent_level -= 1
        self.indent()
        print('</BinaryExpression>')
        
    def visit_MINUS(self, node):
        self.indent()
        print('<MinusExpression>')

        self.indent_level += 1
        self.visit(node[1])
        self.visit(node[2])
        self.indent_level -= 1

        self.indent()
        print('</MinusExpression>')
        
    def visit_DIV(self, node):
        self.indent()
        print('<DivExpression>')
        self.indent_level += 1

        for child_node in node[1:]:
            self.visit(child_node)

        self.indent_level -= 1
        self.indent()
        print('</DivExpression>')
        
    def visit_LOGICAL_OPERATOR(self, node):
        operator = "and" if node[1] == "and" else "or"
        self.indent()
        print(f'<LogicalExpression operator="{operator}">')
        self.indent_level += 1

        self.visit(node[2])  # Visit left operand
        
        if len(node) > 3:
            self.visit(node[3])  # Visit right operand

        self.indent_level -= 1
        self.indent()
        print('</LogicalExpression>')

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_NUMBER(self, node):
        self.indent()
        print(f'<Number value="{node[1]}" />')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_TYPE(self, node):
        self.indent()
        print(f'<Type>{node[1]}</Type>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_IDENTIFIER(self, node):
        self.indent()
        print(f'<Identifier name="{node[1]}" />')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_FLOAT_LITERAL(self, node):
        self.indent()
        print(f'<FloatLiteral value="{node[1]}" />')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_STRING_LITERAL(self, node):
        self.indent()
        print(f'<StringLiteral value="{node[1]}" />')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_COLOR_LITERAL(self, node):
        self.indent()
        print(f'<ColorLiteral value="{node[1]}" />')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_UNARY_EXPRESSION(self, node):
        self.indent()
        print(f'<UnaryExpression operator="{node[1]}">')
        self.indent_level += 1

        self.visit(node[2])  # Visit the operand

        self.indent_level -= 1
        self.indent()
        print('</UnaryExpression>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_IF_STATEMENT(self, node):
        self.indent()
        print('<IfStatement>')
        self.indent_level += 1

        self.visit(node[1])  # Visit the condition
        self.visit(node[2])  # Visit the true branch

        if len(node) > 3:  # If an else branch is present
            self.visit(node[3])

        self.indent_level -= 1
        self.indent()
        print('</IfStatement>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_WHILE_LOOP(self, node):
        self.indent()
        print('<WhileLoop>')
        self.indent_level += 1

        self.visit(node[1])  # Visit the condition
        self.visit(node[2])  # Visit the loop body

        self.indent_level -= 1
        self.indent()
        print('</WhileLoop>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_FUNCTION_DEFINITION(self, node):
        self.indent()
        print(f'<FunctionDefinition name="{node[1]}">')
        self.indent_level += 1

        self.visit(node[2])  # Visit the argument list
        self.visit(node[3])  # Visit the function body

        self.indent_level -= 1
        self.indent()
        print('</FunctionDefinition>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_FUNCTION_CALL(self, node):
        self.indent()
        print(f'<FunctionCall name="{node[1]}">')
        self.indent_level += 1

        for arg in node[2]:
            self.visit(arg)

        self.indent_level -= 1
        self.indent()
        print('</FunctionCall>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_ARGUMENT_LIST(self, node):
        self.indent()
        print('<ArgumentList>')
        self.indent_level += 1

        for arg in node[1:]:
            self.visit(arg)

        self.indent_level -= 1
        self.indent()
        print('</ArgumentList>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_STATEMENT_BLOCK(self, node):
        self.indent()
        print('<StatementBlock>')
        self.indent_level += 1

        for stmt in node[1:]:
            self.visit(stmt)

        self.indent_level -= 1
        self.indent()
        print('</StatementBlock>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_RETURN_STATEMENT(self, node):
        self.indent()
        print('<ReturnStatement>')
        self.indent_level += 1

        self.visit(node[1])  # Visit the returned expression

        self.indent_level -= 1
        self.indent()
        print('</ReturnStatement>')
    
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_PRINT(self, node):
        self.indent()
        print('<PrintStatement>')
        self.indent_level += 1

        self.visit(node[1])  # Visit the expression to be printed

        self.indent_level -= 1
        self.indent()
        print('</PrintStatement>')

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_DELAY(self, node):
        self.indent()
        print(f'<DelayStatement time="{node[1][1]}" />')

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_PIXEL_STATEMENT(self, node):
        self.indent()
        print(f'<PixelStatement>')
        self.indent_level += 1

        for arg in node[2]:
            self.visit(arg)

        self.indent_level -= 1
        self.indent()
        print('</PixelStatement>')

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_WIDTH(self, node):
        self.indent()
        print(f'<Width width="{node[1][1]}" />')

    def visit_HEIGHT(self, node):
        self.indent()
        print(f'<Height height="{node[1][1]}" />')

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_READ(self, node):
        self.indent()
        print('<ReadStatement>')
        self.indent_level += 1

        for arg in node[1:]:
            self.visit(arg)

        self.indent_level -= 1
        self.indent()
        print('</ReadStatement>')

    #---------------------------------------------------------------------------------------------------------------------------------------
    

    
    #---------------------------------------------------------------------------------------------------------------------------------------
    
###########################################################################################################################################

    def indent(self):
        print(' ' * 2 * self.indent_level, end='')
        
###########################################################################################################################################
        
# Usage:
source_code = """
let x: int = 1 and 2;
let y: int = 2 or 1;
"""

try:
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    print("\nXML Representation:\n")    
    xml_generator = ASTXMLGenerator(ast)
    for node in ast:
        xml_generator.visit(node)
    print("\n" + "-"*100)

except LexerError as e:
    print(f"Error: {e}")
except ParserError as e:
    print(f"Error: {e}")