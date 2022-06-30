from abc import ABC, abstractmethod
from lexer import TokenType, Token

from errors import ParserError

from typing import Dict, Any, Optional, List, Tuple


class Environment:
    def __init__(self, enclosing: Optional[Any] = None):
        self.environment: Dict[str, Any] = {}
        if enclosing is None:
            self.enclosing = None
        else:
            self.enclosing = enclosing

    def declare_variable(self, name, value):
        """
        Declares a new (probably undefined) variable
        :param name:
        :param value:
        :return:
        """
        if name not in self.environment:
            self.environment[name] = value
        else:
            self.environment[name] = value

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
            self.environment[name] = value

    def get_variable_value(self, name):
        if name in self.environment:
            return self.environment[name]
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
                evaluated_environment[key] = value.evaluate(self.environment)
        return evaluated_environment

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
    def __init__(self, cond: Expr, if_branch: BlockStatement, else_branch: Optional[BlockStatement], elif_branches: List[Tuple[Expr, BlockStatement]]):
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
    def __init__(self, name, parameters: List[Token], body: BlockStatement, global_env: Environment, call_function: Optional[Any] = None):
        self.name = name
        self.parameters = parameters
        self.arity = len(parameters)
        self.body = body
        self.global_environment = global_env
        self.call_function = call_function

    def execute(self, env: Environment):
        pass

    def call(self, arguments, env: Environment):
        # TODO: create the global environment

        # functions get their own environment
        environment = Environment(env)
        for arg_name, arg_value in zip(self.parameters, arguments):
            environment.declare_variable(arg_name, arg_value)
        if self.call_function is not None:
            self.call_function(env)
        self.body.execute(environment)

    def __repr__(self):
        return f"FunctionStatement(name={self.name}, parameters={self.parameters}, body={self.body}, global_env={self.global_environment})"


class NativeFunctionStatement(Statement):
    @abstractmethod
    def call(self, arguments: List[Any], environment: Environment):
        pass


class VariableStatement(Statement):
    def __init__(self, name: str, expr: Expr):
        self.name = name
        self.expr = expr

    def execute(self, env):
        value = self.expr.evaluate(env)
        env.declare_variable(self.name, value)
        #print(f"Following value was assigned to {self.name}: {value}")

    def __repr__(self):
        return f"VariableStatement(name={self.name}, expr={self.expr})"

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
            raise RuntimeError(f"Expected {len(function.num_of_arguments)} arguments, got {len(arguments)} arguments.")
        #if not isinstance(type(callee), FunctionStatement) or not isinstance(type(callee)):
        #    raise RuntimeError(f"Cant call a {type(callee)} statement.")
        return function.call(arguments=arguments, environment=env)

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
