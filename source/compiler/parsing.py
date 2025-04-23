import enum

from source.compiler.ast_nodes import CodeBox
from source.compiler.tokenization import TokenTypes, Tokenizer


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

    def _consume_whitespaces(self):
        """Jumps over all whitespace tokens in token list"""

        while self._peek_token()[0] == TokenTypes.WHITESPACE:
            self._pull_token()

    def _check_token_type(self, wanted_token_types):
        """Checks if current token has type we want"""
        token_type, _, _ = self._peek_token()

        return token_type in wanted_token_types


    def _check_token_value(self, wanted_token_values):
        """Checks if current token has value we want"""
        _, _, token_value = self._peek_token()

        return token_value in wanted_token_values

    def _peek_token(self):
        return self._tokens[self._tokens_index]

    def _pull_token(self):
        """Returns token and moved index forward"""
        prev_index = self._tokens_index
        self._tokens_index += 1

        return self._tokens[prev_index]


    def parse_root_code(self):
        expression_list = []

        token_type, _, _ = self._peek_token()

        while token_type != TokenTypes.EOF:
            expression_list.append(
                self.parse_expression()
            )

            token_type, _, _ = self._peek_token()

        return CodeBox(expression_list)


    def parse_expression(self):
        # handle parenthesis
        main_term = None

        if self._check_token_value( ["("] ):
            # consume opening
            self._pull_token()

            # parse expression
            main_term = self.parse_expression()

            # check if there is closing bracket and if not, error
            if not self._check_token_value( [")"] ):
                raise SyntaxError()

            # consume closing bracket
            self._pull_token()
        else:
            raise NotImplementedError()


        return main_term

    def parse_code(self):
        pass

    def parse_any(self):
        pass