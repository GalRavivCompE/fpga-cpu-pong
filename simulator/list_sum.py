"""Assemble and execute the list-summing example from the ISA documentation."""

from pathlib import Path

from assembler import assemble
from cpu import CPU


SOURCE = Path(__file__).with_name("list_sum.asm").read_text()


def run_list(values):
    cpu = CPU(assemble(SOURCE))
    cpu.write_word(256, len(values))
    for index, value in enumerate(values):
        cpu.write_word(260 + 4 * index, value)
    cpu.run()
    return cpu


if __name__ == "__main__":
    values = [7, 12, 5]
    cpu = run_list(values)
    print(f"List: {values}")
    print(f"Sum in R1: {cpu.read_reg(1)}")
    print(f"Stopped at byte PC: {cpu.pc}")
