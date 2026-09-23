# Complete candidate ISA, revision 0.1

For an indexed, instruction-by-instruction view with syntax and behavior, see the [instruction set reference](isa-reference.md). This document retains the design rationale and example programs.

**Status: proposed version 1 design for review, not a finalized or working ISA.** Prepared 2026-09-22 and revised during section review. Nothing here has been encoded, assembled, simulated, or run on an FPGA. The [decision log](decisions.md) distinguishes provisional instructions from features deliberately excluded from version 1. A later version can change the scope explicitly.

The goal is a small, general-purpose 32-bit CPU that is approachable to implement on an FPGA and pleasant enough to program by hand. Instruction names here describe behavior; final distinctive names can be chosen after semantics are stable. Inspiration and comparison: [RISC-V RV32I](https://docs.riscv.org/reference/isa/v20240411/unpriv/rv32.html) and [Astro8](https://sam-astro.github.io/Astro8-Computer/docs/Architecture/Instruction%20Set.html). Similar basic arithmetic is useful; counted conditional blocks, `GHOST`, `REPEAT`, eight writable registers, and separate program/data spaces make this design meaningfully different.

## Programmer-visible machine

- Eight writable 32-bit registers named `A`–`H`; no hardwired zero register. These letters select registers; they are not memory addresses. Reset clears them and sets the 32-bit program counter (PC) to byte address 0. Any register can hold a number, address, or bit pattern; there are no type tags.
- Every instruction is one 32-bit word. Program addresses are byte addresses and must be multiples of four. Normal execution advances `PC` by 4. Program fetch and data access have separate logical address spaces; a data load cannot read an instruction word.
- Data memory is byte addressed. A 32-bit word at numeric address `addr` occupies bytes `addr` through `addr+3`; the next aligned word begins at `addr+4`. Byte order within a word is not observable through v1's word-only transfers and is left for a future extension to define.
- `ADD`, `SUB`, `MUL`, and `ADD_CONST` keep the low 32 bits (modulo `2^32`). Signed comparisons interpret bit patterns as two's-complement values. No condition flags are stored.
- Instruction counts (`N`) are unsigned 16-bit values, 0–65535, unless stated otherwise. `imm16` is a 16-bit bit pattern; operations called *signed* sign-extend it to 32 bits. The assembler must reject operands outside the stated range instead of silently truncating them.

## Instruction set

Notation: `dst`, `src1`, `src2`, `src`, `target_reg`, and `link_reg` are **placeholders** for any of the named registers A–H. Brackets mean data memory at the numeric address held in a register: if B contains 256, `READ A, [B]` reads data address 256 into A; it does not copy B into A. The memory address is the number **inside B**, not the letter B. `PC=P` refers to the numeric program address of the instruction currently executing. A destination can also be a source: `ADD A, A, C` reads the old A and C before writing the result to A.

**Operand forms.** Binary register arithmetic (`ADD`, `SUB`, `MUL`, `DIV`, `MOD`) and binary bitwise logic (`AND`, `OR`, `XOR`) use `INSTRUCTION dst, src1, src2`. Both sources are read before `dst` is written, even if `dst` names one of the sources. `NOT` and the one-bit shifts use `INSTRUCTION dst, src1` because they have only one source. `ADD_CONST dst, src1, signed_imm16` uses a number encoded in the instruction instead of a second source register. Conditions use the explicit form `IF_* src1, src2, N`: they read two registers, and `N` is an instruction count, **not a third register**. There is no implicit-count two-operand form. `GHOST N` and `REPEAT N` encode numeric counts; assembler labels can resolve to those numbers. `GHOST` does not read a register count in v1.

| Group | Instructions | Meaning and reason to include |
| --- | --- | --- |
| Constants/copy | `SET_LOW dst, imm16`; `SET_HIGH dst, imm16`; `DUPE dst, src1` | `SET_LOW` replaces bits 15:0 and preserves bits 31:16. `SET_HIGH` replaces bits 31:16 and preserves bits 15:0. Together they build any 32-bit value regardless of the old register contents. `DUPE` copies a register without changing its source. Neither half-setting operation sign-extends. |
| Arithmetic | `ADD dst, src1, src2`; `SUB dst, src1, src2`; `MUL dst, src1, src2`; `DIV dst, src1, src2`; `MOD dst, src1, src2`; `ADD_CONST dst, src1, signed_imm16` | `ADD`, `SUB`, `MUL`, and `ADD_CONST` write the low 32 bits. `ADD_CONST` adds a signed 16-bit constant to a full 32-bit register value; for example, `ADD_CONST B, B, 4` advances a word pointer and `ADD_CONST C, C, -1` decrements a counter. `DIV` uses signed two's-complement operands and truncates toward zero (`-7 / 2 = -3`). `MOD` gives the corresponding signed remainder (`-7 MOD 2 = -1`). A zero divisor faults for either operation. `-2147483648 / -1` wraps to `0x80000000`, and the corresponding remainder is zero. |
| Bitwise | `AND dst, src1, src2`; `OR dst, src1, src2`; `XOR dst, src1, src2`; `NOT dst, src1` | Provisionally chosen as ordinary bitwise logic gates: each bit position is processed independently. Useful for packed data, masks, and input bits. `NOT` flips all 32 bits, not a Boolean value. |
| Shifts | `LSHIFT dst, src1`; `RSHIFT dst, src1`; `RSHIFT_SIGN dst, src1` | Move bits by exactly one position. `LSHIFT` fills the new low bit with zero. `RSHIFT` fills the new top bit with zero; `RSHIFT_SIGN` copies the old top bit into the new top bit. Repeat in software for larger distances. These names are selected; no variable shift amount is encoded. |
| Word memory | `READ dst, [src1]`; `WRITE src, [src1]` | Move aligned 32-bit words between registers and data memory/I/O. The address is the **number held in** `src1`; `src1` itself is a register name. For an offset address, calculate it in a register first; there is no separate offset opcode. |
| Conditional blocks | `IF_EQ src1, src2, N`; `IF_NE src1, src2, N`; `IF_GT src1, src2, N`; `IF_UGT src1, src2, N` | All four are provisionally chosen. If true, continue at `P+4`; if false, skip the *next N complete machine instructions* and continue at `P+4(N+1)`. `GT` uses signed order; `UGT` uses unsigned order. Swap operands to express less-than; combine a condition with `GHOST` for different block shapes. `N=0` has no observable effect. |
| Flow | `GHOST N`; `REPEAT N`; `LEAP target_reg`; `CALL target_reg, link_reg` | `GHOST` unconditionally skips N next instructions: `PC=P+4(N+1)`. `REPEAT` goes to `P-4N`; N must be at least 1. `LEAP` loads the PC from a register. `CALL` first reads the old target, then writes `P+4` to `link_reg`, then jumps to that target. Return with `LEAP link_reg`. The `LEAP` and `CALL` names have been selected. |
| Finish | `HALT`; `FAIL` | Stop with success or with a software-reported failure, respectively. Automatic hardware faults stop with their own cause status. `GHOST 0` serves as a no-op, so there is no separate `NOP` instruction. |

The half-setting instructions are symmetric. If A contains `0x12340000`, then `SET_LOW A, 5` makes A `0x12340005`; the upper half is preserved. `SET_HIGH A, 0xFFFF` then makes A `0xFFFF0005`. To set A to signed -1 (`0xFFFFFFFF`) from an unknown previous value, write `0xFFFF` with both `SET_LOW` and `SET_HIGH`.

**Counts and blocks.** `IF_*` controls exactly N following machine instructions, including any `GHOST` in that range. If the condition is false, none of those N instructions executes. A true `IF_*` does not force all N instructions to execute; control flow inside the block still works normally. This is why a one-instruction conditional block containing `GHOST` can exit a loop. `REPEAT` can revisit the conditional on every iteration. `GHOST 0` simply advances to the next instruction. Counts refer to encoded instructions, not source lines or macro invocations.

**Assembler conveniences, not extra opcodes.** A label can stand in for a `GHOST` destination or `REPEAT` destination; the assembler calculates the count. A block-end label can provide an `IF_*` count. `ADD dst, src2` may expand to `ADD dst, dst, src2`, and similarly for `SUB`. A future assembler could provide a full-constant shortcut that expands to `SET_LOW` and `SET_HIGH` with the appropriate 16-bit halves; both are needed when the destination's old value is unknown. It could also provide a fixed-address read shortcut with an explicit scratch register, expanding to `SET_LOW B, 256`, `SET_HIGH B, 0`, then `READ A, [B]`. These shortcuts are **not** separate CPU instructions in this draft. Expansions must be accounted for before branch counts are calculated. There is no special `RETURN` opcode: it is an alias for `LEAP link_reg` in a documented calling convention.

**Call convention proposal.** Use `G` as the usual link register, while retaining the ISA's ability to select another link register. A function that calls another function saves its incoming link value in data memory and restores it before returning. A fuller convention for argument, result, and stack registers waits until we write a nested-call example. If `target_reg` and `link_reg` name the same register, the old target is used for the jump before the link value overwrites it.

## Memory, I/O, and error behavior

- Reserve a high region of **data** addresses for memory-mapped peripheral registers. `READ` and `WRITE` read buttons and control LEDs or later video hardware through that region. Exact addresses and peripheral behavior are board/platform decisions, not instruction opcodes. Physical buttons need synchronization/debouncing in supporting hardware. The game rules, positions, collision response, and score updates run as CPU software.
- Version 1 has word loads/stores and word-sized I/O only. Byte and halfword transfers, base-plus-offset memory instructions, alternate left shifts, rotates, and continuing warnings are **excluded from v1**. Adding one requires an explicit future ISA revision.
- An invalid opcode, illegal reserved bit, misaligned instruction target or word access, unmapped data access, program address outside installed program memory, or a zero divisor in `DIV`/`MOD` stops execution with a hardware fault code distinguishable from both `HALT` and `FAIL`. An operation has no partial side effect on error. The simulator should report the failing PC and relevant address or divisor; the board may show a compact status on LEDs or serial output. Exact electrical status interface is implementation-specific.
- Polling input is sufficient for the first interactive game. Interrupts, traps, privilege levels, and memory fences are outside this proposed first ISA. `MUL` and `DIV` belong to the target ISA but can be implemented after the first board self-check if needed to keep the initial bring-up manageable.

## Does a 32-bit instruction fit?

Yes in principle. A 6-bit opcode supports up to 64 operations. Three register identifiers consume 9 bits, and a 16-bit immediate/count consumes 16 bits, leaving one bit (`6+9+16+1=32`). The table has fewer than 64 operation names. Different instructions use different subsets of those fields, and unused fields can be required to equal zero. The **exact bit layout and opcode numbers remain unassigned** pending review. A uniform format is convenient but not required. Fixed 32-bit instructions keep counted skips simple even though they are not compact in program memory.

## Example: sum a length-prefixed list

Data memory at address 256 contains a word holding the list length; elements follow at 260, 264, 268, and so on. This program starts immediately after reset, when all registers are zero. It leaves the sum in `A` and reserves `H=0` for the equality check. `ADD_CONST` avoids reserving two additional registers for the constants 4 and 1. A length prevents an element equal to a special sentinel from accidentally ending the list.

```text
SET_LOW A, 0            ; sum
SET_LOW H, 0            ; constant zero
SET_LOW B, 256          ; B holds a numeric data-memory address
READ C, [B]              ; read the word at data address 256
ADD_CONST B, B, 4         ; B now holds address 260
loop:
IF_EQ C, H, 1             ; when count is zero, execute the next GHOST
GHOST done               ; otherwise IF_EQ skips this instruction
READ D, [B]
ADD A, A, D
ADD_CONST B, B, 4
ADD_CONST C, C, -1
REPEAT loop               ; assembler computes backward count
done:
HALT
```

For a Pong-like program, the same pattern polls input with `READ`, updates position/velocity with arithmetic and conditionals, writes state to mapped output registers with `WRITE`, and uses `REPEAT` for the game loop. Dedicated hardware can generate video timing and draw from those state registers without executing game rules.

## Example: mirror one button to one output

The addresses below are **illustrative**, not a selected board's memory map. This program starts immediately after reset, when all registers are zero. Suppose hardware exposes button bits at data address `0xFFFF0000` and output bits at `0xFFFF0004`. `SET_LOW` and `SET_HIGH` build those 32-bit numbers in registers B and C. Bit 0 is isolated with `AND`, then written to the output. `REPEAT` polls continuously; this program does not reach `HALT` unless reset or a hardware fault stops it.

```text
SET_LOW B, 0
SET_HIGH B, 0xFFFF       ; B = numeric input address 0xFFFF0000
SET_LOW C, 4
SET_HIGH C, 0xFFFF       ; C = numeric output address 0xFFFF0004
SET_LOW D, 1           ; mask for button bit 0
loop:
READ A, [B]              ; hardware supplies current button bits
AND A, A, D              ; keep only bit 0
WRITE A, [C]             ; hardware receives output bit 0
REPEAT loop
```

This exercises input, output, masking, and a continuous software loop with the current ISA. It is an assembly sketch, not a simulated or board-tested program. Physical input synchronization and output electrical signals belong to supporting hardware; game rules remain CPU software.

## Review map

Review can proceed in a few larger passes: (1) core values/arithmetic, (2) memory and I/O, (3) conditions and control flow, (4) errors and extensions. For each pass, compare alternatives and decide **accept**, **change**, or **defer**. The next steps are binary encoding, a small assembler and reference simulator, and then RTL. No entry in this draft is *working* until it passes a reproducible test.
