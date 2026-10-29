"""Small two-pass assembler for the simulator's implemented ISA subset.

Pass 1 records label addresses. Pass 2 encodes instructions and converts
GHOST/REPEAT label targets to instruction counts. This is not a full assembler.
"""

OPCODES = {
    "SET_LOW": 0x01, "SET_HIGH": 0x02, "DUPE": 0x03, "ADD": 0x04,
    "ADD_CONST": 0x09, "READ": 0x20, "READ_BYTE": 0x21,
    "WRITE": 0x22, "IF_EQ": 0x28, "GHOST": 0x30,
    "REPEAT": 0x31, "HALT": 0x35,
}


def _register(token):
    if not token.startswith("R") or not token[1:].isdecimal():
        raise ValueError(f"expected register R0–R31, got {token!r}")
    number = int(token[1:])
    if not 0 <= number <= 31:
        raise ValueError(f"register out of range: {token}")
    return number


def _address_register(token):
    if not (token.startswith("[") and token.endswith("]")):
        raise ValueError(f"expected [R0]–[R31], got {token!r}")
    return _register(token[1:-1])


def _number(token, minimum, maximum):
    value = int(token, 0)
    if not minimum <= value <= maximum:
        raise ValueError(f"value {value} outside {minimum}..{maximum}")
    return value


def assemble(source):
    """Convert readable assembly text to a list of 32-bit instruction words."""
    labels = {}
    instructions = []

    # Labels consume no instruction word, so the address is 4 * current count.
    for line_number, raw in enumerate(source.splitlines(), 1):
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        if line.endswith(":"):
            label = line[:-1]
            if not label.isidentifier() or label in labels:
                raise ValueError(f"line {line_number}: invalid or duplicate label {label!r}")
            labels[label] = len(instructions)
        else:
            instructions.append((line_number, line))

    words = []
    for index, (line_number, line) in enumerate(instructions):
        try:
            parts = line.split(None, 1)
            mnemonic = parts[0]
            operand_text = parts[1] if len(parts) == 2 else ""
            operands = ([part.strip() for part in operand_text.split(",")]
                        if operand_text else [])
            if mnemonic not in OPCODES:
                raise ValueError(f"unsupported instruction {mnemonic!r}")
            expected = {
                "SET_LOW": 2, "SET_HIGH": 2, "DUPE": 2, "ADD": 3,
                "ADD_CONST": 3, "READ": 2, "READ_BYTE": 2,
                "WRITE": 2, "IF_EQ": 3, "GHOST": 1,
                "REPEAT": 1, "HALT": 0,
            }[mnemonic]
            if len(operands) != expected:
                raise ValueError(f"{mnemonic} needs {expected} operand(s)")

            word = OPCODES[mnemonic] << 26
            if mnemonic in ("SET_LOW", "SET_HIGH"):
                word |= _register(operands[0]) << 21
                word |= _number(operands[1], 0, 65535)
            elif mnemonic == "ADD":
                word |= _register(operands[0]) << 21
                word |= _register(operands[1]) << 16
                word |= _register(operands[2]) << 11
            elif mnemonic == "ADD_CONST":
                word |= _register(operands[0]) << 21
                word |= _register(operands[1]) << 16
                word |= _number(operands[2], -32768, 32767) & 0xFFFF
            elif mnemonic in ("READ", "READ_BYTE", "WRITE"):
                word |= _register(operands[0]) << 21
                word |= _address_register(operands[1]) << 16
            elif mnemonic == "DUPE":
                word |= _register(operands[0]) << 21
                word |= _register(operands[1]) << 16
            elif mnemonic == "IF_EQ":
                word |= _register(operands[0]) << 21
                word |= _register(operands[1]) << 16
                word |= _number(operands[2], 0, 65535)
            elif mnemonic in ("GHOST", "REPEAT"):
                target = operands[0]
                if target in labels:
                    count = (labels[target] - index - 1 if mnemonic == "GHOST"
                             else index - labels[target])
                else:
                    count = _number(target, 0, 65535)
                if count < 0 or (mnemonic == "REPEAT" and count == 0):
                    raise ValueError(f"{mnemonic} target has wrong direction")
                word |= _number(str(count), 0, 65535)
            words.append(word)
        except ValueError as error:
            raise ValueError(f"line {line_number}: {error}") from error
    return words
