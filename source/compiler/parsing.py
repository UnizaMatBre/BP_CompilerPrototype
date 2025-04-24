import enum

from source.compiler.ast_nodes import CodeBox, LiteralNode, IntegerBox, StringBox, SendNode, UnfinishedSymbolBox, \
    MyselfNode, NoneBox, CompleteSymbolBox, ObjectBox
from source.compiler.tokenization import TokenTypes, Tokenizer


class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self._tokens = tokens
        self._tokens_index = 0

    def _consume_whitespaces(self):
        """Jumps over all whitespace tokens in token list"""

        while self._peek_token()[0].value == TokenTypes.WHITESPACE.value:
            self._pull_token()

    def _check_consume_token_value(self, token_values):
        """Checks if token value matches and if yes, consumes it"""
        result = self._check_token_value(token_values)

        if result:
            self._pull_token()

        return result

    def _check_consume_token_type(self, token_types):
        """Checks if token type matches and if yes, consumes it"""
        result = self._check_token_type(token_types)

        if result:
            self._pull_token()

        return result

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


    def _raise_ParserError(self, expected_token, found_token, position):
        raise ParserError(
            "At {}: expected {}, found {} instead".format(
                position,
                expected_token,
                found_token
            )
        )

    def parse_root_code(self):
        expression_list = []

        token_type, _, _ = self._peek_token()

        while token_type != TokenTypes.EOF:
            expression_list.append(
                self.parse_expression()
            )

            if not self._check_consume_token_type([TokenTypes.COMMA]):
                error_type, error_pos, error_value = self._peek_token()

                self._raise_ParserError(
                    expected_token=(TokenTypes.COMMA, ")"),
                    found_token=(error_type, error_value),
                    position=error_pos
                )

            token_type, _, _ = self._peek_token()

        return CodeBox(expression_list)


    def parse_expression(self):
        main_term = None

        # consume whitespaces before expression itself
        self._consume_whitespaces()


        # handle parenthesis
        if self._check_consume_token_value(["("]):

            # parse expression
            main_term = self.parse_expression()

            # consume whitespaces between expression and closing bracket
            self._consume_whitespaces()

            # check if there is closing bracket and if not, error
            if not self._check_consume_token_value( [")"] ):
                error_type, error_pos, error_value = self._peek_token()

                self._raise_ParserError(
                    expected_token=(TokenTypes.BRACKET_CLOSE, ")"),
                    found_token=(error_type, error_value),
                    position=error_pos
                )

        # handle normal expression (without parenthesis)
        else:
            token_type, token_location, token_value = self._peek_token()


            # TODO: This is extremely brain damaged approach, but i don' know how to solve it right now
            if token_type.value in (TokenTypes.KEYWORD_SYMBOL.value, TokenTypes.OPERATOR_SYMBOL.value):
                self._pull_token()
                selector = UnfinishedSymbolBox(token_value)
                parameters = self._parse_message_arguments()

                main_term = SendNode(
                    receiver=MyselfNode(),
                    selector=selector,
                    parameters=parameters
                )
            else:
                main_term = self._parse_literal()

        # handle possible sends
        self._consume_whitespaces()

        while self._check_consume_token_type([TokenTypes.COLON]):
            token_type, token_location, token_value = self._pull_token()

            # next token MUST BE a symbol of any kind
            if not token_type.value in (TokenTypes.OPERATOR_SYMBOL.value, TokenTypes.KEYWORD_SYMBOL.value):
                self._raise_ParserError(
                    expected_token=[TokenTypes.KEYWORD_SYMBOL, TokenTypes.OPERATOR_SYMBOL],
                    found_token=(token_type, token_value),
                    position=token_location
                )

            selector = UnfinishedSymbolBox(token_value)

            parameters = self._parse_message_arguments()

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

    def _parse_literal(self):
        token_type, token_position, token_value = self._pull_token()

        # TODO: Fix this brain damage approach
        if token_type.value == TokenTypes.INTEGER.value:
            return IntegerBox(token_value)

        if token_type.value == TokenTypes.STRING.value:
            return StringBox(token_value)

        if token_type.value == TokenTypes.OBJECT_BRACKET_OPEN.value:
            return self._parse_object()

        #unknown literal
        self._raise_ParserError(
            expected_token=[TokenTypes.INTEGER, TokenTypes.STRING, TokenTypes.OBJECT_BRACKET_OPEN],
            found_token=(token_type, token_value),
            position=token_position
        )
        return None

    def _parse_object(self):
        slots = []
        code = None

        self._consume_whitespaces()
        while not self._check_token_type( [TokenTypes.OBJECT_BRACKET_CLOSE, TokenTypes.SEMICOLON] ):
            #take slot name
            if not self._check_token_type([TokenTypes.OPERATOR_SYMBOL, TokenTypes.KEYWORD_SYMBOL]):
                error_type, error_pos, error_value = self._peek_token()

                self._raise_ParserError(
                    expected_token=[TokenTypes.OPERATOR_SYMBOL, TokenTypes.KEYWORD_SYMBOL],
                    found_token=(error_type, error_value),
                    position=error_pos
                )

            _, _, slot_name = self._pull_token()

            ## take arity
            if not self._check_consume_token_value(["("]):
                error_type, error_pos, error_value = self._peek_token()

                self._raise_ParserError(
                    expected_token=(TokenTypes.BRACKET_OPEN, "("),
                    found_token=(error_type, error_value),
                    position=error_pos
                )

            if not self._check_token_type([TokenTypes.INTEGER]):
                error_type, error_pos, error_value = self._peek_token()

                self._raise_ParserError(
                    expected_token=[TokenTypes.INTEGER],
                    found_token=(error_type, error_value),
                    position=error_pos
                )


            _, position, arity = self._pull_token()

            if not self._check_consume_token_value([")"]):
                error_type, error_pos, error_value = self._peek_token()

                self._raise_ParserError(
                    expected_token=(TokenTypes.BRACKET_CLOSE, ")"),
                    found_token=(error_type, error_value),
                    position=error_pos
                )

            if arity < 0:
                raise SyntaxError()

            self._consume_whitespaces()

            slot_content = NoneBox()

            # if there is no comma, there is value to load
            if not self._check_token_type([TokenTypes.COMMA]):
                if not self._check_token_value(["="]):
                    error_type, error_pos, error_value = self._peek_token()

                    self._raise_ParserError(
                        expected_token=(TokenTypes.OPERATOR_SYMBOL, "="),
                        found_token=(error_type, error_value),
                        position=error_pos
                    )

                self._pull_token()
                self._consume_whitespaces()

                # read value (literal)
                slot_content = self._parse_literal()

                self._consume_whitespaces()
                if not self._check_token_type([TokenTypes.COMMA]):
                    error_type, error_pos, error_value = self._peek_token()

                    self._raise_ParserError(
                        expected_token=(TokenTypes.COMMA, ","),
                        found_token=(error_type, error_value),
                        position=error_pos
                    )

            # consume comma
            self._pull_token()

            slots.append((
                CompleteSymbolBox(slot_name, arity),
                (), #TODO: Implement slot kind handling
                slot_content
            ))

            self._consume_whitespaces()

        if self._check_token_type([TokenTypes.SEMICOLON]):
            self._pull_token()

            code = []
            while not self._check_consume_token_type([TokenTypes.OBJECT_BRACKET_CLOSE]):
                code.append(self.parse_expression())

                # check and consume token
                if not self._check_consume_token_type([TokenTypes.COMMA]):
                    error_type, error_pos, error_value = self._peek_token()

                    self._raise_ParserError(
                        expected_token=(TokenTypes.COMMA, ","),
                        found_token=(error_type, error_value),
                        position=error_pos
                    )

                self._consume_whitespaces()

            code = CodeBox(code)

        return ObjectBox(
            slots=slots,
            code=code
        )

    def _parse_message_arguments(self):
        arguments = []

        if not self._check_token_value(["("]):
            return arguments

        # consume opening bracket
        self._pull_token()

        while True:

            arguments.append(
                self.parse_expression()
            )

            if self._check_token_value([")"]):
                self._pull_token()
                break

            if self._check_token_type([TokenTypes.COMMA]):
                self._pull_token()
                continue

            error_type, error_pos, error_value = self._peek_token()

            self._raise_ParserError(
                expected_token=[TokenTypes.COMMA, TokenTypes.BRACKET_CLOSE],
                found_token=(error_type, error_value),
                position=error_pos
            )
        return arguments

    def parse_code(self):
        pass

    def parse_any(self):
        pass