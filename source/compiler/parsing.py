import enum

from source.compiler.ast_nodes import CodeBox, LiteralNode, IntegerBox, StringBox, SendNode, UnfinishedSymbolBox, \
    MyselfNode
from source.compiler.tokenization import TokenTypes, Tokenizer




class Parser:
    def __init__(self, tokens):
        self._tokens = tokens
        self._tokens_index = 0

    def _consume_whitespaces(self):
        """Jumps over all whitespace tokens in token list"""

        while self._peek_token()[0].value == TokenTypes.WHITESPACE.value:
            self._pull_token()

    def _check_token_type(self, wanted_token_types):
        """Checks if current token has type we want"""
        token_type, _, _ = self._peek_token()

        return token_type.value in (t.value for t in wanted_token_types)


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
        main_term = None

        # consume whitespaces before expression itself
        self._consume_whitespaces()


        # handle parenthesis
        if self._check_token_value( ["("] ):
            # consume opening bracket
            self._pull_token()

            # parse expression
            main_term = self.parse_expression()

            # consume whitespaces between expression and closing bracket
            self._consume_whitespaces()

            # check if there is closing bracket and if not, error
            if not self._check_token_value( [")"] ):
                raise SyntaxError()

            # consume closing bracket
            self._pull_token()

        # handle normal expression (without parenthesis)
        else:
            token_type, token_location, token_value = self._pull_token()

            # TODO: This is extremely brain damaged approach, but i don' know how to solve it right now
            if token_type.value == TokenTypes.INTEGER.value:
                main_term = LiteralNode(
                    IntegerBox(token_value)
                )

            elif token_type.value  == TokenTypes.STRING.value:
                main_term = LiteralNode(
                    StringBox(token_value)
                )

            elif token_type.value  == TokenTypes.OBJECT_BRACKET_OPEN.value:
                raise NotImplementedError()

            elif token_type.value  in (TokenTypes.KEYWORD_SYMBOL.value, TokenTypes.OPERATOR_SYMBOL.value):
                selector = UnfinishedSymbolBox(token_value)
                parameters = []

                main_term = SendNode(
                    receiver=MyselfNode(),
                    selector=selector,
                    parameters=[]
                )



            else:
                raise SyntaxError()

        # handle possible sends
        self._consume_whitespaces()

        while self._check_token_type([TokenTypes.COLON]):
            # consume colon
            self._pull_token()


            token_type, token_location, token_value = self._pull_token()

            # next token MUST BE a symbol of any kind
            if not token_type.value in (TokenTypes.OPERATOR_SYMBOL.value, TokenTypes.KEYWORD_SYMBOL.value):
                raise SyntaxError()

            selector = UnfinishedSymbolBox(token_value)

            parameters = []

            # parse parameters
            if self._check_token_value(["("]):
                self._pull_token()

                while True:

                    parameters.append(
                        self.parse_expression()
                    )

                    if self._check_token_value([")"]):
                        self._pull_token()
                        break

                    if self._check_token_type([TokenTypes.COMMA]):
                        self._pull_token()
                        continue

                    raise SyntaxError()






            main_term = SendNode(
                receiver=main_term,
                selector=selector,
                parameters=parameters
            )

            #consume any following whitespaces
            self._consume_whitespaces()


        while self._check_token_type( [TokenTypes.OPERATOR_SYMBOL] ):
            # get selector
            _, token_location, token_value = self._pull_token()

            selector = UnfinishedSymbolBox(token_value)

            # consume whitespaces
            self._consume_whitespaces()

            parameters = []

            if not self._check_token_type( [TokenTypes.COMMA] ):
                parameters = [ self.parse_expression() ]

            main_term = SendNode(
                receiver=main_term,
                selector=selector,
                parameters=parameters
            )

        return main_term

    def parse_code(self):
        pass

    def parse_any(self):
        pass