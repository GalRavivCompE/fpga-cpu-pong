# Instruction set reference (draft)

**Status: designed, not implemented or verified.** The operations below are the current candidate v1 ISA. Mnemonics and behavior have been reviewed; **binary opcode IDs and field positions have not been assigned**. An entry here does not mean the instruction runs in simulation or on an FPGA. See the [example programs](examples.md), [decision log](../project/decisions.md), and [ISA comparisons](comparisons.md) for context.

## Machine and notation

- The current candidate has eight writable 32-bit registers named `A` through `H`; 16 registers remain an open alternative. `dst` is a register receiving a result; `src`, `src1`, and `src2` are source registers. All source values are read before a destination is written, so `ADD A, A, B` is valid.
- The program counter (`PC`) and memory addresses are numeric **byte addresses**. Each instruction is 32 bits, at an address divisible by four. Program and data memory are separate logical spaces. Normal execution advances the PC by four bytes.
- `[B]` means the 32-bit data word at the numeric address **held in register B**. It does not mean the value of B itself. Word transfers require addresses divisible by four.
- `N` is a fixed unsigned count of machine instructions encoded in an instruction, not a register or a count of assembly source lines. Labels may let a future assembler calculate `N`. The draft count range is 0–65535. `imm16` is a 16-bit value embedded in an instruction.
- Arithmetic keeps the low 32 bits where noted. Signed values use two's complement. There are no stored comparison flags. `HALT` means successful stop, `FAIL` means a program-reported failure, and invalid operations stop with a distinct hardware fault. Exact binary encoding remains open.

## Instruction index

