import enum


class TokenTypes(enum.Enum):
    INTEGER = 0
    DECIMAL = 1

    STRING = 2
    SYMBOL = 3

    BRACKET = 4
    OBJECT_BRACKET = 5

    COLON = 6
    SEMICOLON = 7
    COMMA = 8


class Tokenizer:
    def __init__(self):
        self._source = None
        self._source_index = None

        self._tokens = None

    def _add_token(self, token_type, token_value):
        self._tokens.append((token_type, token_value))

    def _check_next_match(self, desired_characters):
        next_index = self._source_index + 1

        if next_index >= len(self._source):
            return False

        next_character = self._source[next_index]

        return next_character in desired_characters

    def tokenize(self, source_code):
        self._source = source_code
        self._source_index = 0
        self._tokens = []

        while self._source_index < len(self._source):
            character = self._source[self._source_index]
            self._source_index += 1

            self._add_token(None, character)

        return self._tokens
