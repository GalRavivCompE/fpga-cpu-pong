# Running an ISA program in Python

**Status: assembled and executed in the Python model only.** This is not RTL or an FPGA result. The simulator currently supports 12 of the 30 candidate instructions: `SET_LOW`, `SET_HIGH`, `DUPE`, `ADD`, `ADD_CONST`, `READ`, `READ_BYTE`, `WRITE`, `IF_EQ`, `GHOST`, `REPEAT`, and `HALT`.

Run from the repository root:

```sh
python3 simulator/list_sum.py
python3 -m unittest discover -s simulator -v
```

The [assembly program](../../simulator/list_sum.asm) sums a length-prefixed list. The Python demo loads `[7, 12, 5]` into simulated data RAM: address 256 holds length 3, and addresses 260, 264, and 268 hold the values. The CPU executes `READ` and `ADD` inside a loop and halts with 24 in R1. The tests also run empty and one-item lists and check 32-bit overflow.

The demo's `write_word()` calls **set up RAM before execution**. They are analogous to loading initialized data, not instructions executed by the CPU. The `WRITE` instruction is implemented separately and tested with a small program. The simulated RAM is a 1,024-byte Python `bytearray`; this size and address range are provisional simulator choices, not a board memory map.

## How the pieces fit

1. [`assembler.py`](../../simulator/assembler.py) reads the assembly text. Its first pass records label positions; its second pass converts instructions into 32-bit words. For `GHOST done`, it calculates how many following instructions to skip. For `REPEAT loop`, it calculates how many instructions to move backward.
2. [`list_sum.py`](../../simulator/list_sum.py) loads data into RAM and gives the assembled program to `CPU`.
3. [`cpu.py`](../../simulator/cpu.py) fetches an instruction using the byte PC, decodes fields, and performs one operation. Data RAM is separate from program memory. Word accesses use aligned byte addresses; `READ_BYTE` can use any valid byte address.
4. [`test_list_sum.py`](../../simulator/test_list_sum.py) checks the loop, wraparound, byte order, and an invalid word address.

Only Python's standard library is used: `pathlib.Path` reads the `.asm` file, and `unittest` runs tests. `bytearray`, `int.from_bytes()`, and `int.to_bytes()` are built into Python. The assembler imports no library. `from cpu import CPU` and `from assembler import assemble` import our own neighboring files.

The next step is to run **a program you write** through this simulator, then extend instructions or diagnostics based on what that program needs. The HDL CPU can later execute the same encoded words and compare results against this Python model.
