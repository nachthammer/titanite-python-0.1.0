from abc import ABC, abstractmethod

from lexer import TokenType, Token, TokenObject
from parser import Parser, ParserError
from classes import Environment, Statement, VariableStatement, PrintStatement, ExpressionStatement, BlockStatement, \
    IfStatement, WhileStatement

from typing import List, Optional, Tuple, Dict, Any


class StatementParser:
    def __init__(self, tokens: List[TokenObject]):
        self.tokens = tokens
        self.index = 0
        self.statements: List[Statement] = []
        self.environment = Environment()

    def parse(self) -> List[Statement]:
        while not self.file_finished:
            statement = self.parse_declaration()
            self.statements.append(statement)

        return self.statements

    @property
    def file_finished(self):
        return self.current_token_type == TokenType.EOF or self.index - 1 > len(self.tokens)

    def interpret(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        The interpret function returns the variables stored in the environment, this is for testing better
        :return:
        """
        for statement in self.statements:
            statement.execute(self.environment)

        return self.environment.store, self.environment.evaluated_store

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
            if self.current_token.type != TokenType.ASSIGNMENT:
                # we disallow uninitialized variables at first?
                raise ParserError("Expected an = after an assignment")
            self.index += 1
            # get the expr via the normal expression parser
            expr = self.expression()
            if self.current_token_type != TokenType.SEMICOLON:
                raise ParserError("Expected ';' after variable declaration")
            self.index += 1
            return VariableStatement(name=variable_name, expr=expr)
        else:
            return self.parse_statement()

    @property
    def current_token_is_type(self) -> bool:
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
            if self.current_token_type != TokenType.SEMICOLON:
                raise ParserError("Expected an ';' after a write statement")
            self.index += 1
            return PrintStatement(expr=expr)
        elif self.current_token.type == TokenType.LEFT_CURLY_BRACKET:
            self.index += 1
            return self.block()
        elif self.current_token_type == TokenType.IF:
            """
            ifStmt → "if" "(" expression ")" "{" block_statement "}" ( "else" { block_statement } )? ;
            """
            self.index += 1
            self.consume(TokenType.LEFT_BRACKET, "Expected '(' after an if statement")
            if_condition = self.expression()
            self.consume(TokenType.RIGHT_BRACKET, "Expected ')' after an expression")
            self.consume(TokenType.LEFT_CURLY_BRACKET, "Expected a '{' leading the if branch. ")
            if_branch = self.block()
            else_branch = None
            if self.current_token_type == TokenType.ELSE:
                self.index += 1
                self.consume(TokenType.LEFT_CURLY_BRACKET, "Expected a '{' leading the else branch.")
                else_branch = self.block()
            return IfStatement(if_condition, if_branch, else_branch)
        elif self.current_token_type == TokenType.WHILE:
            self.index += 1
            self.consume(TokenType.LEFT_BRACKET, "Expected '(' after while keyword.")
            condition = self.expression()
            self.consume(TokenType.RIGHT_BRACKET, "Expected ')' at the end of the while condition.")
            self.consume(TokenType.LEFT_CURLY_BRACKET, "Expected a '{' leading the while body")
            while_body = self.block()
            return WhileStatement(condition, while_body)
        else:
            parser = Parser(self.tokens[self.index:])
            expr = parser.parse()
            self.index += parser.length_of_expr
            if self.current_token_type != TokenType.SEMICOLON:
                raise ParserError("Expected ';' after expression")
            self.index += 1
            return ExpressionStatement(expr=expr)

    def expression(self):
        next_tokens = self.tokens[self.index:]
        parser = Parser(next_tokens)
        value_of_variable = parser.parse()
        self.index += parser.length_of_expr
        return value_of_variable

    def block(self) -> BlockStatement:
        statements = []
        while self.current_token.type != TokenType.RIGHT_CURLY_BRACKET and self.index < len(self.tokens):
            statements.append(self.parse_declaration())
        self.consume(TokenType.RIGHT_CURLY_BRACKET, "Expect '}' at the end of a block.")
        return BlockStatement(statements)

    @property
    def current_token(self):
        return self.tokens[self.index].token

    @property
    def current_token_type(self):
        return self.tokens[self.index].token.type

    @property
    def current_token_value(self):
        return self.tokens[self.index].token.value

    def consume(self, token_type: TokenType, error: str):
        if self.current_token_type == token_type:
            self.index += 1
            return True
        raise ParserError(error)
