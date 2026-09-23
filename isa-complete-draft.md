# Complete candidate ISA, revision 0.1

**Status: proposed design for review, not a finalized or working ISA.** Prepared 2026-09-22 and revised during section review. Nothing here has been encoded, assembled, simulated, or run on an FPGA. Earlier choices remain **provisional** in [decisions.md](decisions.md); additional instructions below are candidates for review. Each may be accepted, changed, or deferred.

The goal is a small, general-purpose 32-bit CPU that is approachable to implement on an FPGA and pleasant enough to program by hand. Instruction names here describe behavior; final distinctive names can be chosen after semantics are stable. Inspiration and comparison: [RISC-V RV32I](https://docs.riscv.org/reference/isa/v20240411/unpriv/rv32.html) and [Astro8](https://sam-astro.github.io/Astro8-Computer/docs/Architecture/Instruction%20Set.html). Similar basic arithmetic is useful; counted conditional blocks, `GHOST`, `REPEAT`, eight writable registers, and separate program/data spaces make this design meaningfully different.

## Programmer-visible machine

- Eight writable 32-bit registers named `A`–`H`; no hardwired zero register. These letters select registers; they are not memory addresses. Reset clears them and sets the 32-bit program counter (PC) to byte address 0. Any register can hold a number, address, or bit pattern; there are no type tags.
- Every instruction is one 32-bit word. Program addresses are byte addresses and must be multiples of four. Normal execution advances `PC` by 4. Program fetch and data access have separate logical address spaces; a data load cannot read an instruction word.
- Data memory is byte addressed. A 32-bit word at numeric address `addr` occupies bytes `addr` through `addr+3`; the next aligned word begins at `addr+4`. Byte order within a word is deferred until smaller transfers are designed.
- `ADD`, `SUB`, `MUL`, and `ADD_CONST` keep the low 32 bits (modulo `2^32`). Signed comparisons interpret bit patterns as two's-complement values. No condition flags are stored.
- Instruction counts (`N`) are unsigned 16-bit values, 0–65535, unless stated otherwise. `imm16` is a 16-bit bit pattern; operations called *signed* sign-extend it to 32 bits. The assembler must reject operands outside the stated range instead of silently truncating them.

## Instruction set

Notation: `dst`, `src1`, `src2`, `src`, `target_reg`, and `link_reg` are **placeholders** for any of the named registers A–H. Brackets mean data memory at the numeric address held in a register: if B contains 256, `LOAD A, [B]` reads data address 256 into A; it does not copy B into A. The memory address is the number **inside B**, not the letter B. `PC=P` refers to the numeric program address of the instruction currently executing. A destination can also be a source: `ADD A, A, C` reads the old A and C before writing the result to A.

| Group | Instructions | Meaning and reason to include |
| --- | --- | --- |
| Constants/copy | `SET_CONST dst, signed_imm16`; `SET_HIGH dst, imm16`; `MOVE dst, src1` | Load a signed 16-bit constant into a 32-bit register; replace bits 31:16 of `dst` while keeping bits 15:0; copy a register. The first two build any 32-bit value. `MOVE` is provisionally chosen as a direct instruction because copying a register is distinct from loading data memory. `SET_CONST` with `0xFFFF` produces `0xFFFFFFFF` (-1). |
| Arithmetic | `ADD dst, src1, src2`; `SUB dst, src1, src2`; `MUL dst, src1, src2`; `DIV dst, src1, src2`; `ADD_CONST dst, src1, signed_imm16` | `ADD`, `SUB`, `MUL`, and `ADD_CONST` write the low 32 bits. `ADD_CONST` adds a signed 16-bit constant to a full 32-bit register value; for example, `ADD_CONST B, B, 4` advances a word pointer and `ADD_CONST C, C, -1` decrements a counter. `DIV` uses signed two's-complement operands and truncates toward zero (`-7 / 2 = -3`). Division by zero causes a hardware fault. `-2147483648 / -1` wraps to `0x80000000`. |
| Bitwise | `AND dst, src1, src2`; `OR dst, src1, src2`; `XOR dst, src1, src2`; `NOT dst, src1` | Provisionally chosen as ordinary bitwise logic gates: each bit position is processed independently. Useful for packed data, masks, and input bits. `NOT` flips all 32 bits, not a Boolean value. |
| Shifts | `SHL1 dst, src1`; `SHR1 dst, src1`; `SHR_ZERO1 dst, src1` | Move bits by exactly one position. `SHL1` fills the new low bit with zero. `SHR1` copies the old top bit into the new top bit; `SHR_ZERO1` fills it with zero. Repeat in software for larger distances. Names are provisional. |
| Word memory | `LOAD dst, [src1]`; `STORE src, [src1]` | Move aligned 32-bit words between registers and data memory/I/O. The address is the **number held in** `src1`; `src1` itself is a register name. For an offset address, calculate it in a register first; there is no separate offset opcode. |
| Conditional blocks | `IF_EQ src1, src2, N`; `IF_NE src1, src2, N`; `IF_GT src1, src2, N`; `IF_UGT src1, src2, N` | All four are provisionally chosen. If true, continue at `P+4`; if false, skip the *next N complete machine instructions* and continue at `P+4(N+1)`. `GT` uses signed order; `UGT` uses unsigned order. Swap operands to express less-than; combine a condition with `GHOST` for different block shapes. `N=0` has no observable effect. |
| Flow | `GHOST N`; `REPEAT N`; `JUMP_REG target_reg`; `CALL_REG target_reg, link_reg` | `GHOST` unconditionally skips N next instructions: `PC=P+4(N+1)`. `REPEAT` goes to `P-4N`; N must be at least 1. `JUMP_REG` loads the PC from a register. `CALL_REG` first reads the old target, then writes `P+4` to `link_reg`, then jumps to that target. Return with `JUMP_REG link_reg`. |
| Finish | `HALT`; `ERR_HALT` | Stop with success or with a software-reported failure, respectively. Automatic hardware faults stop with their own cause status. `GHOST 0` serves as a no-op, so there is no separate `NOP` instruction. |

**Counts and blocks.** `IF_*` controls exactly N following machine instructions, including any `GHOST` in that range. If the condition is false, none of those N instructions executes. A true `IF_*` does not force all N instructions to execute; control flow inside the block still works normally. This is why a one-instruction conditional block containing `GHOST` can exit a loop. `REPEAT` can revisit the conditional on every iteration. `GHOST 0` simply advances to the next instruction. Counts refer to encoded instructions, not source lines or macro invocations.

**Assembler conveniences, not extra opcodes.** A label can stand in for a `GHOST` destination or `REPEAT` destination; the assembler calculates the count. A block-end label can provide an `IF_*` count. `ADD dst, src2` may expand to `ADD dst, dst, src2`, and similarly for `SUB`. `LOAD_CONST dst, value` may expand to `SET_CONST` alone if the signed value fits, otherwise to `SET_CONST` plus `SET_HIGH`. A future assembler could support a fixed numeric address using an explicit scratch register, such as `LOAD_AT A, 256, B` expanding to `SET_CONST B, 256` followed by `LOAD A, [B]`. This is **not** a separate CPU instruction in this draft. These expansions must be accounted for before branch counts are calculated. There is no special `RETURN` opcode: it is an alias for `JUMP_REG link_reg` in a documented calling convention.

**Call convention proposal.** Use `G` as the usual link register, while retaining the ISA's ability to select another link register. A function that calls another function saves its incoming link value in data memory and restores it before returning. A fuller convention for argument, result, and stack registers waits until we write a nested-call example. If `target_reg` and `link_reg` name the same register, the old target is used for the jump before the link value overwrites it.

## Memory, I/O, and error behavior

- Reserve a high region of **data** addresses for memory-mapped peripheral registers. `LOAD` and `STORE` read buttons and control LEDs or later video hardware through that region. Exact addresses and peripheral behavior are board/platform decisions, not instruction opcodes. Physical buttons need synchronization/debouncing in supporting hardware. The game rules, positions, collision response, and score updates run as CPU software.
- The current ISA draft has word loads/stores and word-sized I/O only. Byte/halfword operations are deferred extensions. Their behavior and opcodes can be designed when a program shows a need for them.
- An invalid opcode, illegal reserved bit, misaligned instruction target or word access, unmapped data access, program address outside installed program memory, or division by zero stops execution with a hardware fault code distinguishable from both `HALT` and `ERR_HALT`. An operation has no partial side effect on error. The simulator should report the failing PC and relevant address or divisor; the board may show a compact status on LEDs or serial output. Exact electrical status interface is implementation-specific. A continuing `ERR_WARNING` operation is deferred.
- Polling input is sufficient for the first interactive game. Interrupts, traps, privilege levels, and memory fences are outside this proposed first ISA. `MUL` and `DIV` belong to the target ISA but can be implemented after the first board self-check if needed to keep the initial bring-up manageable.

## Does a 32-bit instruction fit?

Yes in principle. A 6-bit opcode supports up to 64 operations. Three register identifiers consume 9 bits, and a 16-bit immediate/count consumes 16 bits, leaving one bit (`6+9+16+1=32`). The table has fewer than 64 operation names. Different instructions use different subsets of those fields, and unused fields can be required to equal zero. The **exact bit layout and opcode numbers remain unassigned** pending review. A uniform format is convenient but not required. Fixed 32-bit instructions keep counted skips simple even though they are not compact in program memory.

## Example: sum a length-prefixed list

Data memory at address 256 contains a word holding the list length; elements follow at 260, 264, 268, and so on. This length prevents an element equal to a special sentinel from accidentally ending the list. The example leaves the sum in `A` and reserves `H=0` for the equality check. `ADD_CONST` avoids reserving two additional registers for the constants 4 and 1.

```text
SET_CONST A, 0            ; sum
SET_CONST H, 0            ; constant zero
SET_CONST B, 256          ; B holds a numeric data-memory address
LOAD C, [B]              ; read the word at data address 256
ADD_CONST B, B, 4         ; B now holds address 260
loop:
IF_EQ C, H, 1             ; when count is zero, execute the next GHOST
GHOST done               ; otherwise IF_EQ skips this instruction
LOAD D, [B]
ADD A, A, D
ADD_CONST B, B, 4
ADD_CONST C, C, -1
REPEAT loop               ; assembler computes backward count
done:
HALT
```

For a Pong-like program, the same pattern polls input with `LOAD`, updates position/velocity with arithmetic and conditionals, writes state to mapped output registers with `STORE`, and uses `REPEAT` for the game loop. Dedicated hardware can generate video timing and draw from those state registers without executing game rules.

## Review map

Review can proceed in a few larger passes: (1) core values/arithmetic, (2) memory and I/O, (3) conditions and control flow, (4) errors and extensions. For each pass, compare alternatives and decide **accept**, **change**, or **defer**. The next steps are binary encoding, a small assembler and reference simulator, and then RTL. No entry in this draft is *working* until it passes a reproducible test.
