import sys

from evaluator import Evaluator
from lexer import Lexer
from parser import Parser
from statements import StatementParser
from classes import Environment


def evaluate_string(string: str):
    tokens = get_tokens(string)
    parser = Parser(tokens)
    parsed_tree = parser.parse()
    evaluator = Evaluator(parsed_tree)
    environment = Environment()
    return evaluator.evaluate(environment)


def get_tokens(code: str):
    lexer = Lexer(code)
    lexer.run_lexer()
    return lexer.get_token_objects()


def execute(string: str):
    tokens = get_tokens(string)

    #print(tokens)
    statement_parser = StatementParser(tokens)
    statement_parser.parse()
    statement_parser.interpret()
    return statement_parser.get_store(), statement_parser.get_clean_store()


if __name__ == "__main__":
    args = sys.argv
    file_name = "program.ti"
    try:
        file_name = args[1]
    except IndexError:
        print(f"You need to give a file name as the first argument")
        exit(-1)

    with open(file_name) as f:
        program_string = f.read()

    store, ev_store = execute(program_string)
    print(ev_store)




