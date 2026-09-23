# Complete candidate ISA, revision 0.1

**Status: proposed design for review, not a finalized or working ISA.** Prepared 2026-09-22 and revised during section review. Nothing here has been encoded, assembled, simulated, or run on an FPGA. Earlier choices remain **provisional** in [decisions.md](decisions.md); additional instructions below are candidates for review. Each may be accepted, changed, or deferred.

The goal is a small, general-purpose 32-bit CPU that is approachable to implement on an FPGA and pleasant enough to program by hand. Instruction names here describe behavior; final distinctive names can be chosen after semantics are stable. Inspiration and comparison: [RISC-V RV32I](https://docs.riscv.org/reference/isa/v20240411/unpriv/rv32.html) and [Astro8](https://sam-astro.github.io/Astro8-Computer/docs/Architecture/Instruction%20Set.html). Similar basic arithmetic is useful; counted conditional blocks, `GHOST`, `REPEAT`, eight writable registers, and separate program/data spaces make this design meaningfully different.

## Programmer-visible machine

- Eight writable 32-bit registers `R0`–`R7`; no hardwired zero register. Reset clears them and sets the 32-bit program counter (PC) to byte address 0. Any register can hold a number, address, or bit pattern; there are no type tags.
- Every instruction is one 32-bit word. Program addresses are byte addresses and must be multiples of four. Normal execution advances `PC` by 4. Program fetch and data access have separate logical address spaces; a data load cannot read an instruction word.
- Data memory is byte addressed. A 32-bit word at address `A` occupies bytes `A` through `A+3`; the next aligned word begins at `A+4`. Byte order within a word is deferred until smaller transfers are designed.
- Arithmetic keeps the low 32 bits (modulo `2^32`). Signed comparisons interpret bit patterns as two's-complement values. No condition flags are stored.
- Instruction counts (`N`) are unsigned 16-bit values, 0–65535, unless stated otherwise. `imm16` is a 16-bit bit pattern; operations called *signed* sign-extend it to 32 bits. The assembler must reject operands outside the stated range instead of silently truncating them.

## Instruction set

Notation: `Rd` receives a result, `Ra` and `Rb` are sources, and `[A]` means data memory at byte address `A`. `PC=P` refers to the address of the instruction currently executing.

| Group | Instructions | Meaning and reason to include |
| --- | --- | --- |
| Constants/copy | `SET_SMALL Rd, signed_imm16`; `SET_HIGH Rd, imm16`; `MOVE Rd, Ra` | Load a small signed value; replace bits 31:16 of `Rd` while keeping bits 15:0; copy a register. The first two build any 32-bit value. `MOVE` is provisionally chosen as a direct instruction because copying a register is distinct from loading data memory. `SET_SMALL` with `0xFFFF` produces `0xFFFFFFFF` (-1). |
| Arithmetic | `ADD Rd, Ra, Rb`; `SUB Rd, Ra, Rb`; `MUL Rd, Ra, Rb`; `DIV Rd, Ra, Rb` | Add/subtract modulo `2^32`. Multiplication and division are provisionally included at the project's request. Their exact signedness and edge cases remain open. A constant must currently be loaded into a register before arithmetic; `ADD_SMALL` is deferred for later review. |
| Bitwise | `AND Rd, Ra, Rb`; `OR Rd, Ra, Rb`; `XOR Rd, Ra, Rb`; `NOT Rd, Ra` | Provisionally chosen as ordinary bitwise logic gates: each bit position is processed independently. Useful for packed data, masks, and input bits. `NOT` flips all 32 bits, not a Boolean value. |
| Shifts | `SHL1 Rd, Ra`; `SHR1 Rd, Ra` | Move bits by exactly one position. `SHL1` fills the new low bit with zero; `SHR1` copies the old top bit into the new top bit. Repeat in software for larger distances. A zero-filling right shift is not a direct instruction in this draft. |
| Word memory | `LOAD Rd, [Ra]`; `STORE Rs, [Ra]` | Move aligned 32-bit words between registers and data memory/I/O. The address is exactly the value in `Ra`. For an offset address, calculate it in a register first; there is no separate offset opcode. |
| Conditional blocks | `IF_EQ Ra, Rb, N`; `IF_NE Ra, Rb, N`; `IF_GT Ra, Rb, N`; `IF_UGT Ra, Rb, N` | If true, continue at `P+4`; if false, skip the *next N complete machine instructions* and continue at `P+4(N+1)`. `GT` uses signed order; `UGT` uses unsigned order. Swap operands to express less-than; combine a condition with `GHOST` for different block shapes. `N=0` has no observable effect. |
| Flow | `GHOST N`; `REPEAT N`; `JUMP_REG Rtarget`; `CALL_REG Rtarget, Rlink` | `GHOST` unconditionally skips N next instructions: `PC=P+4(N+1)`. `REPEAT` goes to `P-4N`; N must be at least 1. `JUMP_REG` loads the PC from a register. `CALL_REG` first reads the old target, then writes `P+4` to `Rlink`, then jumps to that target. Return with `JUMP_REG Rlink`. |
| Finish | `NOP`; `HALT` | `NOP` advances normally without changing registers/memory. `HALT` stops execution with a success status visible to the simulator or board diagnostic circuit. |

**Counts and blocks.** `IF_*` controls exactly N following machine instructions, including any `GHOST` in that range. If the condition is false, none of those N instructions executes. A true `IF_*` does not force all N instructions to execute; control flow inside the block still works normally. This is why a one-instruction conditional block containing `GHOST` can exit a loop. `REPEAT` can revisit the conditional on every iteration. Counts refer to encoded instructions, not source lines or macro invocations.

**Assembler conveniences, not extra opcodes.** A label can stand in for a `GHOST` destination or `REPEAT` destination; the assembler calculates the count. A block-end label can provide an `IF_*` count. `ADD Rd, Rb` may expand to `ADD Rd, Rd, Rb`, and similarly for `SUB`. `LOAD_CONST Rd, value` may expand to `SET_SMALL` alone if the signed value fits, otherwise to `SET_SMALL` plus `SET_HIGH`. These expansions must be accounted for before branch counts are calculated. There is no special `RETURN` opcode: it is an alias for `JUMP_REG Rlink` in a documented calling convention.

**Call convention proposal.** Use `R6` as the usual link register, while retaining the ISA's ability to select another link register. A function that calls another function saves its incoming link value in data memory and restores it before returning. A fuller convention for argument, result, and stack registers waits until we write a nested-call example. If `Rtarget` and `Rlink` name the same register, the old target is used for the jump before the link value overwrites it.

## Memory, I/O, and error behavior

- Reserve a high region of **data** addresses for memory-mapped peripheral registers. `LOAD` and `STORE` read buttons and control LEDs or later video hardware through that region. Exact addresses and peripheral behavior are board/platform decisions, not instruction opcodes. Physical buttons need synchronization/debouncing in supporting hardware. The game rules, positions, collision response, and score updates run as CPU software.
- The current ISA draft has word loads/stores and word-sized I/O only. Byte/halfword operations are deferred extensions. Their behavior and opcodes can be designed when a program shows a need for them.
- An invalid opcode, illegal reserved bit, misaligned instruction target or word/halfword access, unmapped data access, or program address outside installed program memory stops execution with an error code distinguishable from `HALT`. An access has no partial side effect on error. The simulator should report the failing PC and address; the board may show a compact status on LEDs or serial output. Exact electrical status interface is implementation-specific.
- Polling input is sufficient for the first interactive game. Interrupts, traps, privilege levels, and memory fences are outside this proposed first ISA. `MUL` and `DIV` belong to the target ISA but can be implemented after the first board self-check if needed to keep the initial bring-up manageable.

## Does a 32-bit instruction fit?

Yes in principle. A 6-bit opcode supports up to 64 operations. Three register identifiers consume 9 bits, and a 16-bit immediate/count consumes 16 bits, leaving one bit (`6+9+16+1=32`). The table has fewer than 64 operation names. Different instructions use different subsets of those fields, and unused fields can be required to equal zero. The **exact bit layout and opcode numbers remain unassigned** pending review. A uniform format is convenient but not required. Fixed 32-bit instructions keep counted skips simple even though they are not compact in program memory.

## Example: sum a length-prefixed list

Data memory at address 256 contains a word holding the list length; elements follow at 260, 264, 268, and so on. This length prevents an element equal to a special sentinel from accidentally ending the list. The example leaves the sum in `R0`; it reserves `R4=4` for stepping to the next word, `R5=1` for decrementing the count, and `R7=0` for the equality check.

```text
SET_SMALL R0, 0           ; sum
SET_SMALL R7, 0           ; constant zero
SET_SMALL R4, 4           ; bytes per word
SET_SMALL R5, 1           ; count decrement
SET_SMALL R1, 256         ; pointer to length
LOAD R2, [R1]            ; remaining element count
ADD R1, R1, R4            ; pointer to first element
loop:
IF_EQ R2, R7, 1           ; when count is zero, execute the next GHOST
GHOST done                ; otherwise IF_EQ skips this instruction
LOAD R3, [R1]
ADD R0, R0, R3
ADD R1, R1, R4
SUB R2, R2, R5
REPEAT loop               ; assembler computes backward count
done:
HALT
```

For a Pong-like program, the same pattern polls input with `LOAD`, updates position/velocity with arithmetic and conditionals, writes state to mapped output registers with `STORE`, and uses `REPEAT` for the game loop. Dedicated hardware can generate video timing and draw from those state registers without executing game rules.

## Review map

Review can proceed in a few larger passes: (1) core values/arithmetic, (2) memory and I/O, (3) conditions and control flow, (4) errors and extensions. For each pass, compare alternatives and decide **accept**, **change**, or **defer**. The next steps are binary encoding, a small assembler and reference simulator, and then RTL. No entry in this draft is *working* until it passes a reproducible test.
