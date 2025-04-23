import enum

from source.compiler.ast_nodes import CodeBox, LiteralNode, IntegerBox, StringBox, SendNode
from source.compiler.tokenization import TokenTypes, Tokenizer




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


            match token_type:
                # return integer literal box
                case TokenTypes.INTEGER:
                    main_term = LiteralNode(
                        IntegerBox(token_value)
                    )

                # return string literal box
                case TokenTypes.STRING:
                    main_term = LiteralNode(
                        StringBox(token_value)
                    )

                # handle object
                case TokenTypes.OBJECT_BRACKET_OPEN:
                    raise NotImplementedError()

                # handle send
                case TokenTypes.KEYWORD_SYMBOL | TokenTypes.OPERATOR_SYMBOL:
                    raise NotImplementedError()

                # any other token type is not allowed here
                case unknown_token:
                    raise SyntaxError()

        # handle possible sends
        self._consume_whitespaces()

        if self._check_token_type([TokenTypes.COLON]):
            # consume colon
            self._pull_token()


            token_type, token_location, token_value = self._pull_token()

            # next token MUST BE a symbol of any kind
            if not token_type in (TokenTypes.OPERATOR_SYMBOL, TokenTypes.KEYWORD_SYMBOL):
                raise SyntaxError()

            selector = token_value

            # parsing of parameters will be handled later
            parameters = []


            main_term = SendNode(
                receiver=main_term,
                selector=selector,
                parameters=parameters
            )

            #consume any following whitespaces
            self._consume_whitespaces()





        return main_term

    def parse_code(self):
        pass

    def parse_any(self):
        pass