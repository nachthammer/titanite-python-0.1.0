import unittest

from lexer import is_allowed_identifier, Lexer, Token, TokenType


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
        self.lexer = Lexer("int a = 5")
        tokens = self.lexer.get_tokens()
        print(tokens)
        self.assertEqual(len(tokens), 4)
        self.assertListEqual(tokens, [Token(TokenType.INT), Token(TokenType.IDENTIFIER, "a"), Token(TokenType.ASSIGNMENT), Token(TokenType.INT, 5)])

    def test_simple_for_loop(self):
        self.lexer = Lexer("""
        for (int i in a) {
            int b = 6
        }
        """)
        tokens = self.lexer.get_tokens()
        print(tokens)
        simple_for_loop_tokens = [
            Token(TokenType.FOR), Token(TokenType.LEFT_BRACKET), Token(TokenType.INT), Token(TokenType.IDENTIFIER, "i"),
            Token(TokenType.IN), Token(TokenType.IDENTIFIER, "a"), Token(TokenType.RIGHT_BRACKET), 
            Token(TokenType.LEFT_CURLY_BRACKET),Token(TokenType.INT), Token(TokenType.IDENTIFIER, "b"),
            Token(TokenType.ASSIGNMENT), Token(TokenType.INT, 6),
            Token(TokenType.RIGHT_CURLY_BRACKET)
        ]
        self.assertEqual(len(tokens), 13)
        self.assertListEqual(simple_for_loop_tokens, tokens)






if __name__ == '__main__':
    unittest.main()
