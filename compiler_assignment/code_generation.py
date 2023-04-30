from lexer import *
from parser_ import *
from semantic_analayzer import *
from collections import deque

class PixIRGenerator:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.program = []
        self.function_table = {}
        self.function_name = ''
        self.current_scope = deque() # Use deque to easily append and pop from both ends
        self.current_frame_size = 0
        self.current_frame_index = 0
        self.current_level = 0
        self.pc = 0 # Program counter

    def generate(self, node):
        self.visit(node)
        return self.program

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.error)
        return visitor(node)

    def visit_PROGRAM(self, node):
        # Visit all function declarations first
        for function_decl in node[:-1]:
            self.visit(function_decl)

        # Then visit the main function
        self.visit(node[-1])

    def visit_FUNCTION_DECLARATION(self, node):
        # Add the function to the function table
        _, return_type, name, parameters, block = node
        function = Function(return_type, parameters, block)
        self.function_table[name] = function

    def visit_FUNCTION(self, node):
        # Start a new scope for the function
        self.symbol_table.push_scope()
        self.function_name = node[1]

        # Add the function to the program with a label
        self.program.append(Label(self.function_name))

        # Visit the block
        self.visit(node[2])

        # Add a return instruction
        self.program.append(Ret())

        # Pop the function scope
        self.symbol_table.pop_scope()
        self.function_name = ''

    def visit_BLOCK(self, node):
        # Start a new scope for the block
        self.symbol_table.push_scope()
        self.current_level += 1

        # Visit each statement in the block
        for statement in node:
            self.visit(statement)

        # Pop the block scope
        self.symbol_table.pop_scope()
        self.current_level -= 1

    def visit_DECLARATION(self, node):
        _, var_type, var_name, value = node

        # Add the variable to the symbol table
        self.symbol_table.add(var_name, var_type)

        # If there is an initial value, generate code to push it onto the operand stack
        if value:
            self.visit(value)
            self.program.append(St(self.current_frame_index, self.current_level))
            self.current_frame_index += 1

    def visit_ASSIGNMENT(self, node):
        _, var_name, value = node

        # Get the variable's memory location from the symbol table
        var_location = self.symbol_table.get(var_name)

        # Generate code to push the variable's memory location onto the operand stack
        self.program.append(Push(var_location[0]))
        self.program.append(Push(var_location[1]))

        # Visit the value expression and generate code to push its result onto the operand stack
        self.visit(value)

        # Generate the st instruction to store the value in memory
        self.program.append(St(var_location[2], var_location[1]))

    # TODO: Implement visit_FOR, visit_PRINT, and all other remaining visit methods

    def error(self, node):
        raise Exception('Unsupported node type {}'.format(type(node).__name__))
