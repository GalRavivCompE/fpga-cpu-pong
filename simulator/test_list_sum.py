"""Checks for assembly labels, loops, and byte-addressed data RAM."""

import unittest

from assembler import assemble
from cpu import CPU
from list_sum import run_list


class ListAndMemoryTests(unittest.TestCase):
    def test_list_lengths_and_32_bit_wraparound(self):
        for values, expected in [([], 0), ([9], 9), ([7, 12, 5], 24),
                                 ([0xFFFF_FFFF, 1], 0)]:
            with self.subTest(values=values):
                cpu = run_list(values)
                self.assertTrue(cpu.halted)
                self.assertEqual(cpu.read_reg(1), expected)
                self.assertEqual(cpu.pc, 44)

    def test_word_write_and_little_endian_byte_read(self):
        program = assemble("""
            SET_LOW R1, 256
            SET_LOW R2, 0x1234
            WRITE R2, [R1]
            ADD_CONST R1, R1, 1
            READ_BYTE R3, [R1]
            HALT
        """)
        cpu = CPU(program)
        cpu.run()
        self.assertEqual(cpu.read_word(256), 0x1234)
        self.assertEqual(cpu.read_reg(3), 0x12)

    def test_bad_word_address_faults(self):
        cpu = CPU(assemble("READ R1, [R2]"))
        cpu.write_reg(2, 257)
        with self.assertRaisesRegex(ValueError, "unaligned"):
            cpu.step()

    def test_assembler_rejects_out_of_range_register(self):
        with self.assertRaisesRegex(ValueError, "line 1"):
            assemble("DUPE R32, R0")


if __name__ == "__main__":
    unittest.main()
