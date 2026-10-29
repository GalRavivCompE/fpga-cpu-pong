"""First executable slice of the proposed 32-bit CPU ISA.

This is a teaching simulator, not FPGA hardware. It implements only the subset
needed for a list loop and basic memory access. Each instruction is a 32-bit word.
"""

MASK32 = 0xFFFF_FFFF

SET_LOW = 0x01
SET_HIGH = 0x02
DUPE = 0x03
ADD = 0x04
ADD_CONST = 0x09
READ = 0x20
READ_BYTE = 0x21
WRITE = 0x22
IF_EQ = 0x28
GHOST = 0x30
REPEAT = 0x31
HALT = 0x35


class CPU:
    def __init__(self, program, ram_size=1024):
        self.program = list(program)
        self.regs = [0] * 32
        self.pc = 0  # Byte address in instruction memory.
        self.halted = False
        # A small simulator-only data RAM. The board memory map is still open.
        self.ram = bytearray(ram_size)

    def read_reg(self, number):
        # R0 is wired to zero, regardless of attempted writes.
        return 0 if number == 0 else self.regs[number]

    def write_reg(self, number, value):
        if number != 0:
            self.regs[number] = value & MASK32

    def _check_address(self, address, size):
        if size == 4 and address % 4:
            raise ValueError(f"unaligned word address {address}")
        if not 0 <= address <= len(self.ram) - size:
            raise ValueError(f"unmapped data address {address}")

    def read_word(self, address):
        self._check_address(address, 4)
        return int.from_bytes(self.ram[address:address + 4], "little")

    def write_word(self, address, value):
        self._check_address(address, 4)
        self.ram[address:address + 4] = (value & MASK32).to_bytes(4, "little")

    def read_byte(self, address):
        self._check_address(address, 1)
        return self.ram[address]

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
        third = (word >> 11) & 0x1F
        imm16 = word & 0xFFFF
        next_pc = self.pc + 4

        if opcode == DUPE:
            if imm16 != 0:
                raise ValueError("DUPE has nonzero reserved bits")
            self.write_reg(first, self.read_reg(second))
        elif opcode == SET_LOW:
            if second != 0:
                raise ValueError("SET_LOW has nonzero reserved bits")
            old = self.read_reg(first)
            self.write_reg(first, (old & 0xFFFF_0000) | imm16)
        elif opcode == SET_HIGH:
            if second != 0:
                raise ValueError("SET_HIGH has nonzero reserved bits")
            old = self.read_reg(first)
            self.write_reg(first, (imm16 << 16) | (old & 0xFFFF))
        elif opcode == ADD:
            if word & 0x7FF:
                raise ValueError("ADD has nonzero reserved bits")
            self.write_reg(first, self.read_reg(second) + self.read_reg(third))
        elif opcode == ADD_CONST:
            # The embedded 16-bit value is signed; e.g. 0xFFFF means -1.
            signed_imm = imm16 if imm16 < 0x8000 else imm16 - 0x10000
            self.write_reg(first, self.read_reg(second) + signed_imm)
        elif opcode == READ:
            if imm16 != 0:
                raise ValueError("READ has nonzero reserved bits")
            self.write_reg(first, self.read_word(self.read_reg(second)))
        elif opcode == READ_BYTE:
            if imm16 != 0:
                raise ValueError("READ_BYTE has nonzero reserved bits")
            self.write_reg(first, self.read_byte(self.read_reg(second)))
        elif opcode == WRITE:
            if imm16 != 0:
                raise ValueError("WRITE has nonzero reserved bits")
            self.write_word(self.read_reg(second), self.read_reg(first))
        elif opcode == IF_EQ:
            if self.read_reg(first) != self.read_reg(second):
                next_pc += 4 * imm16
        elif opcode == GHOST:
            if (word >> 16) & 0x3FF:
                raise ValueError("GHOST has nonzero reserved bits")
            next_pc += 4 * imm16
        elif opcode == REPEAT:
            if (word >> 16) & 0x3FF:
                raise ValueError("REPEAT has nonzero reserved bits")
            if imm16 == 0:
                raise ValueError("REPEAT count must be at least one")
            next_pc = self.pc - 4 * imm16
        elif opcode == HALT:
            if word & 0x03FF_FFFF:
                raise ValueError("HALT has nonzero reserved bits")
            self.halted = True
            return
        else:
            raise ValueError(f"opcode 0x{opcode:02X} is not implemented")

        self.pc = next_pc

    def run(self, max_steps=1000):
        """Run until HALT, with a limit to catch programs that do not stop."""
        for _ in range(max_steps):
            if self.halted:
                return
            self.step()
        if not self.halted:
            raise RuntimeError(f"program did not halt within {max_steps} steps")
