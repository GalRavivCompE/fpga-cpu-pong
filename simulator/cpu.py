"""First executable slice of the proposed 32-bit CPU ISA.

This is a teaching simulator, not FPGA hardware. It currently implements only
DUPE, SET_LOW, ADD_CONST, and HALT. Each instruction is one 32-bit integer.
"""

MASK32 = 0xFFFF_FFFF

SET_LOW = 0x01
DUPE = 0x03
ADD_CONST = 0x09
HALT = 0x35


class CPU:
    def __init__(self, program):
        self.program = list(program)
        self.regs = [0] * 32
        self.pc = 0  # Byte address in instruction memory.
        self.halted = False

    def read_reg(self, number):
        # R0 is wired to zero, regardless of attempted writes.
        return 0 if number == 0 else self.regs[number]

    def write_reg(self, number, value):
        if number != 0:
            self.regs[number] = value & MASK32

    def step(self):
        """Fetch, decode, and execute one instruction at the current PC."""
        if self.halted:
            raise RuntimeError("CPU is halted")
        if self.pc % 4 or not 0 <= self.pc // 4 < len(self.program):
            raise RuntimeError(f"invalid instruction address {self.pc}")

        word = self.program[self.pc // 4]
        if not 0 <= word <= MASK32:
            raise ValueError(f"instruction is not 32 bits: {word}")

        opcode = (word >> 26) & 0x3F
        first = (word >> 21) & 0x1F
        second = (word >> 16) & 0x1F
        imm16 = word & 0xFFFF

        if opcode == DUPE:
            if imm16 != 0:
                raise ValueError("DUPE has nonzero reserved bits")
            self.write_reg(first, self.read_reg(second))
        elif opcode == SET_LOW:
            if second != 0:
                raise ValueError("SET_LOW has nonzero reserved bits")
            old = self.read_reg(first)
            self.write_reg(first, (old & 0xFFFF_0000) | imm16)
        elif opcode == ADD_CONST:
            # The embedded 16-bit value is signed; e.g. 0xFFFF means -1.
            signed_imm = imm16 if imm16 < 0x8000 else imm16 - 0x10000
            self.write_reg(first, self.read_reg(second) + signed_imm)
        elif opcode == HALT:
            if word & 0x03FF_FFFF:
                raise ValueError("HALT has nonzero reserved bits")
            self.halted = True
            return
        else:
            raise ValueError(f"opcode 0x{opcode:02X} is not implemented")

        self.pc += 4

    def run(self, max_steps=1000):
        """Run until HALT, with a limit to catch programs that do not stop."""
        for _ in range(max_steps):
            if self.halted:
                return
            self.step()
        if not self.halted:
            raise RuntimeError(f"program did not halt within {max_steps} steps")
