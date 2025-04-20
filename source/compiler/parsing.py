


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