| Values and arithmetic | Logic and shifts | Memory and control |
| --- | --- | --- |
| [SET_LOW](#set_low), [SET_HIGH](#set_high), [DUPE](#dupe) | [AND](#and), [OR](#or), [XOR](#xor), [NOT](#not) | [READ](#read), [WRITE](#write) |
| [ADD](#add), [SUB](#sub), [MUL](#mul) | [LSHIFT](#lshift), [RSHIFT](#rshift), [RSHIFT_SIGN](#rshift_sign) | [IF_EQ](#if_eq), [IF_NE](#if_ne), [IF_GT](#if_gt), [IF_UGT](#if_ugt) |
| [DIV](#div), [MOD](#mod), [ADD_CONST](#add_const) | | [GHOST](#ghost), [REPEAT](#repeat), [LEAP](#leap), [CALL](#call), [COUNT](#count), [HALT](#halt), [FAIL](#fail) |

All opcode IDs below are **TBD**. Assigning an ID is part of the next encoding design step.

## Values and arithmetic

### SET_LOW

**Opcode ID:** TBD  
**Syntax:** `SET_LOW dst, imm16`  
**Effect:** Replace bits 15:0 of `dst` with `imm16`; preserve bits 31:16. It does **not** sign extend. If A was `0x12340000`, `SET_LOW A, 5` makes it `0x12340005`.

### SET_HIGH

**Opcode ID:** TBD  
**Syntax:** `SET_HIGH dst, imm16`  
**Effect:** Replace bits 31:16 of `dst` with `imm16`; preserve bits 15:0. Use both half-setting instructions to construct any 32-bit constant when the old register contents are unknown.

### DUPE

**Opcode ID:** TBD  
**Syntax:** `DUPE dst, src`  
**Effect:** Copy all 32 bits from `src` into `dst` without changing `src`. This copies a register; it does not access memory.

### ADD

**Opcode ID:** TBD  
**Syntax:** `ADD dst, src1, src2`  
**Effect:** `dst = (src1 + src2) mod 2^32`.

### SUB

**Opcode ID:** TBD  
**Syntax:** `SUB dst, src1, src2`  
**Effect:** `dst = (src1 - src2) mod 2^32`.

### MUL

**Opcode ID:** TBD  
**Syntax:** `MUL dst, src1, src2`  
**Effect:** Write the low 32 bits of the product. This is multiplication modulo `2^32`.

### DIV

**Opcode ID:** TBD  
**Syntax:** `DIV dst, src1, src2`  
**Effect:** Signed division, with the quotient truncated toward zero. For example, `-7 / 2` gives `-3`. A zero divisor causes a hardware fault and does not write `dst`. The exceptional `-2147483648 / -1` result is `0x80000000`.

### MOD

**Opcode ID:** TBD  
**Syntax:** `MOD dst, src1, src2`  
**Effect:** Signed remainder consistent with `DIV`: `src1 = quotient × src2 + remainder`. Thus `-7 MOD 2` gives `-1`. A zero divisor faults without writing `dst`; `-2147483648 MOD -1` gives zero.

### ADD_CONST

**Opcode ID:** TBD  
**Syntax:** `ADD_CONST dst, src1, signed_imm16`  
**Effect:** Sign extend the embedded 16-bit number and add it to `src1`, keeping the low 32 bits. `ADD_CONST B, B, 4` advances a word address; `ADD_CONST B, B, -1` decrements a value.

## Logic and shifts

### AND

**Opcode ID:** TBD  
**Syntax:** `AND dst, src1, src2`  
**Effect:** Bitwise AND across all 32 bit positions. Useful for selecting input bits with a mask.

### OR

**Opcode ID:** TBD  
**Syntax:** `OR dst, src1, src2`  
**Effect:** Bitwise OR across all 32 bit positions.

### XOR

**Opcode ID:** TBD  
**Syntax:** `XOR dst, src1, src2`  
**Effect:** Bitwise exclusive OR across all 32 bit positions.

### NOT

**Opcode ID:** TBD  
**Syntax:** `NOT dst, src`  
**Effect:** Flip every bit of `src`. This is a bitwise operation, not a zero/nonzero Boolean test.

### LSHIFT

**Opcode ID:** TBD  
**Syntax:** `LSHIFT dst, src1, src2`

**Effect:** Shift the 32-bit value in `src1` left by the unsigned distance in `src2`. Discard bits shifted past the top; fill from the right with zeros. A distance of zero copies `src1`; a distance of 32 or more gives zero. For example, if B is 3 and C is 2, `LSHIFT A, B, C` gives A = 12.

### RSHIFT

**Opcode ID:** TBD  
**Syntax:** `RSHIFT dst, src1, src2`

**Effect:** Shift the 32-bit value in `src1` right by the unsigned distance in `src2`. Discard bits shifted past the bottom; fill from the left with zeros. A distance of zero copies `src1`; a distance of 32 or more gives zero. This treats the source as an unsigned bit pattern.

### RSHIFT_SIGN

**Opcode ID:** TBD  
**Syntax:** `RSHIFT_SIGN dst, src1, src2`

**Effect:** Shift the 32-bit value in `src1` right by the unsigned distance in `src2`, copying the old top bit into the newly opened positions. A distance of zero copies `src1`; a distance of 32 or more gives all zeros if the old top bit was zero, or all ones if it was one. This is arithmetic right shift of a two's-complement value.

## Memory

### READ

**Opcode ID:** TBD  
**Syntax:** `READ dst, [address_reg]`  
**Effect:** Read one 32-bit word from data memory or a mapped input register at the numeric byte address held in `address_reg`. For example, if B contains 256, `READ A, [B]` reads data address 256 into A. Misaligned or unmapped addresses cause a hardware fault.

### WRITE

**Opcode ID:** TBD  
**Syntax:** `WRITE src, [address_reg]`  
**Effect:** Write all 32 bits of `src` to data memory or a mapped output register at the numeric byte address held in `address_reg`. Misaligned or unmapped addresses cause a hardware fault.

## Conditions and control flow

Each `IF_*` instruction has syntax `IF_* src1, src2, N`. If its comparison is true, execution continues at `PC+4`. If false, it skips the **next N encoded instructions** and continues at `PC+4×(N+1)`. `N=0` advances normally. An `IF_*` can control a `GHOST` instruction; a true condition does not prevent control flow within its block.

### IF_EQ

**Opcode ID:** TBD  
**Syntax:** `IF_EQ src1, src2, N`  
**Condition:** The two 32-bit values are equal. Signedness does not matter.

### IF_NE

**Opcode ID:** TBD  
**Syntax:** `IF_NE src1, src2, N`  
**Condition:** The two 32-bit values are unequal. Signedness does not matter.

### IF_GT

**Opcode ID:** TBD  
**Syntax:** `IF_GT src1, src2, N`  
**Condition:** `src1` is greater than `src2` when both are interpreted as signed two's-complement numbers. Swap operands to test less-than.

### IF_UGT

**Opcode ID:** TBD  
**Syntax:** `IF_UGT src1, src2, N`  
**Condition:** `src1` is greater than `src2` when both are interpreted as unsigned 32-bit numbers. Useful for addresses and detecting unsigned wraparound.

### GHOST

**Opcode ID:** TBD  
**Syntax:** `GHOST N`  
**Effect:** Unconditionally skip the next `N` encoded instructions: new `PC = old PC+4×(N+1)`. `GHOST 0` simply advances and serves as a no-op. A label such as `GHOST done` would be converted to a count by an assembler.

### REPEAT

**Opcode ID:** TBD  
**Syntax:** `REPEAT N`  
**Effect:** Jump backward by `N` encoded instructions from the current instruction: new `PC = old PC-4×N`. `N` must be at least one. A label such as `REPEAT loop` would be converted to a count by an assembler.

### LEAP

**Opcode ID:** TBD  
**Syntax:** `LEAP target_reg`  
**Effect:** Set `PC` to the numeric program address in `target_reg`. The address must be valid and aligned. This can jump forward or backward; it can also return from a function using a saved link value.

### CALL

**Opcode ID:** TBD  
**Syntax:** `CALL target_reg, link_reg`  
**Effect:** Read the old target value, store `old PC+4` in `link_reg`, then set `PC` to the target. Return with `LEAP link_reg`. A nested call must save its incoming link value, for example in data memory. The target must be valid and aligned.

### COUNT

**Opcode ID:** TBD

**Syntax:** `COUNT dst`

**Effect:** Copy the **current instruction's byte address** (the PC before its normal advance) into `dst`, then continue at the next instruction. For example, `COUNT A` executing at program byte address 40 makes A = 40, not 10 or 44. The name refers to the program counter; it is not an elapsed-instruction or clock-cycle counter.

### HALT

**Opcode ID:** TBD  
**Syntax:** `HALT`  
**Effect:** Stop normal execution with a successful completion status.

### FAIL

**Opcode ID:** TBD  
**Syntax:** `FAIL`  
**Effect:** Stop normal execution with a program-reported failure status. This is distinct from an automatic hardware fault such as an invalid opcode, bad address, or division by zero.

## Example programs and related decisions

The [examples](examples.md) show a list-summing loop and a button-to-output program. Both are **assembly sketches**, not assembled or tested programs. See the [comparisons](comparisons.md) for design tradeoffs against Astro8 and RISC-V.
