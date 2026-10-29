# First simulator slice

**Status: working in Python simulation only.** The simulator executes four proposed instructions: `DUPE`, `SET_LOW`, `ADD_CONST`, and `HALT`. It does not yet model RAM, input/output, other instructions, or FPGA hardware.

Run from the repository root:

```sh
python3 simulator/first_program.py
python3 -m unittest discover -s simulator -v
```

The sample program is stored as four 32-bit instruction words. The program counter (`PC`) is a **byte address**, so it fetches the words at addresses 0, 4, 8, and 12. The decoder extracts the opcode from bits 31:26 and register numbers from the fields defined in the [ISA reference](../isa/reference.md).

| PC | Assembly | Word | Expected result after execution |
| ---: | --- | --- | --- |
| 0 | `DUPE R1, R0` | `0x0C200000` | R1 = 0 |
| 4 | `SET_LOW R1, 7` | `0x04200007` | R1 = 7 |
| 8 | `ADD_CONST R2, R1, 5` | `0x24410005` | R2 = 12 |
| 12 | `HALT` | `0xD4000000` | CPU stops; PC stays 12 |

The tests also check that writes cannot change R0, `SET_LOW` preserves the upper 16 bits, and `ADD_CONST` sign-extends a negative immediate and wraps to 32 bits. This is a behavior model for learning and checking the encoding. Later RTL simulation must be tested separately; passing Python tests does not show that an FPGA CPU works.

## Read the code in this order

1. In [`first_program.py`](../../simulator/first_program.py), inspect the four encoded words and the printed trace.
2. In [`cpu.py`](../../simulator/cpu.py), follow `step()`: fetch the word at `PC / 4`, decode fields, execute one operation, then advance the PC by four unless `HALT` stops it.
3. In [`test_cpu.py`](../../simulator/test_cpu.py), compare each expected result with the ISA reference.

The [next simulator slice](list-sum.md) adds data RAM, counted control flow, and a small assembler to run a list-summing program. The board memory map remains a separate design decision.
