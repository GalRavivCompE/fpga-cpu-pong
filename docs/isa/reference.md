# Instruction set reference (draft)

**Status: encoded on paper, not implemented or verified.** The operations below are the current candidate v1 ISA. Six-bit opcode IDs and field positions are assigned, but no assembler, simulator test, or FPGA implementation exists. An entry here does not mean the instruction runs. See the [example programs](examples.md), [decision log](../project/decisions.md), and [ISA comparisons](comparisons.md) for context.

## Machine and notation

- Five-bit register codes name `R0`–`R31`. `R0` always reads as 32-bit zero; a write to `R0` discards the result. `R1`–`R31` are writable 32-bit registers. `dst` is a register receiving a result; `src`, `src1`, and `src2` are source registers. All source values are read before a destination is written, so `ADD R1, R1, R2` is valid. The choice of storage circuit for the 31 writable registers remains an implementation decision.
- The program counter (`PC`) and memory addresses are numeric **byte addresses**. Each instruction is 32 bits, at an address divisible by four. Program and data memory are separate logical spaces. Normal execution advances the PC by four bytes.
- `[R2]` means the data at the numeric address **held in register R2**. It does not mean the value of R2 itself. `READ` and `WRITE` transfer 32-bit words and require addresses divisible by four; `READ_BYTE` transfers one byte and accepts any valid byte address. Within a word, the lowest address holds bits 7:0 (little-endian order).
- `N` is a fixed unsigned count of machine instructions encoded in an instruction, not a register or a count of assembly source lines. Labels may let a future assembler calculate `N`. Its encoded range is 0–65535, although `REPEAT` requires at least one. `imm16` is a 16-bit value embedded in an instruction.
- Arithmetic keeps the low 32 bits where noted. Signed values use two's complement. There are no stored comparison flags. `HALT` means successful stop, `FAIL` means a program-reported failure, and invalid operations stop with a distinct hardware fault.

## Instruction index

