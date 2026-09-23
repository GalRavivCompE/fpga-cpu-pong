# Draft ISA gap audit against RISC-V RV32I

This is an earlier comparison snapshot. The [complete candidate ISA](isa-complete-draft.md) is the current proposal; this audit preserves the questions that led to it.

**Status:** Historical analysis snapshot, 2026-09-22. No CPU, assembler, or instruction encoding has been implemented or verified. This compares the earlier working ideas with the RISC-V **base integer** ISA (RV32I), not every optional RISC-V extension. A missing RV32I feature is not automatically a project requirement.

Primary reference: [RISC-V RV32I specification](https://docs.riscv.org/reference/isa/v20240411/unpriv/rv32.html). The [RISC-V introduction](https://docs.riscv.org/reference/isa/v20240411/unpriv/intro.html) describes its address space and optional extensions.

## What the earlier draft covered or proposed

| Area | Earlier draft | RV32I comparison | Status |
| --- | --- | --- | --- |
| Basic machine state | Eight 32-bit general registers; PC implied | 32 registers, including a hardwired zero register; PC | Register count provisional; PC reset and exact behavior open |
| Arithmetic | Three-operand `ADD`/`SUB`, modulo 2^32; two-operand shorthand discussed | Three-operand `ADD`/`SUB`, low 32 bits retained | Operation discussed; exact formats and shorthand open |
| Bitwise operations | Direct bitwise `NOT`; `AND`/`OR` suggested | `AND`/`OR`/`XOR`; NOT is an assembler alias for `XORI -1` | NOT provisional; AND/OR not yet precise |
| Constants | Small immediate plus an upper-half operation | Small immediates plus `LUI` | Structure provisional; exact sign/zero extension open |
| Memory | Byte addresses; aligned 32-bit loads/stores; separate register and base-plus-offset forms | Byte-addressed loads/stores with offsets; word, halfword, and byte sizes | Provisional; offset encoding, misalignment, and data map open |
| Control flow | `IF_EQ src1,src2,N` skips N instructions on false; `GHOST N` skips forward; `REPEAT N` jumps backward | Conditional branches and PC-relative/register-target jumps | Provisional; ranges, edge cases, and other conditions open |
| Code/data spaces | Separate logical instruction and data spaces | One byte-addressed ISA address space | Provisional platform/ISA boundary choice |

The clearest distinctive features are counted conditional blocks, explicit forward and backward skip/jump operations, eight general registers, a dedicated NOT instruction, and separate logical instruction/data spaces. Different names alone would not make a useful architectural difference.

## Gaps to resolve before a first ISA version

| Gap | Why it matters | Viable options | Working recommendation to evaluate |
| --- | --- | --- | --- |
| Exact constant construction | A program must initialize pointers, counters, and masks | Sign-extend a small immediate then replace the upper half; zero-extend then replace upper half; use a data constant table | Sign-extend small values for convenient -1/0/1, with an upper-half replacement instruction for any 32-bit pattern |
| Arithmetic with constants | Advancing a pointer by 4 or decrementing a count should be easy to write | Add/subtract immediate instructions; preload constants in registers; assembler macros expanding to several instructions | Consider one `ADD_IMM`; compare program length and encoding cost first |
| Conditions | Equality, inequality, and signed greater-than were proposed; only `IF_EQ` is specified | Direct `IF_NE`/`IF_GT`; synthesize conditions from fewer primitives; use condition flags | Sketch all three direct forms, then check encoding and RTL cost |
| Bit manipulation | Buttons and peripheral registers often pack fields into bits | Add `AND`/`OR`/`XOR` and shifts; synthesize some in software | `AND` is important for button masks; decide OR/XOR/shifts from sample programs |
| Program completion and invalid instructions | A board self-check needs an observable finish/failure | `HALT` plus status; loop forever and write a status register; trap mechanism | A small `HALT`/error behavior seems useful for simulation and board bring-up |
| Precise PC rules | `IF_EQ`, `GHOST`, and `REPEAT` must agree on what N counts and where execution resumes | Define counts relative to current instruction or following instruction; define N=0 and out-of-range targets | Specify PC equations and edge cases before RTL |
| Alignment and address errors | A 32-bit load at address 101 spans a word boundary | Stop/report error; support misaligned access in hardware; ignore low address bits | Stop/report error rather than silently access the wrong location |

## Broader general-purpose features to consider after the first demo

| Feature | Why it matters | Options |
| --- | --- | --- |
| Reusable functions and returns | `GHOST` and `REPEAT` use fixed forward/backward distances; they do not naturally return to different callers | **Provisional choice after this audit:** register-target jump plus call that saves return PC in a chosen register. Encoding and implementation remain open |
| Byte and halfword data | Text, packed structures, and many devices benefit from smaller accesses | Add load/store byte and halfword; keep word-only v1 and let devices use word-sized registers |
| Unsigned comparison | Addresses, sizes, and bit patterns may occupy the upper half of 32-bit space | Direct unsigned condition; derive from other operations; defer if first programs avoid it |
| Multiply/divide | Speeds up some algorithms; Pong can use addition/subtraction and shifts | Implement hardware instructions; software subroutines; defer. RISC-V places these in its optional M extension |
| Exceptions, interrupts, and memory ordering | Useful for larger systems and asynchronous devices | Poll I/O initially; add a minimal trap/interrupt scheme later; memory fences only if the memory system requires them |

## Next learning exercise

A short list-sum program now appears in the [complete candidate ISA](isa-complete-draft.md). A button-input loop remains to be drafted. These programs should expose undefined behavior or awkward missing operations before opcode bits are assigned.
