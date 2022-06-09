from enum import Enum
import re
from typing import Pattern, AnyStr


class TokenType(Enum):
    IDEN = "IDEN",
    INT = "INT",
    DOUBLE = "DOUBLE",
    STRING = "STRING"
    ASSIGNMENT = "ASSIGNMENT",
    LINE_BREAK = "LINE_BREAK",
    PLUS = "PLUS",
    MINUS = "MINUS",
    MUL = "MUL",
    LEFT_BRACKET = "LEFT_BRACKET",
    RIGHT_BRACKET = "RIGHT_BRACKET",
    SEMICOLON = "SEMICOLON"


# max variable name length is 51
ALLOWED_VARIABLE_CHARS_REGEX: Pattern[AnyStr] = re.compile("^([A-Z]|[a-z])([A-Z]|[a-z]|[0-9]){0,50}$")


def is_allowed_identifier(identifier: str) -> bool:
    return bool(re.match(ALLOWED_VARIABLE_CHARS_REGEX, identifier))


def next_word_is(text: str, word: str):
    if text[0:len(word)] == word:
        return True
    return False


def get_full_identifier(text: str) -> str:
    identifier = ""
    for i in range(0, len(text)):
        pass


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.tokens = []
        self.index = 0
        print(code)

    def get_tokens(self):
        while self.index < len(self.code):
            self.go_forward()

    def go_forward(self):
        if self.code[self.index] == "":
            pass



