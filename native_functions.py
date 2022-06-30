from abc import ABC

from classes import NativeFunctionStatement


class ModStatementFunction(NativeFunctionStatement):
    def __init__(self):
        self.name = "mod"
        self.arity = 2

    def execute(self, env):
        pass

    def call(self, arguments, environment):
        if len(arguments) != self.arity:
            raise RuntimeError(f"Expected {self.arity} arguments, got {len(arguments)}")
        first, second = arguments
        if not isinstance(first, int):
            raise RuntimeError(f"First argument in mod function is supposed to be an integer but was type {type(first)}")
        if not isinstance(second, int):
            raise RuntimeError(f"First argument in mod function is supposed to be an integer but was type {type(first)}")
        if second < 0:
            raise RuntimeError(f"Second argument is supposed to be a positive number")
        return first % second
