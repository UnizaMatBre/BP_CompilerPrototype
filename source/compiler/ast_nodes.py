from bytecodes import LiteralTags, Opcodes
import struct


class CodeContext:
    """
    Represents code object in bytecode form - with separate literals and bytecode
    Used by nodes to compile themselves into it
    """
    def __init__(self):
        self._literal_bytes = []
        self._bytecode = []

    def add_literal_bytes(self, literal_bytes):
        index = len(self._literal_bytes)
        self._literal_bytes.append(literal_bytes)

        return index

    def add_instruction(self, opcode, opcode_parameter):
        self._bytecode.append(opcode)
        self._bytecode.append(opcode_parameter)






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

    def compile(self, code_context):
        # turns literal into bytes
        literal_bytes = self._literal_value.get_compiled()

        # store literal and gets its index
        literal_index = code_context.add_literal_bytes(literal_bytes)

        # store instruction
        code_context.add_instruction(
            Opcodes.PUSH_LITERAL,
            literal_index
        )

        return code_context


class SimpleValueBox:
    def __init__(self, value):
        self._value = value

class IntegerBox(SimpleValueBox):
    def get_compiled(self):
        return [LiteralTags.VM_SMALL_INTEGER] + list( self._value.to_bytes(8, byteorder="big", signed=True) )


class StringBox(SimpleValueBox):
    def get_compiled(self):
        my_bytes = [LiteralTags.VM_STRING]

        character_bytes = bytes(self._value.encode("utf-8"))

        my_bytes.extend(list(
            len(character_bytes).to_bytes(8, byteorder="big", signed=True)
        ))

        my_bytes.extend(list(character_bytes))

        return my_bytes

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