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
        
    def visit_BOOLEAN_LITERAL(self, node):
        self.indent()
        print(f'<BooleanLiteral value="{node[1]}" />')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_BINARY_EXPRESSION(self, node):
        self.indent()
        print(f'<BinaryExpression operator="{node[1]}">')
        self.indent_level += 1

        self.visit(node[2])  
        self.visit(node[3])  

        self.indent_level -= 1
        self.indent()
        print('</BinaryExpression>')
        
    def visit_PLUS(self, node):
        self.indent()
        print(f'<BinaryExpression operator="+">')
        self.indent_level += 1

        self.visit(node[1])  
        self.visit(node[2])  

        self.indent_level -= 1
        self.indent()
        print('</BinaryExpression>')
        
    def visit_MUL(self, node):
        self.indent()
        print(f'<BinaryExpression operator="*">')
        self.indent_level += 1

        self.visit(node[1])  
        self.visit(node[2])  

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

        self.visit(node[2]) 
        
        if len(node) > 3:
            self.visit(node[3]) 

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

        self.visit(node[2])

        self.indent_level -= 1
        self.indent()
        print('</UnaryExpression>')  
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_IF(self, node):
        self.indent()
        print('<IfStatement>')
        self.indent_level += 1

        # Visit the conditional expression
        self.visit(node[1])

        # Visit the block statement
        self.visit(node[2])

        self.indent_level -= 1
        self.indent()
        print('</IfStatement>')

        # Check if there's an else block
        if len(node) > 3:
            self.visit(node[3])

    def visit_ELSE(self, node):
        # Only visit the ElseStatement if there is an else block
        if len(node) > 0:
            self.indent()
            print('<ElseStatement>')
            self.indent_level += 1

            # Visit the block statement
            self.visit(node[1])

            self.indent_level -= 1
            self.indent()
            print('</ElseStatement>')
    
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_RELATIONAL_OPERATOR(self, node):
        self.indent()
        operator = node[0]
        left_operand = node[1]
        right_operand = node[2]
        print(f'<RelationalExpression operator="{operator}">')
        self.indent_level += 1
        self.visit(left_operand)
        self.visit(right_operand)
        self.indent_level -= 1
        self.indent()
        print('</RelationalExpression>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_BLOCK(self, node):
        self.indent()
        print('<BlockStatement>')
        self.indent_level += 1

        for statement in node[1]:
            self.visit(statement)

        self.indent_level -= 1
        self.indent()
        print('</BlockStatement>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_WHILE(self, node):
        self.indent()
        print('<WhileStatement>')
        self.indent_level += 1

        self.visit(node[1])

        self.visit(node[2])

        self.indent_level -= 1
        self.indent()
        print('</WhileStatement>')

    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_FUNCTION_DEF(self, node):
        self.indent()
        print(f'<FunctionDefinition name="{node[1]}">')
        self.indent_level += 1

        # Visit the list of parameters
        for parameter in node[2]:
            self.indent()
            print(f'<Parameter name="{parameter[0]}" type="{parameter[1]}"/>')

        # Visit the return type
        self.indent()
        print(f'<ReturnType>{node[3]}</ReturnType>')

        # Visit the function body
        self.visit(node[4])

        self.indent_level -= 1
        self.indent()
        print('</FunctionDefinition>')
        
    def visit_RETURN(self, node):
        self.indent()
        print('<ReturnStatement>')
        self.indent_level += 1

        # Visit the expression being returned
        self.visit(node[1])

        self.indent_level -= 1
        self.indent()
        print('</ReturnStatement>')

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

        self.visit(node[1]) 

        self.indent_level -= 1
        self.indent()
        print('</ReturnStatement>')
    
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_PRINT(self, node):
        self.indent()
        print('<PrintStatement>')
        self.indent_level += 1

        self.visit(node[1]) 

        self.indent_level -= 1
        self.indent()
        print('</PrintStatement>')

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_DELAY(self, node):
        self.indent()
        print(f'<DelayStatement time="{node[1][1]}" />')

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_WIDTH(self, node):
        self.indent()
        print(f'<Width width="{node[1][1]}" />')

    def visit_HEIGHT(self, node):
        self.indent()
        print(f'<Height height="{node[1][1]}" />')

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_READ_STATEMENT(self, node):
        self.indent()
        print('<ReadStatement>')
        self.indent_level += 1

        for arg in node[1]:
            self.visit(arg)

        self.indent_level -= 1
        self.indent()
        print('</ReadStatement>')

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_PIXEL_STATEMENT(self, node):
        self.indent()
        print('<PixelStatement>')
        self.indent_level += 1

        for arg in node[1:]:
            self.visit(('INTEGER_LITERAL', arg))

        self.indent_level -= 1
        self.indent()
        print('</PixelStatement>')

    def visit_PIXELR_STATEMENT(self, node):
        self.indent()
        print('<PixelrStatement>')
        self.indent_level += 1

        for arg in node[1:]:
            self.visit(('INTEGER_LITERAL', arg))

        self.indent_level -= 1
        self.indent()
        print('</PixelrStatement>')

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_FOR(self, node):
        self.indent()
        print('<ForStatement>')
        self.indent_level += 1

        self.indent()
        print('<Initialization>')
        self.visit(node[1])
        print('</Initialization>')

        self.indent()
        print('<Condition>')
        self.visit(node[2])
        print('</Condition>')

        self.indent()
        print('<Update>')
        self.visit(node[3])
        print('</Update>')

        self.indent()
        print('<Body>')
        self.visit(node[4])
        print('</Body>')

        self.indent_level -= 1
        self.indent()
        print('</ForStatement>')
        
    def visit_ASSIGNMENT(self, node):
        self.indent()
        print('<Assignment>')
        self.indent_level += 1

        self.visit(('IDENTIFIER', node[1]))

        self.indent()
        print('<Operator>', node[0], '</Operator>')

        self.visit(node[2])  

        self.indent_level -= 1
        self.indent()
        print('</Assignment>')

    #---------------------------------------------------------------------------------------------------------------------------------------
    
###########################################################################################################################################

    def indent(self):
        print(' ' * 2 * self.indent_level, end='')
        
###########################################################################################################################################
        
# Usage:
source_code = """
let x: int = 5 * 20 + 5;
let y: float = 3.14;
let z: bool = true;
let v: bool = false;
let w: colour = #FF0000;
"""

#try:
#    lexer = Lexer(source_code)
#    tokens = lexer.tokenize()
#    parser = Parser(tokens)
#    ast = parser.parse()#

#    print("\nXML Representation:\n")    
#    xml_generator = ASTXMLGenerator(ast)
#    for node in ast:
#        xml_generator.visit(node)
#    print("\n" + "-"*100)#

#except LexerError as e:
#    print(f"Error: {e}")
#except ParserError as e:
#    print(f"Error: {e}")