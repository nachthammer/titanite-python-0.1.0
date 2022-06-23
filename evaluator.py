from errors import ParserError
from classes import Environment, Expr


class Evaluator:
    def __init__(self, expression: Expr):
        self.expression = expression

    def evaluate(self, env: Environment):
        if self.expression is None:
            raise ParserError("Could not parse the expression")
        return self.expression.evaluate(env=env)
