from lexer import TokenObject, Token, TokenType, LocationInformation
from parser import BinaryExpr, LiteralExpr, UnaryExpr

tokens_for_plus_and_minus = [
    TokenObject(Token(TokenType.INT, 1), LocationInformation(start_line=1, end_line=1, start_col=0, end_col=1)),
    TokenObject(Token(TokenType.PLUS), LocationInformation(start_line=1, end_line=1, start_col=2, end_col=3)),
    TokenObject(Token(TokenType.INT, 2), LocationInformation(start_line=1, end_line=1, start_col=4, end_col=5)),
    TokenObject(Token(TokenType.MINUS), LocationInformation(start_line=1, end_line=1, start_col=6, end_col=7)),
    TokenObject(Token(TokenType.INT, 3), LocationInformation(start_line=1, end_line=1, start_col=8, end_col=9)),
    TokenObject(Token(TokenType.PLUS), LocationInformation(start_line=1, end_line=1, start_col=10, end_col=11)),
    TokenObject(Token(TokenType.INT, 56), LocationInformation(start_line=1, end_line=1, start_col=12, end_col=14)),
    TokenObject(Token(TokenType.MINUS), LocationInformation(start_line=1, end_line=1, start_col=15, end_col=16)),
    TokenObject(Token(TokenType.INT, 5), LocationInformation(start_line=1, end_line=1, start_col=17, end_col=18))]

parser_tree_for_plus_and_minus = BinaryExpr(expr=BinaryExpr(
    expr=BinaryExpr(expr=BinaryExpr(expr=LiteralExpr(literal=1), operator=TokenType.PLUS, right=LiteralExpr(literal=2)),
                    operator=TokenType.MINUS, right=LiteralExpr(literal=5)), operator=TokenType.PLUS,
    right=LiteralExpr(literal=6)), operator=TokenType.MINUS, right=LiteralExpr(literal=8575))

double_minus_tree = BinaryExpr(expr=LiteralExpr(literal=2), operator=TokenType.MINUS, right=BinaryExpr(expr=UnaryExpr(operator=TokenType.MINUS, right=LiteralExpr(literal=5)), operator=TokenType.MUL, right=LiteralExpr(literal=6)))

parser_tree_for_all_arithmetic_operations = BinaryExpr(
    expr=BinaryExpr(expr=LiteralExpr(literal=1), operator=TokenType.PLUS,
                    right=BinaryExpr(expr=LiteralExpr(literal=2), operator=TokenType.MUL,
                                     right=LiteralExpr(literal=5))), operator=TokenType.MINUS,
    right=BinaryExpr(expr=LiteralExpr(literal=6), operator=TokenType.DIV, right=LiteralExpr(literal=9)))
