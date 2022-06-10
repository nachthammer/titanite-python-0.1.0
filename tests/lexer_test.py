import unittest

from lexer import is_allowed_identifier, Lexer, Token, TokenType
from tests.lexer_snap_test import fizzbuzz_tokens


class EqualsWorksForClasses(unittest.TestCase):
    def test_equals_works_for_token_type_enum(self):
        self.assertTrue(TokenType.INT == TokenType.INT)
        self.assertTrue(TokenType.FALSE == TokenType.FALSE)
        self.assertFalse(TokenType.FALSE == TokenType.INT)

    def test_equals_works_for_token_class(self):
        self.assertTrue(Token(TokenType.INT, 5) == Token(TokenType.INT, 5))
        self.assertTrue(Token(TokenType.FALSE) == Token(TokenType.FALSE))
        self.assertFalse(Token(TokenType.INT, 5) == Token(TokenType.INT, 0))
        self.assertFalse(Token(TokenType.TRUE) == Token(TokenType.TRUE, 0))


class Allowed_Identifiers_Test(unittest.TestCase):
    def test_allowed_identifiers(self):
        self.assertEqual(is_allowed_identifier("a"), True)
        self.assertEqual(is_allowed_identifier("A"), True)
        self.assertEqual(is_allowed_identifier("aA"), True)
        self.assertEqual(is_allowed_identifier("a78"), True)

    def test_not_allowed_identifiers(self):
        self.assertEqual(is_allowed_identifier("a|8"), False)
        self.assertEqual(is_allowed_identifier("0aa"), False)
        self.assertEqual(is_allowed_identifier("_0aa"), False)


class Simple_Statements(unittest.TestCase):
    def test_simple_assignment(self):
        lexer = Lexer("int a = 5")
        lexer.run_lexer()
        tokens = lexer.get_tokens()
        self.assertListEqual(tokens,
                             [Token(TokenType.INT), Token(TokenType.IDENTIFIER, "a"), Token(TokenType.ASSIGNMENT),
                              Token(TokenType.INT, 5)])

    def test_simple_for_loop(self):
        lexer = Lexer("""
        for (int i in a) {
            int b = 6
        }
        """)
        lexer.run_lexer()
        tokens = lexer.get_tokens()
        simple_for_loop_tokens = [
            Token(TokenType.FOR), Token(TokenType.LEFT_BRACKET), Token(TokenType.INT), Token(TokenType.IDENTIFIER, "i"),
            Token(TokenType.IN), Token(TokenType.IDENTIFIER, "a"), Token(TokenType.RIGHT_BRACKET),
            Token(TokenType.LEFT_CURLY_BRACKET), Token(TokenType.INT), Token(TokenType.IDENTIFIER, "b"),
            Token(TokenType.ASSIGNMENT), Token(TokenType.INT, 6),
            Token(TokenType.RIGHT_CURLY_BRACKET)
        ]
        self.assertListEqual(simple_for_loop_tokens, tokens)

    def test_fizz_buzz(self):
        lexer = Lexer("""for (int i in nums(1,101)) {
    if (mod(1,15) == 0) {
        write("FizzBuzz")
    } elif (mod(1,3) == 0) {
        write("Fizz")
    } elif (mod(1,5) == 0) {
        write("Buzz")
    } else {
        write(toStr(i))
    }
}
    """
                           )
        lexer.run_lexer()
        tokens = lexer.get_tokens()
        self.assertListEqual(tokens, fizzbuzz_tokens)


if __name__ == '__main__':
    unittest.main()
