from enum import Enum
import re
from typing import Pattern, AnyStr, List, Optional, Tuple, Union


class TokenType(Enum):
    IDENTIFIER = "IDENTIFIER"
    # types
    INT = "INT"
    DOUBLE = "DOUBLE"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    LIST = "LIST"
    # literals
    TRUE = "TRUE"
    FALSE = "FALSE"
    ASSIGNMENT = "ASSIGNMENT"
    # keywords (loops, conditions)
    FOR = "FOR"
    IN = "IN"
    WHILE = "WHILE"
    IF = "IF"
    ELIF = "ELIF"
    ELSE = "ELSE"
    MODULO = "MODULO"
    # I/O
    WRITE = "WRITE"
    READ = "READ"
    # arithmetic operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    # separators
    LEFT_BRACKET = "LEFT_BRACKET"
    RIGHT_BRACKET = "RIGHT_BRACKET"
    LEFT_CURLY_BRACKET = "LEFT_CURLY_BRACKET"
    RIGHT_CURLY_BRACKET = "RIGHT_CURLY_BRACKET"
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    LINE_BREAK = "LINE_BREAK"
    # arithmetic comparators (only possible on number types)
    GREATER_EQUALS = "GREATER_EQUALS"
    LESSER_EQUALS = "LESSER_EQUALS"
    GREATER = "GREATER"
    LESSER = "LESSER"
    # comparators possible on other objects
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    # logical operators
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    # error token
    ERROR = "ERROR"


class Token:
    def __init__(self, _type: TokenType, value: Optional[Union[str, int, float]] = None):
        self.type = _type
        self.value = value

    def __repr__(self):
        if self.value is None:
            return f"Token({self.type})"
        elif isinstance(self.value, str):
            return f"Token({self.type}, \"{self.value}\")"
        return f"Token({self.type}, {self.value})"

    def __eq__(self, other):
        return self.type == other.type and self.value == other.value


class LocationInformation:
    def __init__(self, start_line: int, end_line: int, start_col: int, end_col: int):
        self.start_line = start_line
        self.end_line = end_line
        self.start_col = start_col
        self.end_col = end_col

    def __repr__(self):
        return f"LocationInformation(start_line={self.start_line}, end_line={self.end_line}, start_col={self.start_col}, end_col={self.end_col})"

    def __eq__(self, other):
        return self.start_line == other.start_line and self.end_line == other.end_line and \
               self.start_col == other.start_col and self.end_col == other.end_col


