from lexer import Token, TokenType, TokenObject
from abc import ABC, abstractmethod
from errors import ParserError
from typing import List
from classes import Environment


class Expr(ABC):
    @abstractmethod
    def evaluate(self, env: Environment):
        pass


class BinaryExpr(Expr):
    def __init__(self, expr, operator: TokenType, right: Expr):
        self.expr = expr
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinaryExpr(expr={self.expr}, operator={self.operator}, right={self.right})"

    def __eq__(self, other):
        if not isinstance(other, BinaryExpr):
            return False
        return self.expr == other.expr and self.operator == other.operator and self.right == other.right

    def evaluate(self, env: Environment):
        left = self.expr.evaluate(env)
        right = self.right.evaluate(env)
        if self.operator == TokenType.PLUS:
            return left + right
        elif self.operator == TokenType.MINUS:
            return left - right
        elif self.operator == TokenType.MUL:
            return left * right
        elif self.operator == TokenType.DIV:
            return left / right
        elif self.operator == TokenType.GREATER:
            return left > right
        elif self.operator == TokenType.GREATER_EQUALS:
            return left >= right
        elif self.operator == TokenType.LESSER:
            return left < right
        elif self.operator == TokenType.LESSER_EQUALS:
            return left <= right
        elif self.operator == TokenType.EQUALS:
            return left == right
        elif self.operator == TokenType.NOT_EQUALS:
            return left != right
        elif self.operator == TokenType.AND:
            return left and right
        elif self.operator == TokenType.OR:
            return left or right
        else:
            raise ParserError("Following operator is not supported for binary expression", )


class UnaryExpr(Expr):
    def __init__(self, operator: TokenType, right: Expr):
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"UnaryExpr(operator={self.operator}, right={self.right})"

    def __eq__(self, other):
        if not isinstance(other, UnaryExpr):
            return False
        return self.operator == other.operator and self.right == other.right

    def evaluate(self, env: Environment):
        evaluated_right = self.right.evaluate(env)
        if self.operator == TokenType.NOT:
            return not evaluated_right
        elif self.operator == TokenType.MINUS:
            if isinstance(evaluated_right, float) or isinstance(evaluated_right, int):
                return -evaluated_right
            else:
                raise ParserError(f"Cannot negate a non number: {evaluated_right}")
        else:
            raise ParserError(f"Could not evaluate this unary expression. {self}")


class LiteralExpr(Expr):
    def __init__(self, literal):
        self.literal = literal

    def __repr__(self):
        return f"LiteralExpr(literal={self.literal})"

    def __eq__(self, other):
        if not isinstance(other, LiteralExpr):
            return False
        return self.literal == other.literal

    def evaluate(self, env: Environment):
        if self.literal is None:
            raise ParserError("Could not evaluate None")
        return self.literal


class IdentifierExpr(Expr):
    def __init__(self, identifier):
        self.identifier = identifier

    def __repr__(self):
        return f"LiteralExpr(literal={self.identifier})"

    def __eq__(self, other):
        if not isinstance(other, IdentifierExpr):
            return False
        return self.identifier == other.identifier

    def evaluate(self, env: Environment):
        if self.identifier is None:
            raise ParserError("Could not evaluate None")
        return env.get_variable_value(self.identifier)


class GroupingExpr(Expr):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"GroupingExpr(expr={self.expr})"

    def __eq__(self, other):
        if not isinstance(other, GroupingExpr):
            return False
        return self.expr == other.expr

    def evaluate(self, env: Environment):
        if self.expr is None:
            raise ParserError("Could not evaluate None.")
        return self.expr.evaluate(env)


