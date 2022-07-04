from abc import ABC
from typing import List, Any

from classes import NativeFunctionStatement


class ModStatementFunction(NativeFunctionStatement):
    def __init__(self):
        self.name = "mod"
        self.arity = 2

    def execute(self, env):
        pass

    def call(self, arguments, env):
        first, second = _check_types(function_name=self.name, arity=self.arity, arguments=arguments, types=[int, int])
        return first % second


class PowStatementFunction(NativeFunctionStatement):
    def __init__(self):
        self.name = "pow"
        self.arity = 2

    def execute(self, env):
        pass

    def call(self, arguments, env):
        first, second = _check_types("pow", arity=self.arity, arguments=arguments, types=[int, int])
        return first ** second


def _check_types(function_name: str, arity: int, arguments: List[Any], types: List[type]) -> List[Any]:
    if len(arguments) != arity:
        raise RuntimeError(f"{function_name}: Expected {arity} arguments, got {len(arguments)}")
    for i, (arg, var_type) in enumerate(zip(arguments, types)):
        if not isinstance(arg, var_type):
            raise RuntimeError(f"{i}. argument in mod function is supposed to be an {var_type} but was type {type(arg)}")
        yield arg


class NumsStatementFunction(NativeFunctionStatement):
    def __init__(self):
        self.name = "nums"
        self.arity = 2

    def execute(self, env):
        pass

    def call(self, arguments, env):
        first, second = _check_types("nums", arity=self.arity, arguments=arguments, types=[int, int])
        return [i for i in range(first, second)]
