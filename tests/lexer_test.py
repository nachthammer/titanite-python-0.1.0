import unittest

from lexer import is_allowed_identifier


class MyTestCase(unittest.TestCase):
    def test_allowed_identifiers(self):
        self.assertEqual(is_allowed_identifier("a"), True)
        self.assertEqual(is_allowed_identifier("A"), True)
        self.assertEqual(is_allowed_identifier("aA"), True)
        self.assertEqual(is_allowed_identifier("a78"), True)

    def test_not_allowed_identifiers(self):
        self.assertEqual(is_allowed_identifier("a|8"), False)
        self.assertEqual(is_allowed_identifier("0aa"), False)
        self.assertEqual(is_allowed_identifier("_0aa"), False)


if __name__ == '__main__':
    unittest.main()
