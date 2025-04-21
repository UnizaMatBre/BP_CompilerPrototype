
CORRECT_MODULE_SIGNATURE = [ord(char) for char in "ORE"]

class Opcodes:

    # empty opcode, does nothing
    NOOP = 0x00

    # push running method into active frame stack
    PUSH_MYSELF = 0x10

    # push literal from specified index into active frame stack
    PUSH_LITERAL = 0x11

    # pull item from active frame stack and throw it away
    PULL = 0x1A

    # send message, selector is specified by literal index
    SEND = 0x20

    # returns top of the stack to previous frame
    RETURN_EXPLICIT = 0x30


class LiteralTags:
    """Enumeration of tags that determine interpretation of following bytes"""
    VM_NONE = 0x00
    VM_SMALL_INTEGER = 0x01

    VM_BYTE_ARRAY = 0x10
    VM_OBJECT_ARRAY = 0x11
    VM_SYMBOL = 0x12
    VM_STRING = 0x13

    VM_CODE = 0x20
    VM_ASSIGNMENT = 0x21

    VM_OBJECT = 0x30


class SlotKindTags:
    PARENT_SLOT_TAG =  0b00000001

    PARAMETER_SLOT_TAG = 0b00000010
