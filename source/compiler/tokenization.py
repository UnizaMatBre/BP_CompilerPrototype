import enum
from xml.dom.pulldom import CHARACTERS


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

    WHITESPACE = 9


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

    def _get_char_and_advance(self):
        prev_index = self._source_index
        self._source_index += 1

        return self._source[prev_index]


    def tokenize(self, source_code):
        self._source = source_code
        self._source_index = 0
        self._tokens = []

        while self._source_index < len(self._source):
            character = self._get_char_and_advance()

            match character:
                case ":":
                    self._add_token(TokenTypes.COLON, character)

                case ",":
                    self._add_token(TokenTypes.COMMA, character)

                case ";":
                    if self._check_next_match((")", "]", "}")):
                        bracket = self._get_char_and_advance()

                        self._add_token(TokenTypes.OBJECT_BRACKET, character + bracket)


                    else:
                        self._add_token(TokenTypes.SEMICOLON, character)

                case "(" | "[" | "{":
                    if self._check_next_match((";",)):
                        semicolon = self._get_char_and_advance()

                        self._add_token(TokenTypes.OBJECT_BRACKET, character + semicolon)

                    else:
                        self._add_token(TokenTypes.BRACKET, character)

                case '"':
                    token_string = ""

                    while self._source_index < len(self._source):
                        next_character = self._get_char_and_advance()

                        if next_character == '"':
                            break

                        token_string += next_character
                    else:
                        # ending '"' was not found
                        raise SyntaxError()

                    self._add_token(TokenTypes.STRING, token_string)

                case " " | "\t" | "\n" | "\r":
                    self._add_token(TokenTypes.WHITESPACE, character)


                case x if x in "0123456789":
                    token_number = x

                    while self._check_next_match("0123456789"):
                        token_number += self._get_char_and_advance()

                    # TODO: implement handling of decimals
                    self._add_token(
                        TokenTypes.INTEGER,
                        int(token_number)
                    )


                case _:
                    # TODO: Implement custom error
                    raise SyntaxError()

        return self._tokens
