import enum
from xml.dom.pulldom import CHARACTERS


class TokenTypes(enum.Enum):
    INTEGER = 0
    DECIMAL = 1

    STRING = 2
    SYMBOL = 3

    BRACKET_OPEN = 4
    BRACKET_CLOSE = 5

    OBJECT_BRACKET_OPEN = 6
    OBJECT_BRACKET_CLOSE = 7

    COLON = 8
    SEMICOLON = 9
    COMMA = 10

    WHITESPACE = 11

    EOF = 12


OPERATOR_CHARACTERS = "".join(("+", "-", "*", "\\", "/", "%", "=", "!", "<", ">", "|", "&"))


ASCII_CHARACTERS = "".join(
    [chr(char) for char in range(ord("a"), ord("z"))]
) + "".join(
    [chr(char) for char in range(ord("A"), ord("Z"))]
)

ASCII_DIGITS = "0123456789"

KEYWORD_CHARACTERS = ASCII_CHARACTERS + ASCII_DIGITS + "_"


class TokenizerError(Exception):
    pass


class Tokenizer:
    def __init__(self):
        self._source = None
        self._source_index = None

        self._tokens = None

    def _add_token(self, token_type, token_value):
        self._tokens.append((
            token_type,
            (0, 0), # TODO: Implement actual source position counting
            token_value

        ))

    def _check_next_match(self, predicate):
        if self._source_index >= len(self._source):
            return False

        return predicate(self._source[self._source_index])

    def _get_char_and_advance(self):
        prev_index = self._source_index
        self._source_index += 1

        return self._source[prev_index]

    def _raise_tokenizer_error(self, message):
        # calculate location
        line = line_pos = 0

        for local_index in range(self._source_index - 1):
            char = self._source[local_index]

            if char == "\n":
                line_pos = 0
                line += 1
                return

            line_pos += 1

        raise TokenizerError((line, line_pos), message)

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
                    if self._check_next_match(lambda char: char in (")", "]", "}")):
                        bracket = self._get_char_and_advance()

                        self._add_token(TokenTypes.OBJECT_BRACKET_CLOSE, character + bracket)


                    else:
                        self._add_token(TokenTypes.SEMICOLON, character)

                case "(" | "[" | "{":
                    if self._check_next_match(lambda char: char == ";"):
                        semicolon = self._get_char_and_advance()

                        self._add_token(TokenTypes.OBJECT_BRACKET_OPEN, character + semicolon)

                    else:
                        self._add_token(TokenTypes.BRACKET_OPEN, character)

                case ")" | "]" | "}":
                    self._add_token(TokenTypes.BRACKET_CLOSE, character)

                case '"':
                    token_string = ""

                    while self._source_index < len(self._source):
                        next_character = self._get_char_and_advance()

                        if next_character == '"':
                            break

                        token_string += next_character
                    else:
                        # ending '"' was not found
                        self._raise_tokenizer_error(r'String enclosing quotation marks not found.')

                    self._add_token(TokenTypes.STRING, token_string)

                case " " | "\t" | "\n" | "\r":
                    self._add_token(TokenTypes.WHITESPACE, character)


                case x if x in "0123456789":
                    token_number = x

                    while self._check_next_match(lambda char: char in "0123456789"):
                        token_number += self._get_char_and_advance()

                    # TODO: implement handling of decimals
                    self._add_token(
                        TokenTypes.INTEGER,
                        int(token_number)
                    )

                # handle operator symbols
                case x if x in OPERATOR_CHARACTERS:
                    operator_text = x

                    while self._check_next_match(lambda char: char in OPERATOR_CHARACTERS):
                        operator_text += self._get_char_and_advance()

                    self._add_token(
                        TokenTypes.SYMBOL,
                        operator_text
                    )

                # handle keyword symbols
                case x if x == "_" or x in ASCII_CHARACTERS:
                    keyword_text = x

                    while self._check_next_match(lambda char: char in KEYWORD_CHARACTERS):
                        keyword_text += self._get_char_and_advance()

                    self._add_token(
                        TokenTypes.SYMBOL,
                        keyword_text
                    )



                case unknown_char:
                    self._raise_tokenizer_error("Unexpected character '{}'".format(unknown_char))


        self._add_token(TokenTypes.EOF, "")

        return self._tokens

