from abc import ABC, abstractmethod

from lexer import TokenType, Token, TokenObject
from parser import Parser, ParserError
from classes import Environment, Statement, VariableStatement, PrintStatement, ExpressionStatement, BlockStatement

from typing import List, Optional, Tuple, Dict, Any


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

    def interpret(self) -> Dict[str, Any]:
        """
        The interpret function returns the variables stored in the environment, this is for testing better
        :return:
        """
        #print(f"statements {self.statements}")
        for statement in self.statements:
            statement.execute()
        return self.environment.store

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
        """
        :return: True if token type is one of the following: bool, string, int, double
        """
        if self.current_token.value is not None:
            return False
        current_type = self.current_token.type
        return current_type == TokenType.STRING or current_type == TokenType.INT or current_type == TokenType.DOUBLE or current_type == TokenType.BOOLEAN

    def parse_statement(self):
        if self.current_token.type == TokenType.WRITE:
            self.index += 1
            next_tokens = self.tokens[self.index:]
            parser = Parser(next_tokens)
            expr = parser.parse()
            self.index += parser.length_of_expr
            return PrintStatement(expr=expr, env=self.environment)
        elif self.current_token == TokenType.LEFT_CURLY_BRACKET:
            self.index += 1
            return BlockStatement(self.block())
        else:
            parser = Parser(self.tokens[self.index:])
            expr = parser.parse()
            self.index += parser.length_of_expr
            return ExpressionStatement(expr=expr, env=self.environment)

    def block(self):
        statements = []
        while self.current_token != TokenType.RIGHT_CURLY_BRACKET and self.index < len(self.tokens):
            statements.append(self.parse_declaration())
        if self.current_token != TokenType.RIGHT_CURLY_BRACKET:
            raise ParserError("Expected '}' after block.")
        return statements

    @property
    def current_token(self):
        return self.tokens[self.index].token
