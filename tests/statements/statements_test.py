import unittest

from lexer import Lexer, TokenObject, TokenType
from parser import Parser, LiteralExpr, BinaryExpr, GroupingExpr, UnaryExpr
from evaluator import Evaluator
from errors import ParserError, LexerError
from statements import StatementParser

from typing import List


def get_tokens(code: str) -> List[TokenObject]:
    lexer = Lexer(code)
    lexer.run_lexer()
    return lexer.get_token_objects()


def execute(string: str):
    tokens = get_tokens(string)
    #print(tokens)
    statement_parser = StatementParser(tokens)
    statement_parser.parse()
    statement_parser.interpret()


class SimplePrintStatements(unittest.TestCase):
    def test_simple_prints(self):
        execute('write("lala")')
        execute('write(1+2)\nwrite("lala")')


class VariableDeclarationStatements(unittest.TestCase):
    def test_simple_variable_declarations(self):
        execute('int a = 5')
        execute('str b = "lalelu"\nint a = 6\ndouble a = 7.6')

    def test_variables_data_is_reusable(self):
        execute('int a = 5\nint b = (a+a)')

