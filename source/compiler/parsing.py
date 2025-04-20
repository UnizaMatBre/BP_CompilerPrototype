import enum


class LiteralTypes(enum.Enum):
    INTEGER_LITERAL = 0
    DECIMAL_LITERAL = 1

    STRING_LITERAL = 2
    SYMBOL_LITERAL = 3

class LiteralNode:
    def __init__(self, lit_type, lit_value):
        self._lit_type = lit_type
        self._lit_value = lit_value



class Parser:
    def __init__(self, tokens):
        self._tokens = tokens
        self._tokens_index = 0


    def _pull_token(self):
        """Returns token and moved index forward"""
        prev_index = self._tokens_index
        self._tokens_index += 1

        return self._tokens[prev_index]


    def parse_any(self):
        pass