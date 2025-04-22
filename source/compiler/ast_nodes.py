from bytecodes import LiteralTags, Opcodes
import struct

def translate_integer(value):
    return value.to_bytes(8, byteorder="big", signed=True)

class CodeContext:
    """
    Represents code object in bytecode form - with separate literals and bytecode
    Used by nodes to compile themselves into it
    """
    def __init__(self):
        self._stack_usage = 0
        self._literal_bytes = []
        self._bytecode = []

    def add_literal_bytes(self, literal_bytes):
        index = len(self._literal_bytes)
        self._literal_bytes.append(literal_bytes)

        return index

    def add_instruction(self, opcode, opcode_parameter):
        if opcode in (Opcodes.PUSH_MYSELF, Opcodes.PUSH_LITERAL):
            self._stack_usage += 1

        if not (0 <= opcode_parameter <= 255):
            raise SyntaxError()

        self._bytecode.append(opcode)
        self._bytecode.append(opcode_parameter)

    def get_compiled(self):
        code_bytes = [LiteralTags.VM_CODE]

        # add stack usage
        code_bytes.extend(
            translate_integer(self._stack_usage)
        )

        # add literals
        code_bytes.append(LiteralTags.VM_OBJECT_ARRAY)
        code_bytes.extend(
            translate_integer(len(self._literal_bytes))
        )
        for one_literal_bytes in self._literal_bytes:
            code_bytes.extend(one_literal_bytes)

        # add bytecode
        code_bytes.append(LiteralTags.VM_BYTE_ARRAY)
        code_bytes.extend(
            translate_integer(len(self._bytecode))
        )
        code_bytes.extend(self._bytecode)

        return code_bytes







class SendNode:
    """
    Represents message send tree node
    """
    def __init__(self, receiver, selector, parameters):
        self._receiver = receiver
        self._selector = selector
        self._parameters = parameters

    def compile(self, code_context):
        # compile receiver
        self._receiver.compile(code_context)

        # compile parameters
        for parameter in self._parameters:
            parameter.compile(code_context)

        # get arity
        arity = len(self._parameters)

        # compile symbol box
        selector_bytes = self._selector.get_compiled_with(arity)
        selector_index = code_context.add_literal_bytes(selector_bytes)

        # add send instruction
        code_context.add_instruction(
            Opcodes.SEND,
            selector_index
        )

        return code_context

class ExplicitReturnNode:
    """
    Represents explicit return from method
    """
    def __init__(self, return_node):
        self._return_node = return_node

    def compile(self, code_context):
        self._return_node.compile(code_context)

        code_context.add_instruction(Opcodes.RETURN_EXPLICIT, 0x00)

        return code_context

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
        return [LiteralTags.VM_SMALL_INTEGER] + list( translate_integer(self._value) )


class StringBox(SimpleValueBox):
    def get_compiled(self):
        my_bytes = [LiteralTags.VM_STRING]

        character_bytes = bytes(self._value.encode("utf-8"))

        my_bytes.extend(translate_integer(len(self._value)))

        my_bytes.extend(list(character_bytes))

        return my_bytes

class UnfinishedSymbolBox(SimpleValueBox):
    def get_compiled_with(self, symbol_arity):
        symbol_bytes = [LiteralTags.VM_SYMBOL]

        symbol_bytes.extend(
            translate_integer(symbol_arity)
        )
        symbol_bytes.extend(
            translate_integer(len(self._value))
        )
        symbol_bytes.extend(
            (ord(character) for character in self._value)
        )

        return symbol_bytes

class CompleteSymbolBox:
    def __init__(self, arity, characters):
        self._characters = characters
        self._arity = arity

    def get_compiled(self):
        symbol_bytes = [LiteralTags.VM_SYMBOL]

        symbol_bytes.extend(
            translate_integer(self._arity)
        )
        symbol_bytes.extend(
            translate_integer(len(self._characters))
        )
        symbol_bytes.extend(
            (ord(character) for character in self._characters)
        )

        return symbol_bytes

class CodeBox(SimpleValueBox):
    def get_compiled(self):
        new_code_context = CodeContext()

        *rest, tail = self._value

        for node in rest:
            node.compile(new_code_context)
            new_code_context.add_instruction(Opcodes.PULL, 0x00)

        tail.compile(new_code_context)

        return new_code_context




class ObjectBox:
    """
    Box storing object. Because its complexity, it cannot be handed by simple value box
    """
    def __init__(self, slots, code):
        self._slots = slots
        self._code = code

    def get_compiled(self):
        object_bytes = [LiteralTags.VM_OBJECT]

        # handle slots - there is 0 for now, because slots are not implemented yet
        object_bytes.extend(translate_integer(0))

        # handle code
        if self._code is None:
            object_bytes.append(LiteralTags.VM_NONE)
        else:
            object_bytes.extend(
                self._code.get_compiled()
            )

        return object_bytes

class NoneBox:
    def get_compiled(self):
        return [LiteralTags.VM_NONE]