from lexer import Token, TokenType, TokenObject
from errors import ParserError
from typing import List
from classes import VariableStatement, AssignExpr, BinaryExpr, UnaryExpr, IdentifierExpr, LiteralExpr, GroupingExpr, \
    LogicExpr, CallExpr, ArrayIndexExpr, Expr, ArrayExpr


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
        return self.tokens[self.index - 1 if self.index - 1 > -1 else self.index].token

    @property
    def previous_token_type(self):
        return self.tokens[self.index - 1 if self.index - 1 > -1 else self.index].token.type

    def expression(self):
        expr = self.assignment()
        return expr

    def assignment(self):
        expr = self.logic_or()

        if self.current_token_type == TokenType.ASSIGNMENT:
            self.advance()
            value = self.assignment()
            if isinstance(expr, VariableStatement):
                name = expr.name
                return AssignExpr(name, value)
            elif isinstance(expr, IdentifierExpr):
                name = expr.identifier
                return AssignExpr(name, value)
            raise ParserError(f"Invalid assignment target. Was an {type(expr)}")
        return expr

    def logic_or(self):
        expr = self.logic_and()
        while self.current_token_type == TokenType.OR:
            self.advance()
            right = self.logic_and()
            expr = LogicExpr(expr, TokenType.OR, right)
        return expr

    def logic_and(self):
        expr = self.equality()
        while self.current_token_type == TokenType.AND:
            self.advance()
            right = self.equality()
            expr = LogicExpr(expr, TokenType.AND, right)
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
        while self.match_types([TokenType.GREATER, TokenType.GREATER_EQUALS, TokenType.LESSER_EQUALS, TokenType.LESSER]):
            operator = self.previous_token_type
            right = self.term()
            comparison = BinaryExpr(comparison, operator, right)
        return comparison

    def term(self):
        """
        term           → factor ( ( "-" | "+" ) factor )*
        :return:
        """
        term = self.factor()

        while self.match_types([TokenType.MINUS, TokenType.PLUS]):
            operator = self.previous_token_type
            right = self.factor()
            term = BinaryExpr(term, operator, right)

        return term

    def factor(self):
        """
        factor         → unary ( ( "/" | "*" ) unary )*
        :return:
        """
        factor = self.unary()

        while self.match_types([TokenType.DIV, TokenType.MUL]):
            operator = self.previous_token_type
            right = self.unary()
            factor = BinaryExpr(factor, operator, right)

        return factor

    def unary(self):
        """
        unary          → ( "!" | "-" ) unary | primary
        :return:
        """
        while self.match_types([TokenType.NOT, TokenType.MINUS]):
            operator = self.previous_token_type
            right = self.primary()
            return UnaryExpr(operator, right)

        return self.call()

    def call(self):
        """
        call           → primary ( "(" arguments? ")" )* ;
        :return:
        """
        expr = self.primary()
        while True:
            if self.current_token_type == TokenType.LEFT_BRACKET:
                self.advance()
                expr = self.finish_call(expr)
            else:
                break

        return expr

    def finish_call(self, call_name):
        arguments = []
        if self.current_token_type != TokenType.RIGHT_BRACKET:
            arguments.append(self.expression())
            while self.current_token_type == TokenType.COMMA:
                self.advance()
                if len(arguments) > 255:
                    raise ParserError("Cannot have more than 255 arguments.")
                arguments.append(self.expression())
        # now we have all arguments
        self.consume(TokenType.RIGHT_BRACKET, "Expected ')' for closing the arguments section.")
        return CallExpr(call_name, TokenType.RIGHT_BRACKET, arguments)

    def primary(self):
        """
        primary→int | string | true | false | "(" expression ")" | identifier | ( identifier"[" expression"]")
                "[" "]" | "[" ( expression "," )* expression "]";
        :return:
        """
        if self.current_token_type == TokenType.IDENTIFIER:
            identifier = self.current_token.value
            literal_expr = IdentifierExpr(self.current_token.value)
            self.advance()
            if not self.match_types([TokenType.LEFT_CORNERED_BRACKET]):
                return literal_expr
            # we spotted an '[' so we expect an index here (it should be an int)
            index_expr = self.expression()
            self.consume(TokenType.RIGHT_CORNERED_BRACKET, "Expected ']' at the end of the index expression.")
            return ArrayIndexExpr(identifier=identifier, index_expr=index_expr)
        elif self.match_types([TokenType.LEFT_CORNERED_BRACKET]):
            if self.match_types([TokenType.RIGHT_CORNERED_BRACKET]):
                return ArrayExpr(expressions=[])
            array_expr: List[Expr] = [self.expression()]
            while self.match_types([TokenType.COMMA]):
                array_expr.append(self.expression())
            self.consume(TokenType.RIGHT_CORNERED_BRACKET, "Expected ']' as the ending of the list.")
            return ArrayExpr(expressions=array_expr)
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

    def arguments(self):
        """
        arguments      → expression ( "," expression )* ;
        :return:
        """
        expr = [self.expression()]
        while self.current_token_type == TokenType.COMMA:
            self.advance()
            expr.append(self.expression())

        return expr

    def consume(self, token_type: TokenType, error: str):
        if self.current_token_type == token_type:
            self.advance()
            return True
        raise ParserError(error)

    @property
    def current_token(self):
        return self.tokens[self.index].token

    def match_types(self, token_types: List[TokenType]) -> bool:
        """
        Returns true if the current token is one of token in the params
        :param token_types: the to be compared token types
        :return: True if the current token type is in the list, False otherwise
        """
        for token_type in token_types:
            if token_type == self.tokens[self.index].token.type:
                self.advance()
                return True
        return False
