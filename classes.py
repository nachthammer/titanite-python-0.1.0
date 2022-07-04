from abc import ABC, abstractmethod
from enum import Enum

from lexer import TokenType, Token

from errors import ParserError, ReturnError

from typing import Dict, Any, Optional, List, Tuple

native_functions = ["mod", "pow"]

class StaticType(Enum):
    INT = "INT"
    STRING = "STRING"
    DOUBLE = "DOUBLE"
    BOOLEAN = "BOOLEAN"
    LIST = "LIST"
    FUNCTION = "FUNCTION"
    NATIVE_FUNCTION = "NATIVE_FUNCTION"
    ANY = "ANY"
    STRUCT = "STRUCT"

    def __repr__(self):
        return f"{self.value}"


def convert_token_type_to_static_type(token_type: TokenType):
    if token_type == TokenType.INT:
        return StaticType.INT
    elif token_type == TokenType.DOUBLE:
        return StaticType.DOUBLE
    elif token_type == TokenType.STRING:
        return StaticType.STRING
    elif token_type == TokenType.BOOLEAN:
        return StaticType.BOOLEAN
    elif token_type == TokenType.LIST:
        return StaticType.LIST
    elif token_type == TokenType.FUN:
        return StaticType.FUNCTION
    elif token_type == TokenType.STRUCT:
        return StaticType.STRUCT

    else:
        raise RuntimeError(f"Expected a valid token type to convert to static type. Got {token_type}")


def convert_value_to_static_type(value: Any):
    if isinstance(value, int):
        return StaticType.INT
    elif isinstance(value, float):
        return StaticType.DOUBLE
    elif isinstance(value, str):
        return StaticType.STRING
    elif isinstance(value, bool):
        return StaticType.BOOLEAN
    elif isinstance(value, list):
        return StaticType.LIST
    elif isinstance(value, FunctionStatement):
        return StaticType.FUNCTION
    else:
        raise RuntimeError(f"Could not infer the type of {value}")


class Environment:
    def __init__(self, enclosing: Optional[Any] = None):
        """
        Example env:
        {
            "a": (
                type: StaticType.INT
                value: 3
            ),
            "string_example": (
                type: StaticType.STRING
                value: "Hello World!"
            )
        }
        :param enclosing:
        """
        self.environment: Dict[str, Tuple[StaticType, Any]] = {}
        if enclosing is None:
            self.enclosing = None
        else:
            self.enclosing = enclosing

    def declare_variable(self, name, value: Any, var_type: Optional[TokenType], _static_type: Optional[StaticType] = None):
        """
        Declares a new (probably undefined) variable

        :param name:
        :param value:
        :param var_type:
        :param _static_type:
        :return:
        """
        # we use this try catch statement to know if the variable was already declared.
        variable_already_use = True
        try:
            var_type = self.get_variable_value(name)
        except RuntimeError:
            variable_already_use = False
        if variable_already_use:
            raise RuntimeError(f"Variable {name} was already declared. Cannot redeclare the variable.")

        expected_static_type = StaticType.ANY
        if _static_type is not None:
            expected_static_type = _static_type
        elif var_type is not None:
            expected_static_type = convert_token_type_to_static_type(var_type)

        actual_value_type = StaticType.ANY
        if hasattr(value, "static_type"):
            actual_value_type = StaticType.FUNCTION
        else:
            actual_value_type = convert_value_to_static_type(value)
        value_tuple = (expected_static_type, value)

        if expected_static_type != actual_value_type:
            print("raise error", name, value, var_type, _static_type)
            raise RuntimeError(f"Cannot assign {actual_value_type} ({value}) to type {expected_static_type} (name: {name})")
        if name not in self.environment:
            self.environment[name] = value_tuple
        else:
            raise ParserError(f"Cannot redefine already defined variable '{name}'")

    def assign_variable(self, name, value):
        """
        Assigns a variable, the variable has to be defined before.

        :param name: the name of the variable
        :param value: the value of the variable
        :return:
        :raises: ParserError if the variable was not defined yet
        """
        if name not in self.environment and self.enclosing is None:
            raise RuntimeError(f"Undefined variable {name}")
        elif name not in self.environment and self.enclosing is not None:
            self.enclosing.assign_variable(name, value)
        else:
            # check type
            env_var_type = self.environment[name][0]
            value_type = convert_value_to_static_type(value)
            if env_var_type != value_type:
                raise RuntimeError(f"Incompatible type of {name} (of type {env_var_type}) and {value} (of type {value_type})")
            self.environment[name] = (env_var_type, value)

    def get_variable_value(self, name):
        """
        Gets a variable with the specified name

        :param name:
        :return: returns the Expression object
        :raises: RuntimeError if there is no variable with this name
        """
        if name in self.environment:
            return self.environment[name][1]
        if self.enclosing is not None:
            return self.enclosing.get_variable_value(name)
        raise RuntimeError(f"Undefined variable {name}.")

    @property
    def store(self) -> Dict[str, Any]:
        return self.environment

    @property
    def evaluated_store(self) -> Dict[str, Any]:
        evaluated_environment = self.environment
        for key, value in evaluated_environment.items():
            if issubclass(type(value), Expr):
                evaluated_environment[key] = value[1].evaluate(self.environment)
        return evaluated_environment

    @property
    def clean_store(self) -> Dict[str, Any]:
        evaluated_environment = self.environment
        for key, value in evaluated_environment.items():
            if issubclass(type(value), Expr):
                evaluated_environment[key] = value[1].evaluate(self.environment)

        clean_env = {}
        for key, value in evaluated_environment.items():
            if key not in native_functions:
                clean_env[key] = evaluated_environment[key]
        return clean_env

    def __repr__(self):
        return f"Environment(environment={self.environment}, enclosing={self.enclosing})"


