from lexer import LocationInformation

from typing import Optional


class Error(Exception):
    """Base class for errors"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ParserError(Error):
    def __init__(self, message: str, position: Optional[LocationInformation] = None):
        if position is None:
            self.location_str = "Following error occurred: "
        else:
            self.location_str = f"Following error occurred at line: {position.start_line}, col: {position.start_col - position.end_col}."
        super(ParserError, self).__init__(self.location_str + message)


class LexerError(Error):
    def __init__(self, message: str, position: Optional[LocationInformation] = None):
        if position is None:
            self.location_str = "Following error occurred: "
        else:
            self.location_str = f"Following error occurred at line: {position.start_line}, col: {position.start_col - position.end_col}."
        super(LexerError, self).__init__(self.location_str + message)