| Values and arithmetic | Logic and shifts | Memory and control |
| --- | --- | --- |
| [SET_LOW](#set_low), [SET_HIGH](#set_high), [DUPE](#dupe) | [AND](#and), [OR](#or), [XOR](#xor), [NOT](#not) | [READ](#read), [READ_BYTE](#read_byte), [WRITE](#write) |
| [ADD](#add), [SUB](#sub), [MUL](#mul) | [LSHIFT](#lshift), [RSHIFT](#rshift), [RSHIFT_SIGN](#rshift_sign) | [IF_EQ](#if_eq), [IF_NE](#if_ne), [IF_GT](#if_gt), [IF_UGT](#if_ugt) |
| [DIV](#div), [MOD](#mod), [ADD_CONST](#add_const) | | [GHOST](#ghost), [REPEAT](#repeat), [LEAP](#leap), [CALL](#call), [COUNT](#count), [HALT](#halt), [FAIL](#fail) |

## Binary encoding (candidate v1)

Every instruction is one 32-bit word. Bits 31:26 always hold a six-bit opcode. The opcode selects one of these layouts; unused bits **must be zero**, or the instruction faults. The operand field names below describe positions, not fixed hardware roles: for example, `WRITE` puts its source register in the first field.

| Layout | Fields below the opcode, from high bits to low bits | Instructions |
| --- | --- | --- |
| Three registers | 25:21 `dst`; 20:16 `src1`; 15:11 `src2`; 10:0 zero | Register arithmetic, logic, shifts |
| Two registers | 25:21 first operand; 20:16 second operand; 15:0 zero | `DUPE`, `NOT`, `READ`, `READ_BYTE`, `WRITE`, `CALL` |
| One register | 25:21 operand; 20:0 zero | `LEAP`, `COUNT` |
| Two registers + 16-bit value | 25:21 first operand; 20:16 second operand; 15:0 value | `ADD_CONST`, `IF_*` |
| One register + 16-bit value | 25:21 `dst`; 20:16 zero; 15:0 value | `SET_LOW`, `SET_HIGH` |
| 16-bit value only | 25:16 zero; 15:0 count | `GHOST`, `REPEAT` |
| No operands | 25:0 zero | `HALT`, `FAIL` |

For the two-register layout, bits 15:0 are zero. In layouts with a 16-bit value, bits 15:0 hold that value instead; the third-register field therefore overlaps the value field across different layouts. `ADD_CONST` sign-extends its 16-bit value, while `IF_*`, `GHOST`, and `REPEAT` treat theirs as unsigned counts. Opcode `0x00` is invalid, so an all-zero instruction word faults instead of silently acting as a no-op.

For example, `ADD R1, R2, R3` is `0x10221800`: opcode `0x04` in bits 31:26, R1=`1` in 25:21, R2=`2` in 20:16, and R3=`3` in 15:11. `IF_EQ R1, R0, 2` is `0xA0200002`: opcode `0x28`, R1=`1`, R0=`0`, count=`2`. These are instruction **words**; how a future ROM image serializes words into bytes remains to be specified.

Opcode IDs are grouped by purpose for readability. The grouping does not add hidden operations or change the fixed field positions. Unassigned codes, including `0x00`, fault in v1.

| Opcode | Instructions |
| --- | --- |
| `0x01`–`0x09` | `SET_LOW`, `SET_HIGH`, `DUPE`, `ADD`, `SUB`, `MUL`, `DIV`, `MOD`, `ADD_CONST` |
| `0x10`–`0x16` | `AND`, `OR`, `XOR`, `NOT`, `LSHIFT`, `RSHIFT`, `RSHIFT_SIGN` |
| `0x20`–`0x22` | `READ`, `READ_BYTE`, `WRITE` |
| `0x28`–`0x2B` | `IF_EQ`, `IF_NE`, `IF_GT`, `IF_UGT` |
| `0x30`–`0x36` | `GHOST`, `REPEAT`, `LEAP`, `CALL`, `COUNT`, `HALT`, `FAIL` |

Within each row, instruction names correspond to opcode values in ascending order. For example, `ADD` is `0x04` and `READ_BYTE` is `0x21`. The gaps are reserved for future versions, not aliases.

## Values and arithmetic

### SET_LOW

**Opcode ID:** `0x01`\
**Syntax:** `SET_LOW dst, imm16`  
**Effect:** Replace bits 15:0 of `dst` with `imm16`; preserve bits 31:16. It does **not** sign extend. If R1 was `0x12340000`, `SET_LOW R1, 5` makes it `0x12340005`.

### SET_HIGH

**Opcode ID:** `0x02`\
**Syntax:** `SET_HIGH dst, imm16`  
**Effect:** Replace bits 31:16 of `dst` with `imm16`; preserve bits 15:0. Use both half-setting instructions to construct any 32-bit constant when the old register contents are unknown.

### DUPE

**Opcode ID:** `0x03`\
**Syntax:** `DUPE dst, src`  
**Effect:** Copy all 32 bits from `src` into `dst` without changing `src`. This copies a register; it does not access memory.

### ADD

**Opcode ID:** `0x04`\
**Syntax:** `ADD dst, src1, src2`  
**Effect:** `dst = (src1 + src2) mod 2^32`.

### SUB

**Opcode ID:** `0x05`\
**Syntax:** `SUB dst, src1, src2`  
**Effect:** `dst = (src1 - src2) mod 2^32`.

### MUL

**Opcode ID:** `0x06`\
**Syntax:** `MUL dst, src1, src2`  
**Effect:** Write the low 32 bits of the product. This is multiplication modulo `2^32`.

### DIV

**Opcode ID:** `0x07`\
**Syntax:** `DIV dst, src1, src2`  
**Effect:** Signed division, with the quotient truncated toward zero. For example, `-7 / 2` gives `-3`. A zero divisor causes a hardware fault and does not write `dst`. The exceptional `-2147483648 / -1` result is `0x80000000`.

### MOD

**Opcode ID:** `0x08`\
**Syntax:** `MOD dst, src1, src2`  
**Effect:** Signed remainder consistent with `DIV`: `src1 = quotient × src2 + remainder`. Thus `-7 MOD 2` gives `-1`. A zero divisor faults without writing `dst`; `-2147483648 MOD -1` gives zero.

### ADD_CONST

**Opcode ID:** `0x09`\
**Syntax:** `ADD_CONST dst, src1, signed_imm16`  
**Effect:** Sign extend the embedded 16-bit number and add it to `src1`, keeping the low 32 bits. `ADD_CONST R2, R2, 4` advances a word address; `ADD_CONST R2, R2, -1` decrements a value.

## Logic and shifts

### AND

**Opcode ID:** `0x10`\
**Syntax:** `AND dst, src1, src2`  
**Effect:** Bitwise AND across all 32 bit positions. Useful for selecting input bits with a mask.

### OR

**Opcode ID:** `0x11`\
**Syntax:** `OR dst, src1, src2`  
**Effect:** Bitwise OR across all 32 bit positions.

### XOR

**Opcode ID:** `0x12`\
**Syntax:** `XOR dst, src1, src2`  
**Effect:** Bitwise exclusive OR across all 32 bit positions.

### NOT

**Opcode ID:** `0x13`\
**Syntax:** `NOT dst, src`  
**Effect:** Flip every bit of `src`. This is a bitwise operation, not a zero/nonzero Boolean test.

### LSHIFT

**Opcode ID:** `0x14`\
**Syntax:** `LSHIFT dst, src1, src2`

**Effect:** Shift the 32-bit value in `src1` left by the unsigned distance in `src2`. Discard bits shifted past the top; fill from the right with zeros. A distance of zero copies `src1`; a distance of 32 or more gives zero. For example, if R2 is 3 and R3 is 2, `LSHIFT R1, R2, R3` gives R1 = 12.

### RSHIFT

**Opcode ID:** `0x15`\
**Syntax:** `RSHIFT dst, src1, src2`

**Effect:** Shift the 32-bit value in `src1` right by the unsigned distance in `src2`. Discard bits shifted past the bottom; fill from the left with zeros. A distance of zero copies `src1`; a distance of 32 or more gives zero. This treats the source as an unsigned bit pattern.

### RSHIFT_SIGN

**Opcode ID:** `0x16`\
**Syntax:** `RSHIFT_SIGN dst, src1, src2`

**Effect:** Shift the 32-bit value in `src1` right by the unsigned distance in `src2`, copying the old top bit into the newly opened positions. A distance of zero copies `src1`; a distance of 32 or more gives all zeros if the old top bit was zero, or all ones if it was one. This is arithmetic right shift of a two's-complement value.

## Memory

### READ

**Opcode ID:** `0x20`\
**Syntax:** `READ dst, [address_reg]`  
**Effect:** Read one 32-bit word from data memory or a mapped input register at the numeric byte address held in `address_reg`. For example, if R2 contains 256, `READ R1, [R2]` reads data address 256 into R1. Misaligned or unmapped addresses cause a hardware fault.

### READ_BYTE

**Opcode ID:** `0x21`

**Syntax:** `READ_BYTE dst, [address_reg]`

**Effect:** Read one 8-bit value from the numeric data-memory byte address held in `address_reg`, then zero-extend it to 32 bits in `dst`. Any valid byte address is allowed; alignment to four is not required. For example, if a word at address 256 is `0x44332211`, `READ_BYTE R1, [R2]` with R2 = 257 sets R1 to `0x00000022`. A byte read from a mapped peripheral is valid only if that peripheral's memory-map specification supports it; otherwise it faults. An unmapped address also faults. This instruction does not modify memory.

### WRITE

**Opcode ID:** `0x22`\
**Syntax:** `WRITE src, [address_reg]`  
**Effect:** Write all 32 bits of `src` to data memory or a mapped output register at the numeric byte address held in `address_reg`. Misaligned or unmapped addresses cause a hardware fault.

## Conditions and control flow

Each `IF_*` instruction has syntax `IF_* src1, src2, N`. If its comparison is true, execution continues at `PC+4`. If false, it skips the **next N encoded instructions** and continues at `PC+4×(N+1)`. `N=0` advances normally. An `IF_*` can control a `GHOST` instruction; a true condition does not prevent control flow within its block.

### IF_EQ

**Opcode ID:** `0x28`\
**Syntax:** `IF_EQ src1, src2, N`  
**Condition:** The two 32-bit values are equal. Signedness does not matter.

### IF_NE

**Opcode ID:** `0x29`\
**Syntax:** `IF_NE src1, src2, N`  
**Condition:** The two 32-bit values are unequal. Signedness does not matter.

### IF_GT

**Opcode ID:** `0x2A`\
**Syntax:** `IF_GT src1, src2, N`  
**Condition:** `src1` is greater than `src2` when both are interpreted as signed two's-complement numbers. Swap operands to test less-than.

### IF_UGT

**Opcode ID:** `0x2B`\
**Syntax:** `IF_UGT src1, src2, N`  
**Condition:** `src1` is greater than `src2` when both are interpreted as unsigned 32-bit numbers. Useful for addresses and detecting unsigned wraparound.

### GHOST

**Opcode ID:** `0x30`\
**Syntax:** `GHOST N`  
**Effect:** Unconditionally skip the next `N` encoded instructions: new `PC = old PC+4×(N+1)`. `GHOST 0` simply advances and serves as a no-op. A label such as `GHOST done` would be converted to a count by an assembler.

### REPEAT

**Opcode ID:** `0x31`\
**Syntax:** `REPEAT N`  
**Effect:** Jump backward by `N` encoded instructions from the current instruction: new `PC = old PC-4×N`. `N` must be at least one. A label such as `REPEAT loop` would be converted to a count by an assembler.

### LEAP

**Opcode ID:** `0x32`\
**Syntax:** `LEAP target_reg`  
**Effect:** Set `PC` to the numeric program address in `target_reg`. The address must be valid and aligned. This can jump forward or backward; it can also return from a function using a saved link value.

### CALL

**Opcode ID:** `0x33`\
**Syntax:** `CALL target_reg, link_reg`  
**Effect:** Read the old target value, store `old PC+4` in `link_reg`, then set `PC` to the target. Return with `LEAP link_reg`. A nested call must save its incoming link value, for example in data memory. The target must be valid and aligned.

### COUNT

**Opcode ID:** `0x34`

**Syntax:** `COUNT dst`

**Effect:** Copy the **current instruction's byte address** (the PC before its normal advance) into `dst`, then continue at the next instruction. For example, `COUNT R1` executing at program byte address 40 makes R1 = 40, not 10 or 44. The name refers to the program counter; it is not an elapsed-instruction or clock-cycle counter.

### HALT

**Opcode ID:** `0x35`\
**Syntax:** `HALT`  
**Effect:** Stop normal execution with a successful completion status.

### FAIL

**Opcode ID:** `0x36`\
**Syntax:** `FAIL`  
**Effect:** Stop normal execution with a program-reported failure status. This is distinct from an automatic hardware fault such as an invalid opcode, bad address, or division by zero.

## Example programs and related decisions

The [examples](examples.md) show a list-summing loop and a button-to-output program. Both are **assembly sketches**, not assembled or tested programs. See the [comparisons](comparisons.md) for design tradeoffs against Astro8 and RISC-V.
