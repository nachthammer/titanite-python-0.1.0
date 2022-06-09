from enum import Enum
import re
from typing import Pattern, AnyStr, List, Optional, Tuple, Union


class TokenType(Enum):
    IDENTIFIER = "IDENTIFIER"
    INT = "INT"
    DOUBLE = "DOUBLE"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    TRUE = "TRUE"
    FALSE = "FALSE"
    ASSIGNMENT = "ASSIGNMENT"
    FOR = "FOR"
    IN = "IN"
    LINE_BREAK = "LINE_BREAK"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    LEFT_BRACKET = "LEFT_BRACKET"
    RIGHT_BRACKET = "RIGHT_BRACKET"
    LEFT_CURLY_BRACKET = "LEFT_CURLY_BRACKET"
    RIGHT_CURLY_BRACKET = "RIGHT_CURLY_BRACKET"
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    GREATER_EQUALS = "GREATER_EQUALS"
    LESSER_EQUALS = "LESSER_EQUALS"
    GREATER = "GREATER"
    LESSER = "LESSER"
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    LIST = "LIST"
    ERROR = "ERROR"



class Token:
    def __init__(self, _type: TokenType, value: Optional[Union[str, int, float]] = None):
        self.type = _type
        self.value = value

    def __repr__(self):
        if self.value is None:
            return f"{self.type}"
        return f"{self.type} : {self.value}"

    def __eq__(self, other):
        return self.type == other.type and self.value == other.value


KEYWORDS = ["for", "in"]
SPECIAL_CHARACTERS = ["=", ">", "<", "-", "+", "*", "/", "(", ")", "{", "}", ";"]
COMPARE_OPERATORS = [">=", "<=", "==", "!="]
LOGICAL_OPERATORS = ["&&", "||", "!"]
TYPES = ["int", "double", "str", "List", "bool"]
SEPARATION_CHARACTERS: List[str] = [" ", "=", ">", "<", "-", "+", "*", "/", "(", ")", "{", "}", ";", "&", "|", "!", ","]
# max variable name length is 51
ALLOWED_VARIABLE_CHARS_REGEX: Pattern[AnyStr] = re.compile("^([A-Z]|[a-z])([A-Z]|[a-z]|[0-9]){0,50}$")
LITERAL_REGEX = re.compile("^([0-9][0-9]*)$|^([1-9][0-9]*).([0-9]*)$|^(\"[\w]\")$|false|true")
INT_REGEX = re.compile("^([0-9][0-9]*)$")
DOUBLE_REGEX = re.compile("^([1-9][0-9]*)(.)([0-9]*)$")


def is_allowed_identifier(identifier: str) -> bool:
    return bool(re.match(ALLOWED_VARIABLE_CHARS_REGEX, identifier))


def next_word_is(text: str, word: str):
    if text[0:len(word)] == word:
        return True
    return False


def get_full_identifier(text: str) -> Tuple[str, int, Optional[str]]:
    identifier = ""

    is_in_string = True if text[0] == "\"" else False # this is for when a string begins all the special characters do not disable anymore
    for i in range(0, len(text)):
        if text[i] == "\"":
            if is_in_string:
                return identifier, len(identifier)+2, None
            else:
                return identifier, len(identifier)+1, "Did not expect a \""
        elif is_in_string:
            identifier += text[i]
        # filter by not word, not by all the separation characters
        elif text[i] not in SEPARATION_CHARACTERS and not is_in_string:
            identifier += text[i]
        else:
            return identifier, len(identifier), None
    return identifier, len(identifier), None


