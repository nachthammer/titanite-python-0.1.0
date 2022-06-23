import unittest

from lexer import Lexer, TokenObject, TokenType
from parser import Parser, LiteralExpr, BinaryExpr, GroupingExpr, UnaryExpr
from evaluator import Evaluator
from errors import ParserError, LexerError
from classes import Environment

from typing import List


def get_tokens(code: str) -> List[TokenObject]:
    lexer = Lexer(code)
    lexer.run_lexer()
    return lexer.get_token_objects()


def evaluate_string(string: str):
    tokens = get_tokens(string)
    parser = Parser(tokens)
    parsed_tree = parser.parse()
    evaluator = Evaluator(parsed_tree)
    environment = Environment()
    return evaluator.evaluate(environment)


class SimpleArithmeticsExpressions(unittest.TestCase):
    def test_plus_works(self):
        self.assertEqual(evaluate_string("11+23"), 34)
        self.assertEqual(evaluate_string("1+2+3+4+5"), 15)
        self.assertEqual(evaluate_string("(1+2)+(78+6)"), 87)

    def test_minus_works(self):
        self.assertEqual(evaluate_string("1-221"), -220)
        self.assertEqual(evaluate_string("1- -1"), 2)
        self.assertEqual(evaluate_string("1- -(-1)"), 0)
        with self.assertRaises(ParserError):
            evaluate_string("1- --1")
        self.assertEqual(-9, evaluate_string("-2-3-4"))

    def test_mul_works(self):
        self.assertEqual(10, evaluate_string("2*5"))
        self.assertEqual(120, evaluate_string("1*2*3*4*5"))
        self.assertEqual(120, evaluate_string("(1*2)*(3*4*5)"))
        self.assertEqual(-120, evaluate_string("(1*2)*(-3*-4*-5)"))
        with self.assertRaises(ParserError):
            evaluate_string("(1**2)*(-3*-4*-5)")

    def test_div_works(self):
        self.assertEqual(evaluate_string("2/5"), 0.4)
        self.assertEqual(evaluate_string("2/5/6/2"), 1 / 30)
        self.assertEqual(evaluate_string("(2/5)/(6/2)"), 2 / 15)


class StackedArithmeticExpressions(unittest.TestCase):
    def test_plus_and_minus(self):
        self.assertEqual(evaluate_string("2+3-5"), 0)
        self.assertEqual(evaluate_string("(2+3)-5"), 0)
        self.assertEqual(evaluate_string("2-12-5+10"), -5)

    def test_mul_and_div(self):
        self.assertEqual(evaluate_string("2*5/6"), 10/6)
        # rounding error
        self.assertAlmostEqual(evaluate_string("2/5*6"), 12 / 5)

    def test_complex_arithmetic_expressions(self):
        self.assertEqual(evaluate_string(" 1+ 2*5/6 + 4 - 2"), 10/6 + 3)
        self.assertAlmostEqual(evaluate_string(" 1 + 2/5*6"), 17 / 5)


class BooleanExpressions(unittest.TestCase):
    def test_simple_boolean_expressions(self):
        self.assertEqual(False, evaluate_string("1 == 2"))
        self.assertEqual(True, evaluate_string("1 == 1"))
        self.assertEqual(False, evaluate_string("1 != 1"))
        self.assertEqual(True, evaluate_string("1 != 2"))
        self.assertEqual(False, evaluate_string("true && false"))
        self.assertTrue(evaluate_string("true || false"))
        self.assertEqual(True, evaluate_string("!false"))


class StringExpressions(unittest.TestCase):
    def test_simple_strings(self):
        self.assertEqual("lala", evaluate_string('"lala"'))
        self.assertEqual("lala", evaluate_string('("lala")'))