class TokenObject:
    def __init__(self, token: Token, location_info: LocationInformation):
        self.token = token
        self.location_info = location_info

    def __repr__(self):
        return f"TokenObject({self.token}, {self.location_info})"

    def __eq__(self, other):
        return self.token == other.token and self.location_info == other.location_info

    def get_token(self):
        return self.token


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


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.tokens: List[TokenObject] = []
        self.index = 0
        self.line = 1
        self.column = 1

    def run_lexer(self):
        while self.index < len(self.code):
            self.go_forward()

    def get_token_objects(self) -> List[TokenObject]:
        return self.tokens

    def get_tokens(self) -> List[Token]:
        return [token_obj.get_token() for token_obj in self.tokens]

    def advance(self, increment_value: int = 1, column_length: Optional[int] = None):
        self.index += increment_value
        if column_length is None:
            self.column += increment_value
        else:
            self.column = column_length

    def get_current_location(self) -> Tuple[int, int]:
        line_number = len(self.code[0:self.index].split("\n"))
        col_number = len(self.code[0:self.index].split("\n")[-1])
        return line_number, col_number

    def go_forward(self):
        if self.index == len(self.code):
            # should be a } at the end
            return
        current_char = self.code[self.index]
        next_char = self.code[self.index + 1] if self.index + 1 < len(self.code) - 1 else ""
        start_line, start_col = self.get_current_location()
        skip_length = 1
        token = None
        if current_char in [" ", "\t"]:
            self.column += 1
        elif current_char == "\n":
            self.line += 1
            self.column = 1
        elif current_char == ">":
            if next_char == "=":
                token = Token(TokenType.GREATER_EQUALS)
                skip_length = 2
            else:
                token = Token(TokenType.GREATER)
        elif current_char == "<":
            if next_char == "=":
                token = Token(TokenType.LESSER_EQUALS)
                skip_length = 2
            else:
                token = Token(TokenType.LESSER)
        elif current_char == "=":
            if next_char == "=":
                token = Token(TokenType.EQUALS)
                skip_length = 2
            else:
                token = Token(TokenType.ASSIGNMENT)
        elif current_char == "&":
            if next_char == "&":
                token = Token(TokenType.EQUALS)
                skip_length = 2
            else:
                token = Token(TokenType.ERROR, "Expected a '&' after a '&'")
        elif current_char == "|":
            if next_char == "|":
                token = Token(TokenType.EQUALS)
                skip_length = 2
            else:
                token = Token(TokenType.ERROR, "Expected a '|' after a '|'")
        elif current_char == "!":
            if next_char == "=":
                token = Token(TokenType.NOT_EQUALS)
                skip_length = 2
            else:
                token = Token(TokenType.NOT)
        elif current_char == "-":
            token = Token(TokenType.MINUS)
        elif current_char == "+":
            token = Token(TokenType.PLUS)
        elif current_char == "*":
            token = Token(TokenType.MUL)
        elif current_char == "/":
            token = Token(TokenType.DIV)
        elif current_char == "(":
            token = Token(TokenType.LEFT_BRACKET)
        elif current_char == ")":
            token = Token(TokenType.RIGHT_BRACKET)
        elif current_char == "{":
            token = Token(TokenType.LEFT_CURLY_BRACKET)
        elif current_char == "}":
            token = Token(TokenType.RIGHT_CURLY_BRACKET)
        elif current_char == ";":
            token = Token(TokenType.SEMICOLON)
        elif current_char == ",":
            token = Token(TokenType.COMMA)
        elif current_char == "\"":
            string, error = self.get_string_from_text(text=self.code[self.index:])
            column_length = self.column
            if error is None:
                skip_length = len(string) + 2
                token = Token(TokenType.STRING, string)
            else:
                token = Token(TokenType.ERROR, error)
                skip_length = len(string) + 1
        elif (identifier_param := self.get_full_identifier(text=self.code[self.index:]))[0] != "":
            full_word, length, error = identifier_param
            skip_length = length
            column_length = self.column
            if error is not None:
                token = Token(TokenType.ERROR, error)
            elif full_word == "int":
                token = Token(TokenType.INT)
            elif full_word == "double":
                token = Token(TokenType.DOUBLE)
            elif full_word == "str":
                token = Token(TokenType.STRING)
            elif full_word == "List":
                token = Token(TokenType.LIST)
            elif full_word == "bool":
                token = Token(TokenType.BOOLEAN)
            elif full_word == "for":
                token = Token(TokenType.FOR)
            elif full_word == "in":
                token = Token(TokenType.IN)
            elif full_word == "while":
                token = Token(TokenType.WHILE)
            elif full_word == "if":
                token = Token(TokenType.IF)
            elif full_word == "elif":
                token = Token(TokenType.ELIF)
            elif full_word == "else":
                token = Token(TokenType.ELSE)
            elif re.match(LITERAL_REGEX, full_word):
                if full_word == "true":
                    token = Token(TokenType.TRUE)
                elif full_word == "false":
                    token = Token(TokenType.FALSE)
                elif re.match(INT_REGEX, full_word):
                    token = Token(TokenType.INT, int(full_word))
                elif re.match(DOUBLE_REGEX, full_word):
                    token = Token(TokenType.DOUBLE, float(full_word))
            elif re.match(ALLOWED_VARIABLE_CHARS_REGEX, full_word):
                token = Token(TokenType.IDENTIFIER, full_word)

        self.advance(skip_length)
        end_line, end_col = self.get_current_location()
        location_info = LocationInformation(
            start_line=start_line,
            end_line=end_line,
            start_col=start_col,
            end_col=end_col
        )
        if token is not None:
            self.tokens.append(TokenObject(token=token, location_info=location_info))

    def get_string_from_text(self, text: str) -> Tuple[str, Optional[str]]:
        """
        This function gets called when a " character gets spotted
        :param text:
        :return:
        """
        if text[0] != "\"":
            return "", "Something went horribly wrong when parsing a string."
        string = ""
        for i in range(1, len(text)):
            if text[i] == "\"":
                return string, None
            else:
                string += text[i]
                if text[i] == "\n":
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
        return string, "String never ended."

    def get_full_identifier(self, text: str) -> Tuple[str, int, Optional[str]]:
        """
        This function gets the next full viable word in the text
        :param text: The trimmed down text
        :return: the identifier, length of the identifier, optional error message
        """
        identifier = ""
        word_regex = re.compile("([A-Z]|[a-z]|[0-9])")
        digit_regex = re.compile("([0-9])")
        # this means that we look for a number
        if re.match(digit_regex, text[0]):
            after_point = False
            for i in range(len(text)):
                if re.match(digit_regex, text[i]):
                    identifier += text[i]
                elif text[i] == "." and after_point:
                    return identifier, len(identifier)+1, "Expected only one . for a number."
                elif text[i] == ".":
                    after_point = True
                    identifier += "."
                else:
                    if text[i-1] == ".":
                        return identifier, len(identifier)+1, f"No lonely point allowed for double. Write {identifier}0 instead"
                    return identifier, len(identifier), None
            return identifier, len(identifier), None
        else:
            for i in range(0, len(text)):
                if re.match(word_regex, text[i]):
                    identifier += text[i]
                else:
                    break

            return identifier, len(identifier), None
