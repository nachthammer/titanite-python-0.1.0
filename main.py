import numpy as np
from sys import getsizeof

from evaluator import Evaluator
from lexer import Lexer
from parser import Parser

expression = "(2/5)/3"
lexer = Lexer(expression)
lexer.run_lexer()
tokens = lexer.get_token_objects()
parser = Parser(tokens)
tree = parser.parse()
evaluator = Evaluator(tree)
print(evaluator.evaluate())

