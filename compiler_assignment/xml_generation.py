# Import all definitions from the lexer and parser code
from lexer import *
from parser_ import *

# Class for generating an XML representation of the AST
class ASTXMLGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.indent_level = 0
        
###########################################################################################################################################

    def visit(self, node):
        # Determine the method name for the node type
        method_name = f"visit_{node[0]}"
        # Get the method to visit the node type, or use the generic visit method if not implemented
        visit_method = getattr(self, method_name, self.generic_visit)
        # Visit the node using the appropriate method
        return visit_method(node)
    
    # Generic visit method for unsupported node types
    def generic_visit(self, node):
        raise NotImplementedError(f"Visit method for node type {node[0]} not implemented.")
    
###########################################################################################################################################
        
    def visit_PROGRAM(self, node):
        # Opening tag for Program
        print('<Program>')
        self.indent_level += 1
        # Visit each child node of Program
        for child in node[1:]:
            self.visit(child)
        self.indent_level -= 1
        # Closing tag for Program
        print('</Program>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_DECLARATION(self, node):
        # Opening tag for Declaration with type and identifier attributes
        self.indent()
        print(f'<Decl type="{node[1]}" identifier="{node[2]}">')
        self.indent_level += 1

        # If there is an expression, visit it
        if len(node) > 3:
            self.visit(node[3])

        self.indent_level -= 1
        # Closing tag for Declaration
        self.indent()
        print('</Decl>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_INTEGER_LITERAL(self, node):
        # IntegerLiteral tag with value attribute
        self.indent()
        print(f'<IntegerLiteral value="{node[1]}" />')

    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_BOOLEAN_LITERAL(self, node):
        # Indent and print the opening tag with the boolean value as an attribute
        self.indent()
        print(f'<BooleanLiteral value="{node[1]}" />')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_BINARY_EXPRESSION(self, node):
        # Print opening tag for the binary expression
        self.indent()
        print(f'<BinaryExpression operator="{node[1]}">')
        # Increase indentation level for nested nodes
        self.indent_level += 1

        # Visit left child node
        self.visit(node[2])
        # Visit right child node
        self.visit(node[3])

        # Decrease indentation level back to original level
        self.indent_level -= 1
        # Print closing tag for the binary expression
        self.indent()
        print('</BinaryExpression>')
        
    def visit_PLUS(self, node):
        # Print opening tag for the plus expression
        self.indent()
        print(f'<BinaryExpression operator="+">')
        # Increase indentation level for nested nodes
        self.indent_level += 1

        # Visit left child node
        self.visit(node[1])
        # Visit right child node
        self.visit(node[2])

        # Decrease indentation level back to original level
        self.indent_level -= 1
        # Print closing tag for the plus expression
        self.indent()
        print('</BinaryExpression>')
        
    def visit_MUL(self, node):
        # Print opening tag for the multiplication expression
        self.indent()
        print(f'<BinaryExpression operator="*">')
        # Increase indentation level for nested nodes
        self.indent_level += 1

        # Visit left child node
        self.visit(node[1])
        # Visit right child node
        self.visit(node[2])

        # Decrease indentation level back to original level
        self.indent_level -= 1
        # Print closing tag for the multiplication expression
        self.indent()
        print('</BinaryExpression>')
        
    def visit_MINUS(self, node):
        # Print opening tag for the minus expression
        self.indent()
        print('<MinusExpression>')

        # Increase indentation level for nested nodes
        self.indent_level += 1
        # Visit left child node
        self.visit(node[1])
        # Visit right child node
        self.visit(node[2])
        # Decrease indentation level back to original level
        self.indent_level -= 1

        # Print closing tag for the minus expression
        self.indent()
        print('</MinusExpression>')
        
    def visit_DIV(self, node):
        # Print opening tag for the division expression
        self.indent()
        print('<DivExpression>')
        # Increase indentation level for nested nodes
        self.indent_level += 1

        # Visit child nodes
        for child_node in node[1:]:
            self.visit(child_node)

        # Decrease indentation level back to original level
        self.indent_level -= 1
        # Print closing tag for the division expression
        self.indent()
        print('</DivExpression>')
        
    def visit_LOGICAL_OPERATOR(self, node):
        # Determine the logical operator based on the node's value
        operator = "and" if node[1] == "and" else "or"
        # Print opening tag for the logical operator expression
        self.indent()
        print(f'<LogicalExpression operator="{operator}">')
        # Increase indentation level for nested nodes
        self.indent_level += 1

        # Visit left child node
        self.visit(node[2]) 
        
        # Visit right child node if it exists        
        if len(node) > 3:
            self.visit(node[3]) 

        # Decrease indentation level and close logical expression tag
        self.indent_level -= 1
        self.indent()
        print('</LogicalExpression>')

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_NUMBER(self, node):
        # Print the number element with its value
        self.indent()
        print(f'<Number value="{node[1]}" />')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_TYPE(self, node):
        # Print the type element with its value
        self.indent()
        print(f'<Type>{node[1]}</Type>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_IDENTIFIER(self, node):
        # Print the identifier element with its name
        self.indent()
        print(f'<Identifier name="{node[1]}" />')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_FLOAT_LITERAL(self, node):
        # Print the float literal element with its value
        self.indent()
        print(f'<FloatLiteral value="{node[1]}" />')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_STRING_LITERAL(self, node):
        # Print the string literal element with its value
        self.indent()
        print(f'<StringLiteral value="{node[1]}" />')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_COLOR_LITERAL(self, node):
        # Print the color literal element with its value
        self.indent()
        print(f'<ColorLiteral value="{node[1]}" />')
        
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_UNARY_EXPRESSION(self, node):
        # Print opening tag with unary operator
        self.indent()
        print(f'<UnaryExpression operator="{node[1]}">')
        self.indent_level += 1

        # Visit child node
        self.visit(node[2])

        # Print closing tag
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
        # Indent and print the opening tag for the relational expression
        self.indent()
        operator = node[0]
        left_operand = node[1]
        right_operand = node[2]
        print(f'<RelationalExpression operator="{operator}">')
        self.indent_level += 1
        
        # Visit the left and right operands
        self.visit(left_operand)
        self.visit(right_operand)
        
        # Un-indent and print the closing tag for the relational expression
        self.indent_level -= 1
        self.indent()
        print('</RelationalExpression>')

    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_BLOCK(self, node):
        # Start the BlockStatement tag
        self.indent()
        print('<BlockStatement>')
        self.indent_level += 1

        # Visit each statement in the block
        for statement in node[1]:
            self.visit(statement)

        # End the BlockStatement tag
        self.indent_level -= 1
        self.indent()
        print('</BlockStatement>')
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_WHILE(self, node):
        # Start the WhileStatement tag
        self.indent()
        print('<WhileStatement>')
        self.indent_level += 1

        # Visit the condition expression and the loop body
        self.visit(node[1])
        self.visit(node[2])

        # End the WhileStatement tag
        self.indent_level -= 1
        self.indent()
        print('</WhileStatement>')

    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_FUNCTION_DEF(self, node):
        # Print the opening tag for function definition
        self.indent()
        print(f'<FunctionDefinition name="{node[1]}">')
        self.indent_level += 1

        # Visit the list of parameters
        for parameter in node[2]:
            # Print the opening tag for parameter
            self.indent()
            print(f'<Parameter name="{parameter[0]}" type="{parameter[1]}"/>')

        # Print the return type of function
        self.indent()
        print(f'<ReturnType>{node[3]}</ReturnType>')

        # Visit the function body
        self.visit(node[4])

        # Print the closing tag for function definition
        self.indent_level -= 1
        self.indent()
        print('</FunctionDefinition>')
        
    def visit_RETURN(self, node):
        # Print the opening tag for return statement
        self.indent()
        print('<ReturnStatement>')
        self.indent_level += 1

        # Visit the expression being returned
        self.visit(node[1])

        # Print the closing tag for return statement
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
        # Open ArgumentList tag
        self.indent()
        print('<ArgumentList>')
        self.indent_level += 1

        # Visit each argument in the argument list
        for arg in node[1:]:
            self.visit(arg)

        # Close ArgumentList tag
        self.indent_level -= 1
        self.indent()
        print('</ArgumentList>')

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_STATEMENT_BLOCK(self, node):
        # Open StatementBlock tag
        self.indent()
        print('<StatementBlock>')
        self.indent_level += 1

        # Visit each statement in the statement block
        for stmt in node[1:]:
            self.visit(stmt)

        # Close StatementBlock tag
        self.indent_level -= 1
        self.indent()
        print('</StatementBlock>')
    
    #---------------------------------------------------------------------------------------------------------------------------------------
        
    def visit_PRINT(self, node):
        # Print the opening tag for PrintStatement
        self.indent()
        print('<PrintStatement>')
        self.indent_level += 1

        # Visit the expression to be printed
        self.visit(node[1]) 

        # Print the closing tag for PrintStatement
        self.indent_level -= 1
        self.indent()
        print('</PrintStatement>')

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_DELAY(self, node):
        # Print the opening tag for DelayStatement with the time attribute
        self.indent()
        print(f'<DelayStatement time="{node[1][1]}" />')

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_WIDTH(self, node):
        # Print the opening tag for the Width statement
        self.indent()
        print(f'<Width width="{node[1][1]}" />')

    def visit_HEIGHT(self, node):
        # Print the opening tag for the Height statement
        self.indent()
        print(f'<Height height="{node[1][1]}" />')

    #---------------------------------------------------------------------------------------------------------------------------------------

    def visit_READ_STATEMENT(self, node):
        # Print the opening tag for the ReadStatement
        self.indent()
        print('<ReadStatement>')
        self.indent_level += 1

        # Visit the list of arguments
        for arg in node[1]:
            self.visit(arg)

        # Print the closing tag for the ReadStatement
        self.indent_level -= 1
        self.indent()
        print('</ReadStatement>')

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_PIXEL_STATEMENT(self, node):
        # Start PixelStatement tag
        self.indent()
        print('<PixelStatement>')
        self.indent_level += 1

        # Visit each argument and create INTEGER_LITERAL tag for each
        for arg in node[1:]:
            self.visit(('INTEGER_LITERAL', arg))

        self.indent_level -= 1

        # End PixelStatement tag
        self.indent()
        print('</PixelStatement>')


    def visit_PIXELR_STATEMENT(self, node):
        # Start PixelrStatement tag
        self.indent()
        print('<PixelrStatement>')
        self.indent_level += 1

        # Visit each argument and create INTEGER_LITERAL tag for each
        for arg in node[1:]:
            self.visit(('INTEGER_LITERAL', arg))

        self.indent_level -= 1

        # End PixelrStatement tag
        self.indent()
        print('</PixelrStatement>')

    #---------------------------------------------------------------------------------------------------------------------------------------
    
    def visit_FOR(self, node):
        self.indent()
        print('<ForStatement>')
        self.indent_level += 1

        # Visit initialization expression
        self.indent()
        print('<Initialization>')
        self.visit(node[1])
        print('</Initialization>')

        # Visit condition expression
        self.indent()
        print('<Condition>')
        self.visit(node[2])
        print('</Condition>')

        # Visit update expression
        self.indent()
        print('<Update>')
        self.visit(node[3])
        print('</Update>')

        # Visit the body of the loop
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

        # Visit the identifier being assigned to
        self.visit(('IDENTIFIER', node[1]))

        # Print the assignment operator
        self.indent()
        print('<Operator>', node[0], '</Operator>')

        # Visit the expression being assigned
        self.visit(node[2])  

        self.indent_level -= 1
        self.indent()
        print('</Assignment>')

    #---------------------------------------------------------------------------------------------------------------------------------------
    
###########################################################################################################################################

    # Define a method to indent the generated XML code based on the current indent level
    def indent(self):
        print(' ' * 2 * self.indent_level, end='')
        
###########################################################################################################################################
        
# Usage:

## Specify the name of the file
#filename = 'input.txt'#

## Open the file and read the contents into a string
#with open(filename, 'r') as file:
#    source_code = file.read()#

#try:
#    # Tokenize the source code
#    lexer = Lexer(source_code)
#    tokens = lexer.tokenize()#

#    # Parse the tokens into an abstract syntax tree (AST)
#    parser = Parser(tokens)
#    ast = parser.parse()#

#    # Generate an XML representation of the AST
#    print("\n" + "-"*100)
#    print("\nXML Representation:\n")    
#    xml_generator = ASTXMLGenerator(ast)
#    for node in ast:
#        xml_generator.visit(node)#

## Catch and report lexer errors
#except LexerError as e:
#    print(f"Error: {e}")
## Catch and report parser errors
#except ParserError as e:
#    print(f"Error: {e}")
#    
#print("\n" + "-"*100)