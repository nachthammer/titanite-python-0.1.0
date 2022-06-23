import numpy as np
from sys import getsizeof

from evaluator import Evaluator
from lexer import Lexer
from parser import Parser
from statements import StatementParser


def get_tokens(code: str):
    lexer = Lexer(code)
    lexer.run_lexer()
    return lexer.get_token_objects()


def execute(string: str):
    tokens = get_tokens(string)
    #print(tokens)
    statement_parser = StatementParser(tokens)
    statement_parser.parse()
    return statement_parser.interpret()


store = execute("int a = 1 \n a = 2")
print(store)


