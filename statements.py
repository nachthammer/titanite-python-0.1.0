from abc import ABC, abstractmethod

from lexer import TokenType, Token, TokenObject
from parser import Expr, Parser, ParserError
from classes import Environment

from typing import List, Optional, Tuple, Dict, Any


class Statement(ABC):
    @abstractmethod
    def execute(self):
        pass


class PrintStatement(Statement):
    def __init__(self, expr: Expr, env: Environment):
        self.expr = expr
        self.env = env

    def execute(self):
        print(self.expr.evaluate(self.env))

    def __repr__(self):
        return f"PrintStatement({self.expr})"


class ExpressionStatement(Statement):
    def __init__(self, expr: Expr, env: Environment):
        self.expr = expr
        self.env = env

    def execute(self):
        self.expr.evaluate(self.env)

    def __repr__(self):
        return f"ExpressionStatement({self.expr})"


class VariableStatement(Statement):
    def __init__(self, name: str, expr: Expr, env: Environment):
        self.name = name
        self.expr = expr
        self.env = env

    def execute(self):
        value = self.expr.evaluate(self.env)
        print(f"Following value was assigned to {self.name}: {value}")

    def __repr__(self):
        return f"VariableStatement({self.expr})"


class StatementParser:
    def __init__(self, tokens: List[TokenObject]):
        self.tokens = tokens
        self.index = 0
        self.statements: List[Statement] = []
        self.environment = Environment()

    def parse(self) -> List[Statement]:
        while self.index < len(self.tokens):
            statement = self.parse_declaration()
            self.statements.append(statement)
        return self.statements

    def interpret(self):
        print(f"statements {self.statements}")
        for statement in self.statements:
            statement.execute()

    def parse_declaration(self):
        if self.current_token_is_type:
            # variable declaration
            self.index += 1
            if self.current_token.type != TokenType.IDENTIFIER:
                raise ParserError("Expected variable name after type.")
            if self.current_token.value is None:
                raise ParserError("Expected variable name to be not None")
            variable_name = self.current_token.value
            self.index += 1
            value_of_variable = None
            if self.current_token.type != TokenType.ASSIGNMENT:
                # we disallow uninitialized variables at first?
                raise ParserError("Expected an = after an assignment")
            self.index += 1
            # get the expr via the normal expression parser
            next_tokens = self.tokens[self.index:]
            parser = Parser(next_tokens)
            value_of_variable = parser.parse()
            self.index += parser.length_of_expr
            return VariableStatement(name=variable_name, expr=value_of_variable, env=self.environment)
        else:
            return self.parse_statement()

    @property
    def current_token_is_type(self):
        if self.current_token.value is not None:
            return False
        current_type = self.current_token.type
        return current_type == TokenType.STRING or current_type == TokenType.INT or current_type == TokenType.DOUBLE

    def parse_statement(self):
        if self.current_token.type == TokenType.WRITE:
            self.index += 1
            next_tokens = self.tokens[self.index:]
            parser = Parser(next_tokens)
            expr = parser.parse()
            self.index += parser.length_of_expr
            return PrintStatement(expr=expr, env=self.environment)
        else:
            parser = Parser(self.tokens[self.index:])
            expr = parser.parse()
            self.index += parser.length_of_expr
            return ExpressionStatement(expr=expr, env=self.environment)

    @property
    def current_token(self):
        return self.tokens[self.index].token
