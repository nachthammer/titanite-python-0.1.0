from typing import List, Tuple, Dict, Any, Optional

from classes import Environment, Statement, VariableStatement, PrintStatement, ExpressionStatement, BlockStatement, \
    IfStatement, WhileStatement, FunctionStatement, NativeFunctionStatement, Expr, ReturnStatement
from lexer import TokenType, Token, TokenObject
from native_functions import ModStatementFunction, PowStatementFunction
from parser import Parser, ParserError


class StatementParser:
    def __init__(self, tokens: List[TokenObject]):
        self.tokens = tokens
        self.index = 0
        self.statements: List[Statement] = []
        self.environment = Environment()
        self.add_native_functions()

    def parse(self) -> List[Statement]:
        while not self.file_finished:
            statement = self.parse_declaration()
            self.statements.append(statement)

        return self.statements

    @property
    def file_finished(self):
        return self.current_token_type == TokenType.EOF or self.index - 1 > len(self.tokens)

    def interpret(self) -> Dict[str, Any]:
        """
        The interpret function returns the variables stored in the environment, this is for testing better
        :return:
        """
        for statement in self.statements:
            statement.execute(self.environment)

        return self.environment.evaluated_store

    def get_store(self):
        return self.environment.store

    def get_evaluated_store(self):
        return self.environment.evaluated_store

    def parse_declaration(self):
        if self.current_token_is_type:
            var_type = self.current_token_type
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
            var_stmt = VariableStatement(var_type=var_type, name=variable_name, expr=expr)
            return var_stmt
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
        if self.match(TokenType.WRITE):
            return self.write_statement()
        elif self.match(TokenType.FUN):
            func_statement = self.function("function")
            self.environment.declare_variable(func_statement.name, func_statement, TokenType.FUN)
            return func_statement
        elif self.match(TokenType.STRUCT):
            class_statement = self.struct_declaration()
        elif self.match(TokenType.RETURN):
            return self.return_statement()
        elif self.match(TokenType.LEFT_CURLY_BRACKET):
            return self.block()
        elif self.match(TokenType.IF):
            # ifStmt → "if" "(" expression ")" "{" block_statement "}" ( "else" { block_statement } )? ;
            return self.if_statement()
        elif self.match(TokenType.WHILE):
            # while stmt -> "while" "(" expression ")" "{" block_statement "}"
            return self.while_statement()
        else:
            expr = self.expression()
            self.consume(TokenType.SEMICOLON, "Expected ';' after expression")
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

    def struct_declaration(self):
        struct_name_token = self.consume(TokenType.IDENTIFIER, "Expected the struct name")
        self.consume(TokenType.LEFT_BRACKET, "Expected '{' leading the struct body.")
        methods = []
        while self.current_token != TokenType.RIGHT_CURLY_BRACKET and not self.file_finished:
            methods.append(self.function("method"))
        self.consume(TokenType.LEFT_BRACKET, "Expected '}' closing the struct body.")
        return StructStatement(stuct_name=struct_name_token.value, methods=methods)

    def function(self, kind: str):
        """
        function       → IDENTIFIER "(" parameters? ")" block ;
        parameters     → IDENTIFIER ( "," IDENTIFIER )* ;
        :return:
        """
        name_token: Token = self.consume(TokenType.IDENTIFIER, f"Expected {kind} name.")
        self.consume(TokenType.LEFT_BRACKET, f"Expected '(' after {kind} name.")
        parameters: List[Tuple[TokenType, Token]] = []
        if self.current_token_type != TokenType.RIGHT_BRACKET:
            var_type = self.consume_type()
            var_name = self.consume(TokenType.IDENTIFIER, "Expected an identifier as function argument.")
            parameters.append((var_type, var_name))
            while self.current_token_type == TokenType.COMMA:
                self.index += 1
                if len(parameters) > 255:
                    raise ParserError("Cannot have more than 255 function arguments.")
                var_type = self.consume_type()
                var_name = self.consume(TokenType.IDENTIFIER, "Expected an identifier as function argument.")
                parameters.append((var_type, var_name))
        self.consume(TokenType.RIGHT_BRACKET, "Expected ')' after function arguments.")
        self.consume(TokenType.LEFT_CURLY_BRACKET, "Expected '{' before " + kind + " body.")
        function_body = self.block()
        return FunctionStatement(name=name_token.value, parameters=parameters, body=function_body, global_env=self.environment)

    def if_statement(self):
        self.consume(TokenType.LEFT_BRACKET, "Expected '(' after an if statement")
        if_condition = self.expression()
        self.consume(TokenType.RIGHT_BRACKET, "Expected ')' after an expression")
        self.consume(TokenType.LEFT_CURLY_BRACKET, "Expected a '{' leading the if body. ")
        if_branch = self.block()
        elif_branches: List[Tuple[Expr, BlockStatement]] = []
        while self.current_token_type == TokenType.ELIF:
            self.index += 1
            self.consume(TokenType.LEFT_BRACKET, "Expected '(' after an if statement")
            elif_condition: Expr = self.expression()
            self.consume(TokenType.RIGHT_BRACKET, "Expected ')' after an expression")
            self.consume(TokenType.LEFT_CURLY_BRACKET, "Expected a '{' leading the if body. ")
            elif_branch: BlockStatement = self.block()
            elif_branches.append((elif_condition, elif_branch))
        else_branch = None
        if self.current_token_type == TokenType.ELSE:
            self.index += 1
            self.consume(TokenType.LEFT_CURLY_BRACKET, "Expected a '{' leading the else body.")
            else_branch = self.block()
        return IfStatement(if_condition, if_branch, else_branch, elif_branches)

    def while_statement(self):
        self.consume(TokenType.LEFT_BRACKET, "Expected '(' after while keyword.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_BRACKET, "Expected ')' at the end of the while condition.")
        self.consume(TokenType.LEFT_CURLY_BRACKET, "Expected a '{' leading the while body")
        while_body = self.block()
        return WhileStatement(condition, while_body)

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
            current_token = self.current_token
            self.index += 1
            return current_token
        raise ParserError(error)

    def consume_type(self) -> TokenType:
        if (token := self.matches([TokenType.INT, TokenType.STRING, TokenType.DOUBLE, TokenType.BOOLEAN])) is not None:
            return token
        raise ParserError(f"Expected type. Got {self.current_token_type}")

    def match(self, token_type: TokenType):
        if self.current_token_type == token_type:
            self.index += 1
            return True
        return False

    def matches(self, token_types: List[TokenType]) -> Optional[TokenType]:
        for token_type in token_types:
            if token_type == self.current_token_type:
                self.index += 1
                return token_type
        return None

    def add_native_functions(self):
        self.environment.declare_variable("mod", ModStatementFunction(), TokenType.FUN)
        self.environment.declare_variable("pow", PowStatementFunction(), TokenType.FUN)

    def write_statement(self):
        self.consume(TokenType.LEFT_BRACKET, "Expect '(' after write statement.")
        expr = self.expression()
        self.consume(TokenType.RIGHT_BRACKET, "Expect ')' at the end of the write expression.")
        if self.current_token_type != TokenType.SEMICOLON:
            raise ParserError("Expected an ';' after a write statement")
        self.index += 1
        return PrintStatement(expr=expr)

    def return_statement(self):
        expr = None
        if self.current_token_type != TokenType.SEMICOLON:
            expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';', at the end of return statement.")
        return ReturnStatement(expr)
