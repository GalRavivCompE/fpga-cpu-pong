"""Small checks for behaviors that are easy to misread in the ISA draft."""

import unittest

from cpu import CPU
from first_program import PROGRAM


class FirstSliceTests(unittest.TestCase):
    def test_hand_traced_program(self):
        cpu = CPU(PROGRAM)
        cpu.run()
        self.assertTrue(cpu.halted)
        self.assertEqual(cpu.pc, 12)
        self.assertEqual((cpu.read_reg(0), cpu.read_reg(1), cpu.read_reg(2)),
                         (0, 7, 12))

    def test_r0_ignores_writes_and_set_low_preserves_high_half(self):
        cpu = CPU([0x0420_0007])  # SET_LOW R1, 7
        cpu.write_reg(0, 99)
        cpu.write_reg(1, 0xABCD_1234)
        cpu.step()
        self.assertEqual(cpu.read_reg(0), 0)
        self.assertEqual(cpu.read_reg(1), 0xABCD_0007)

    def test_add_const_sign_extension_and_wraparound(self):
        cpu = CPU([0x2421_FFFF])  # ADD_CONST R1, R1, -1
        cpu.step()
        self.assertEqual(cpu.read_reg(1), 0xFFFF_FFFF)


if __name__ == "__main__":
    unittest.main()
