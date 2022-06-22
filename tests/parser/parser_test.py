import unittest

from lexer import Lexer, TokenObject, TokenType
from parser import Parser, LiteralExpr, BinaryExpr, GroupingExpr, UnaryExpr
from tests.parser.parser_snap import tokens_for_plus_and_minus, parser_tree_for_all_arithmetic_operations, \
    parser_tree_for_plus_and_minus, double_minus_tree

from typing import List


def get_tokens(code: str) -> List[TokenObject]:
    lexer = Lexer(code)
    lexer.run_lexer()
    return lexer.get_token_objects()


class SimpleArithmeticsExpressions(unittest.TestCase):
    def test_plus_and_minus_work(self):
        tokens = get_tokens("1 + 2 - 5 + 6 - 8575")
        parser = Parser(tokens)
        parsed_tree = (parser.parse())
        print(parsed_tree)
        self.assertEqual(parser_tree_for_plus_and_minus, parsed_tree)

    #@unittest.skip("double minus is not supported yet.")
    def test_double_minus_works(self):
        tokens = get_tokens("2 - -5 * 6")
        parser = Parser(tokens)
        parsed_tree = (parser.parse())
        print("parsed_Tree", parsed_tree)
        self.assertEqual(double_minus_tree, parsed_tree)
        #self.assertEqual(False, True)

    def test_all_arithmetic_operators_work(self):
        tokens = get_tokens("1 + 2 * 5 - 6 / 9")
        parser = Parser(tokens)
        parsed_tree = (parser.parse())
        print(parsed_tree)
        self.assertEqual(parser_tree_for_all_arithmetic_operations, parsed_tree)