class Statement(ABC):
    @abstractmethod
    def execute(self, env: Environment):
        pass


class Expr(ABC):
    @abstractmethod
    def evaluate(self, env: Environment):
        pass


##########################################################################
# Statements
##########################################################################


class BlockStatement(Statement):
    def __init__(self, block):
        self.block: List[Statement] = block

    def execute(self, env):
        environment = Environment(env)
        previous_env = env
        env = environment
        try:
            for statement in self.block:
                statement.execute(env)
        finally:
            env = previous_env

    def __repr__(self):
        return f"BlockStatement(block={self.block})"


class IfStatement(Statement):
    def __init__(self, cond: Expr, if_branch: BlockStatement, else_branch: Optional[BlockStatement],
                 elif_branches: List[Tuple[Expr, BlockStatement]]):
        self.cond = cond
        self.if_branch = if_branch
        self.else_branch = else_branch
        self.elif_branches = elif_branches

    def execute(self, env: Environment):
        condition = self.cond.evaluate(env)
        if condition:
            self.if_branch.execute(env)
            return
        for elif_branch_cond, elif_branch_body in self.elif_branches:
            if elif_branch_cond.evaluate(env):
                elif_branch_body.execute(env)
                return
        if not condition and self.else_branch is not None:
            self.else_branch.execute(env)
            return
        return

    def __repr__(self):
        return f"IfStatement({self.cond}, {self.if_branch}, {self.else_branch})"


class WhileStatement(Statement):
    def __init__(self, cond: Expr, while_body: BlockStatement):
        self.cond = cond
        self.while_body = while_body

    def execute(self, env):
        condition = get_bool(self.cond, env)
        while condition:
            self.while_body.execute(env)
            condition = get_bool(self.cond, env)

    def __repr__(self):
        return f"WhileStatement(cond={self.cond}, while_body={self.while_body})"


def get_bool(expr: Expr, env):
    value = expr.evaluate(env)
    if isinstance(value, bool):
        return value
    raise RuntimeError("Expected a boolean.")


class PrintStatement(Statement):
    def __init__(self, expr: Expr):
        self.expr = expr

    def execute(self, env: Environment):
        print(self.expr.evaluate(env))

    def __repr__(self):
        return f"PrintStatement(expr={self.expr})"


class ExpressionStatement(Statement):
    def __init__(self, expr: Expr):
        self.expr = expr

    def execute(self, env):
        self.expr.evaluate(env)

    def __repr__(self):
        return f"ExpressionStatement(expr={self.expr})"


class FunctionStatement(Statement):
    def __init__(self, name, parameters: List[Tuple[TokenType, Token]], body: BlockStatement, global_env: Environment):
        self.name = name
        self.parameters = parameters
        self.arity = len(parameters)
        self.body = body
        self.global_environment = global_env

    def execute(self, env: Environment):
        pass

    def call(self, arguments, env: Environment):
        # TODO: create the global environment
        # functions get their own environment
        environment = Environment(env)
        for (arg_type, arg_token_name), arg_value in zip(self.parameters, arguments):
            check_correct_type(arg_type, arg_value)
            environment.declare_variable(arg_token_name.value, arg_value, arg_type)
        try:
            self.body.execute(environment)
        except ReturnError as r:
            return r.return_value
        return None

    @staticmethod
    @property
    def static_type():
        return StaticType.FUNCTION

    def __repr__(self):
        return f"FunctionStatement(name={self.name}, parameters={self.parameters}, body={self.body}, global_env={self.global_environment})"


