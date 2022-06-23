from abc import ABC, abstractmethod
from lexer import TokenType

from errors import ParserError

from typing import Dict, Any, Optional, List


class Environment:
    def __init__(self, enclosing: Optional[Any] = None):
        if enclosing is None:
            self.environment: Dict[str, Any] = {}
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
            return self.enclosing.get_variable_value()
        raise RuntimeError(f"Undefined variable {name}.")

    @property
    def store(self) -> Dict[str, Any]:
        return self.environment


class Statement(ABC):
    @abstractmethod
    def execute(self):
        pass


class Expr(ABC):
    @abstractmethod
    def evaluate(self, env: Environment):
        pass


class BlockStatement(Statement):
    def __init__(self, block, env):
        self.block: List[Statement] = block
        self.env = env

    def execute(self):
        environment = Environment(self.env)
        previous_env = self.env
        self.env = environment
        try:
            for statement in self.block:
                statement.execute()
        finally:
            self.env = previous_env

    def __repr__(self):
        return f"BlockStatement({self.block})"


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
        self.env.declare_variable(self.name, value)
        #print(f"Following value was assigned to {self.name}: {value}")

    def __repr__(self):
        return f"VariableStatement(name={self.name}, expr={self.expr})"


class AssignExpr(Expr):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def evaluate(self, env: Environment):
        env.assign_variable(self.name, self.value)
        return self.value


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
