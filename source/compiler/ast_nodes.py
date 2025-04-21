

class SendNode:
    """
    Represents message send tree node
    """
    def __init__(self, receiver, selector, parameters):
        self._receiver = receiver
        self._selector = selector
        self._parameters = parameters



class LiteralNode:
    """
    Represents literal that appears in code (and thus needs to be stored in list of literals)
    """
    def __init__(self, literal_value):
        self._literal_value = literal_value



class SimpleValueBox:
    def __init__(self, value):
        self._value = value

class IntegerBox(SimpleValueBox):
    pass

class DecimalBox(SimpleValueBox):
    pass

class StringBox(SimpleValueBox):
    pass