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
    return statement_parser.interpret()


class SimplePrintStatements(unittest.TestCase):
    def test_simple_prints(self):
        execute('write("lala");')
        execute('write(1+2); write("lala");')


class VariableDeclarationStatements(unittest.TestCase):
    def test_simple_variable_declarations(self):
        store = execute('int a = 5;')
        self.assertEqual(5, store["a"])
        store = execute('str b = "lalelu";\nint a = 6;\ndouble a = 7.6;')
        self.assertEqual("lalelu", store["b"])
        #self.assertEqual(6, store["a"])
        self.assertEqual(7.6, store["a"])

    def test_complicated_boolean_expressions_to_variable(self):
        store = execute('bool b = true && true;')
        self.assertTrue(store["b"])
        store = execute('bool b = (true && true) && (false && false) || true;')
        self.assertTrue(store["b"])
        store = execute('bool b = ((false && true) && (false || false)) || false;')
        self.assertFalse(store["b"])

    def test_variables_data_is_reusable(self):
        store = execute('int a = 1;\nint b = (a+2);')
        self.assertEqual(3, store["b"])
        store = execute('bool a = true;\nbool b = (a || false);')
        self.assertTrue(store["b"])

    def test_data_can_be_assigned(self):
        store = execute("int a = 1; \n a = 2;")
        self.assertEqual(2, store["a"])
        store = execute("""
        int a = 1;
        {
            int b = 2;
            int c = 3;
        }
        """)
        self.assertEqual(1, store["a"])


class IfStatements(unittest.TestCase):
    def test_simple_if_statement(self):
        store = execute("""
        int a = 1;
        if (true) {
            a = 2;
        }
        """)
        self.assertEqual(2, store["a"])