class Parser:
    """
    This parser
    """

    def __init__(self, tokens: List[TokenObject]):
        self.tokens = tokens
        self.index: int = 0
        self.length_of_expr = 0

    def __repr__(self):
        return f"Parser(tokens={self.tokens})"

    def parse(self):
        return self.expression()

    def advance(self):
        if self.index < len(self.tokens) - 1:
            self.index += 1
            self.length_of_expr += 1
        else:
            self.length_of_expr += 1

    def current_token_type_is(self, token_obj: TokenObject):
        return self.tokens[self.index].token.type == token_obj.token.type

    @property
    def current_token_type(self):
        return self.tokens[self.index].token.type

    @property
    def previous_token(self):
        return self.tokens[self.index - 1 if self.index-1 > -1 else self.index].token

    def expression(self):
        return self.logic_or()

    def match_type(self, token_types: List[TokenType]) -> bool:
        for token_type in token_types:
            if token_type == self.tokens[self.index].token.type:
                return True
        return False

    def logic_or(self):
        expr = self.logic_and()
        while self.current_token_type == TokenType.OR:
            self.advance()
            right  = self.logic_and()
            expr = BinaryExpr(expr, TokenType.OR, right)
        return expr

    def logic_and(self):
        expr = self.equality()
        while self.current_token_type == TokenType.OR:
            self.advance()
            right = self.equality()
            expr = BinaryExpr(expr, TokenType.AND, right)
        return expr

    def equality(self):
        """
        equality -> comparison ( ( "!="  | "==" ) comparison )*
        :return:
        """
        expr = self.comparison()
        while (self.current_token.type == TokenType.EQUALS) or (
                self.current_token.type == TokenType.NOT_EQUALS):
            operator = self.current_token
            self.advance()
            right = self.comparison()
            expr = BinaryExpr(expr, operator.type, right)
        return expr

    def comparison(self):
        """
        comparison -> term ( ( ">" | ">=" | "<" | "<=" ) term ) *
        :return:
        """
        comparison = self.term()
        while self.match_type([TokenType.GREATER, TokenType.GREATER_EQUALS, TokenType.LESSER_EQUALS, TokenType.LESSER]):
            operator = self.current_token
            self.advance()
            right = self.term()
            comparison = BinaryExpr(comparison, operator.type, right)
        return comparison

    def term(self):
        """
        term           → factor ( ( "-" | "+" ) factor )* ;
        :return:
        """
        term = self.factor()

        while self.match_type([TokenType.MINUS, TokenType.PLUS]):
            operator = self.current_token_type
            self.advance()
            right = self.factor()
            term = BinaryExpr(term, operator, right)

        return term

    def factor(self):
        """
        factor         → unary ( ( "/" | "*" ) unary )* ;
        :return:
        """
        factor = self.unary()

        while self.match_type([TokenType.DIV, TokenType.MUL]):
            operator = self.current_token_type
            self.advance()
            right = self.unary()
            factor = BinaryExpr(factor, operator, right)

        return factor

    def unary(self):
        """
        unary          → ( "!" | "-" ) unary | primary ;
        :return:
        """
        while self.match_type([TokenType.NOT, TokenType.MINUS]):
            operator = self.current_token_type
            self.advance()
            right = self.primary()
            return UnaryExpr(operator, right)

        return self.primary()

    def primary(self):
        """
        primary        → int | string | true | false | "(" expression ")" | identifier;
        :return:
        """
        if self.current_token_type == TokenType.IDENTIFIER:
            literal_expr = IdentifierExpr(self.current_token.value)
            self.advance()
            return literal_expr
        elif self.current_token_type == TokenType.INT and self.current_token.value is not None:
            literal_expr = LiteralExpr(self.current_token.value)
            self.advance()
            return literal_expr
        elif self.current_token_type == TokenType.DOUBLE and self.current_token.value is not None:
            literal_string = LiteralExpr(self.current_token.value)
            self.advance()
            return literal_string
        elif self.current_token_type == TokenType.STRING and self.current_token.value is not None:
            literal_string = LiteralExpr(self.current_token.value)
            self.advance()
            return literal_string
        elif self.current_token_type == TokenType.BOOLEAN and self.current_token.value is not None:
            literal_string = LiteralExpr(self.current_token.value)
            self.advance()
            return literal_string
        elif self.current_token_type == TokenType.TRUE:
            self.advance()
            return LiteralExpr(True)
        elif self.current_token_type == TokenType.FALSE:
            self.advance()
            return LiteralExpr(False)
        elif self.current_token_type == TokenType.LEFT_BRACKET:
            self.advance()
            expr = self.expression()
            if self.current_token_type != TokenType.RIGHT_BRACKET:
                raise ParserError("No right parenthesis found.")
            else:
                self.advance()
                return GroupingExpr(expr)
        else:
            raise ParserError(f"Expected an expression. Got {self.current_token}")

    @property
    def current_token(self):
        return self.tokens[self.index].token