class StructStatement(Statement):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def execute(self, env: Environment):
        env.declare_variable(self.name, None, None, StaticType.STRUCT)
        _class = ClassExpr(name)


def check_correct_type(token_type: TokenType, value: Any):
    """
    Checks if the value has the specified type. The value should be an evaluated expression
    :param token_type:
    :param value:
    :return:
    """
    if token_type == TokenType.INT:
        if not isinstance(value, int):
            raise RuntimeError(f"Expected int. Got {type(value)}")
    elif token_type == TokenType.STRING:
        if not isinstance(value, str):
            raise RuntimeError(f"Expected str. Got {type(value)}")
    elif token_type == TokenType.DOUBLE:
        if not isinstance(value, float):
            raise RuntimeError(f"Expected float. Got {type(value)}")
    elif token_type == TokenType.BOOLEAN:
        if not isinstance(value, bool):
            raise RuntimeError(f"Expected bool. Got {type(value)}")
    else:
        raise RuntimeError(f"Expected a type for the token. Got {token_type}")


class ReturnStatement(Statement):
    def __init__(self, expr: Expr):
        self.expr = expr

    def execute(self, env):
        value = None
        if self.expr is not None:
            value = self.expr.evaluate(env)
        raise ReturnError(value)


class NativeFunctionStatement(Statement):
    @abstractmethod
    def call(self, arguments: List[Any], environment: Environment):
        pass

    @staticmethod
    @property
    def static_type():
        return StaticType.NATIVE_FUNCTION


class VariableStatement(Statement):
    def __init__(self, var_type: TokenType, name: str, expr: Expr):
        self.var_type = var_type
        self.name = name
        self.expr = expr

    def execute(self, env):
        value = self.expr.evaluate(env)
        env.declare_variable(self.name, value, self.var_type)
        # print(f"Following value was assigned to {self.name}: {value}")

    def __repr__(self):
        return f"VariableStatement(var_type={self.var_type}, name={self.name}, expr={self.expr})"


##########################################################################
# Expressions
##########################################################################


class AssignExpr(Expr):
    def __init__(self, name, value: Expr):
        self.name = name
        self.value = value

    def evaluate(self, env: Environment):
        env.assign_variable(self.name, self.value.evaluate(env))
        return self.value

    def __repr__(self):
        return f"AssignExpr(name={self.name}, value={self.value})"


class CallExpr(Expr):
    def __init__(self, callee_name, paranthesis, arguments: List[Expr]):
        self.callee_name = callee_name
        self.paranthesis = paranthesis
        self.arguments = arguments

    def evaluate(self, env: Environment):
        callee = self.callee_name.evaluate(env)
        arguments = [arguments.evaluate(env) for arguments in self.arguments]
        function = callee
        if len(arguments) != function.arity:
            raise RuntimeError(f"Expected {function.arity} arguments, got {len(arguments)} arguments.")
        # if not isinstance(type(callee), FunctionStatement) or not isinstance(type(callee)):
        #    raise RuntimeError(f"Cant call a {type(callee)} statement.")
        return function.call(arguments=arguments, env=env)

    def __repr__(self):
        return f"CallExpr(callee_name={self.callee_name}, paranthesis={self.paranthesis}, arguments={self.arguments})"


class LogicExpr(Expr):
    def __init__(self, expr: Expr, logic_operator: TokenType, right: Expr):
        self.expr = expr
        self.logic_operator = logic_operator
        self.right = right

    def __repr__(self):
        return f"BinaryExpr(expr={self.expr}, operator={self.logic_operator}, right={self.right})"

    def __eq__(self, other):
        if not isinstance(other, LogicExpr):
            return False
        return self.expr == other.expr and self.logic_operator == other.logic_operator and self.right == other.right

    def evaluate(self, env: Environment):
        left = self.expr.evaluate(env)
        if not isinstance(left, bool):
            raise RuntimeError("Expected a boolean type for logic operators.")
        if self.logic_operator == TokenType.AND:
            if not left:
                return False
            return self.right.evaluate(env)
        elif self.logic_operator == TokenType.OR:
            if left:
                return True
            return self.right.evaluate(env)
        else:
            raise ParserError("Expected an logic operator in a logic operation.")


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
