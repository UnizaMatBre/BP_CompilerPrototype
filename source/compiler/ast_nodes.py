from bytecodes import LiteralTags
import struct

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
    def get_compiled(self):
        return [LiteralTags.VM_SMALL_INTEGER] + list( self._value.to_bytes(8, byteorder="big", signed=True) )


class StringBox(SimpleValueBox):
    def get_compiled(self):
        my_bytes = [LiteralTags.VM_STRING]

        my_bytes.extend(list(
            len(self._value).to_bytes(8, byteorder="big", signed=True)
        ))


class ObjectBox:
    """
    Box storing object. Because its complexity, it cannot be handed by simple value box
    """
    def __init__(self, slots, code):
        self._slots = slots
        self._code = code

class NoneBox:
    def get_compiled(self):
        return [LiteralTags.VM_NONE]