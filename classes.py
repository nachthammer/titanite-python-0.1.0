from errors import ParserError

from typing import Dict, Any


class Environment:
    def __init__(self):
        self.environment: Dict[str, Any] = {}

    def add_variable(self, name, value):
        if name not in self.environment:
            self.environment[name] = value
        else:
            self.environment[name] = value

    def get_variable_value(self, name):
        if name in self.environment:
            return self.environment[name]
        raise ParserError(f"Undefined variable {name}.")

    @property
    def store(self) -> Dict[str, Any]:
        return self.environment
