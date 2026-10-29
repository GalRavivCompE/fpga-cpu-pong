"""Run the four-instruction program traced in the project discussion."""

from cpu import CPU


# Byte PC  Assembly                 Encoded instruction word
PROGRAM = [
    0x0C20_0000,  # 0   DUPE R1, R0
    0x0420_0007,  # 4   SET_LOW R1, 7
    0x2441_0005,  # 8   ADD_CONST R2, R1, 5
    0xD400_0000,  # 12  HALT
]


if __name__ == "__main__":
    cpu = CPU(PROGRAM)
    while not cpu.halted:
        address = cpu.pc
        word = PROGRAM[address // 4]
        cpu.step()
        print(f"PC={address:2}  word=0x{word:08X}  R0={cpu.read_reg(0)}  "
              f"R1={cpu.read_reg(1)}  R2={cpu.read_reg(2)}")