def get_string_from_text(text: str) -> Tuple[str, Optional[str]]:
    if text[0] != "":
        return "", "Something went wrong"
    string = ""
    for i in range(1, len(text)):
        if text[i] == "\"":
            return string, None
        else:
            string += text[i]
    return string, "String never ended."


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.tokens: List[Token] = []
        self.index = 0
        self.line = -1
        self.column = -1
        print(code)

    def get_tokens(self) -> List[Token]:
        while self.index < len(self.code):
            self.go_forward()
        return self.tokens

    def increment(self, increment_value: int = 1):
        self.index += increment_value
        self.column += increment_value

    def go_forward(self):
        if self.index == len(self.code):
            # should be a } at the end
            return
        current_char = self.code[self.index]
        next_char = self.code[self.index+1] if self.index+1 < len(self.code)-1 else ""
        if current_char in [" ", "\t"]:
            self.increment()
        elif current_char == ">":
            if next_char == "=":
                self.tokens.append(Token(TokenType.GREATER_EQUALS))
                self.increment(2)
            else:
                self.tokens.append(Token(TokenType.GREATER))
                self.increment()
        elif current_char == "<":
            if next_char == "=":
                self.tokens.append(Token(TokenType.LESSER_EQUALS))
                self.increment(2)
            else:
                self.tokens.append(Token(TokenType.LESSER))
                self.increment()
        elif current_char == "=":
            if next_char == "=":
                self.tokens.append(Token(TokenType.EQUALS))
                self.increment(2)
            else:
                self.tokens.append(Token(TokenType.ASSIGNMENT))
                self.increment()
        elif current_char == "&":
            if next_char == "&":
                self.tokens.append(Token(TokenType.EQUALS))
                self.increment(2)
            else:
                self.tokens.append(Token(TokenType.ERROR, "Expected a '&' after a '&'"))
                self.increment()
        elif current_char == "|":
            if next_char == "|":
                self.tokens.append(Token(TokenType.EQUALS))
                self.increment(2)
            else:
                self.tokens.append(Token(TokenType.ERROR, "Expected a '|' after a '|'"))
                self.increment()
        elif current_char == "!":
            if next_char == "=":
                self.tokens.append(Token(TokenType.NOT_EQUALS))
                self.increment(2)
            else:
                self.tokens.append(Token(TokenType.NOT))
                self.increment()
        elif current_char == "-":
            self.tokens.append(Token(TokenType.MINUS))
            self.increment()
        elif current_char == "+":
            self.tokens.append(Token(TokenType.PLUS))
            self.increment()
        elif current_char == "*":
            self.tokens.append(Token(TokenType.MUL))
            self.increment()
        elif current_char == "/":
            self.tokens.append(Token(TokenType.DIV))
            self.increment()
        elif current_char == "(":
            self.tokens.append(Token(TokenType.LEFT_BRACKET))
            self.increment()
        elif current_char == ")":
            self.tokens.append(Token(TokenType.RIGHT_BRACKET))
            self.increment()
        elif current_char == "{":
            self.tokens.append(Token(TokenType.LEFT_CURLY_BRACKET))
            self.increment()
        elif current_char == "}":
            self.tokens.append(Token(TokenType.RIGHT_CURLY_BRACKET))
            self.increment()
        elif current_char == ";":
            self.tokens.append(Token(TokenType.SEMICOLON))
            self.increment()
        elif current_char == ",":
            self.tokens.append(Token(TokenType.COMMA))
            self.increment()
        elif current_char == "\"":
            string, error = get_string_from_text(text=self.code[self.index:])
            if error is None:
                self.increment(len(string)+2)
                self.tokens.append(Token(TokenType.STRING, string))
            else:
                self.tokens.append(Token(TokenType.ERROR, error))
                self.increment(len(string)+1)
        elif (identifier_param := get_full_identifier(text=self.code[self.index:]))[0] != "":
            full_word, length, error = identifier_param
            print(full_word)
            self.increment(length)

            if error is not None:
                self.tokens.append(Token(TokenType.ERROR, error))
            elif full_word == "int":
                self.tokens.append(Token(TokenType.INT))
            elif full_word == "double":
                self.tokens.append(Token(TokenType.DOUBLE))
            elif full_word == "str":
                self.tokens.append(Token(TokenType.STRING))
            elif full_word == "List":
                self.tokens.append(Token(TokenType.LIST))
            elif full_word == "bool":
                self.tokens.append(Token(TokenType.BOOLEAN))
            elif full_word == "for":
                self.tokens.append(Token(TokenType.FOR))
            elif full_word == "in":
                self.tokens.append(Token(TokenType.IN))
            elif re.match(LITERAL_REGEX, full_word):
                if full_word == "true":
                    self.tokens.append(Token(TokenType.TRUE))
                elif full_word == "false":
                    self.tokens.append(Token(TokenType.FALSE))
                elif re.match(INT_REGEX, full_word):
                    self.tokens.append(Token(TokenType.INT, int(full_word)))
                elif re.match(DOUBLE_REGEX, full_word):
                    self.tokens.append(Token(TokenType.DOUBLE, float(full_word)))
            elif re.match(ALLOWED_VARIABLE_CHARS_REGEX, full_word):
                self.tokens.append(Token(TokenType.IDENTIFIER, full_word))







