# ISA comparisons

**Status: design review, not implementation evidence.** This page compares the current [instruction reference](reference.md) with [Astro8](https://sam-astro.github.io/Astro8-Computer/docs/Architecture/Instruction%20Set.html) and [RISC-V RV32I](https://docs.riscv.org/reference/isa/v20240411/unpriv/rv32.html). The external names and opcode IDs describe those machines, not ours. Our candidate still has no assigned opcode IDs or working implementation.

## Astro8

The comparison led to `COUNT` and variable-distance shifts in our candidate ISA; the remaining options below have not been adopted.

The question is whether Astro8 can do something useful that our current instructions cannot, or can do only awkwardly. Similar instruction names do not guarantee identical behavior: Astro8 uses registers A/B/C for several fixed-purpose operations, whereas our instructions usually name any of eight registers.

| Astro8 feature | Current route in our ISA | Possible choice and tradeoff |
| --- | --- | --- |
| `AIN`, `BIN`, `CIN`, `STA`, `LDLGE`, `STLGE`: read/write using an address supplied in or after the instruction | Build an address with `SET_LOW`/`SET_HIGH`, then use `READ`/`WRITE`. An assembler could hide the setup as a shortcut. | **Keep register-addressed memory for v1** for a small, regular CPU; consider a direct-address instruction later if real programs spend too many instructions building addresses. |
| `LDIA`, `LDIB`, `LDW`, `LDWB`: load a value, including a value in the following word | `SET_LOW` plus `SET_HIGH` builds any 32-bit constant. The halves can also be updated separately. | **Keep two half-setting instructions for v1**; a literal-in-next-word format might shorten source code but creates variable-length instructions and complicates counted `GHOST`/`IF_*` semantics. |
| `BSL`, `BSR`: shift by a distance held in a register | `LSHIFT`, `RSHIFT`, and `RSHIFT_SIGN` now take `dst, src1, src2`, with the distance held in `src2`. | **Added to the candidate ISA.** The amount is unsigned; counts of 32 or more have defined fill behavior. A barrel shifter versus a multicycle shifter is still an implementation choice. |
| `PCR`: copy the program counter to a register | `COUNT dst` now writes the current instruction's PC **byte address** to a destination register. | **Added to the candidate ISA.** This avoids relying solely on absolute labels for location-relative code. The name does not mean a source-line count or an elapsed cycle count. |
| `JMP`, `JMPZ`, `JMPC`, `JREG`: unconditional, zero, carry, and register jumps | `GHOST`/`REPEAT` handle fixed forward/backward movement; `LEAP` handles a register target. Compare against a zero register with `IF_EQ`; after unsigned addition, compare the result with an input using `IF_UGT` to detect wraparound. | **No immediate need for special zero/carry branches.** A direct condition-and-target branch could reduce instruction count, but it would change the distinctive counted-block model. Measure code size first. |
| `SWP`, `SWPC`: exchange register contents | Use a temporary register and `DUPE` three times, or use `XOR` operations when no scratch register is free. | **Optional convenience.** A `SWAP a, b` could save instructions without adding new computational ability. Its usefulness should be judged from actual programs. |
| `BNK`, `BNKC`: select a memory bank | Our data addresses are 32-bit numbers; the first physical RAM can simply implement a small valid region. | **Do not add for the first board.** Banking is useful when a physical address space exceeds the simple address hardware, but it introduces hidden state to every memory access. |
| `VBUF`: copy video memory to the display | The CPU can `WRITE` to a memory-mapped video control register; supporting hardware can swap buffers or render state. | **Keep video control in the hardware memory map.** If a display later needs buffer swapping, document the register and its behavior rather than reserve a CPU opcode for it. |
| Expansion-port and fixed input/output operations | `READ`/`WRITE` access memory-mapped peripheral registers. | **Keep one I/O model** for buttons, LEDs, serial, and later video. The exact addresses are platform decisions, still open. |
| `NOP` | `GHOST 0` advances without changing registers or data memory. | **Already covered.** A separate opcode would duplicate this behavior. |

Astro8's page also lists ordinary arithmetic and bitwise operations already present in our draft. Our candidate additionally has `XOR`, `MOD`, unsigned greater-than, a sign-preserving right shift, `CALL` with a link register, and explicit `HALT`/`FAIL` outcomes. Those differences reflect design choices; they do not by themselves make either ISA better for a particular program.

## RISC-V RV32I

RV32I is a useful comparison for general-purpose software, though compatibility is not a project goal. This table compares the [base integer ISA](https://docs.riscv.org/reference/isa/v20240411/unpriv/rv32.html); optional extensions are described separately in the [RISC-V ISA introduction](https://docs.riscv.org/reference/isa/v20240411/unpriv/intro.html).

| Area | RV32I | Current candidate and tradeoff |
| --- | --- | --- |
| Registers | 32 integer registers, one fixed at zero | Eight writable A–H are the current candidate; 16 writable registers remain open. Fewer registers simplify encoding but may require more RAM traffic. Dedicated constant registers are set aside. |
| Addressing | One byte-addressed ISA memory space; base-plus-offset load/store operations for several data widths | Separate logical program/data spaces, with register-addressed aligned 32-bit `READ`/`WRITE`. This simplifies the first memory interface but makes byte data and some addressing patterns awkward. |
| Control flow | Conditional branches and jumps use relative targets; `JALR` can jump through a register | Counted `IF_*`, `GHOST`, `REPEAT`, `LEAP`, and `CALL` use different control-flow rules. Fixed 32-bit instruction size makes instruction counts predictable; assembler labels still need to resolve those counts. |
| Arithmetic and bits | `ADD`/`SUB`, logical operations, and variable-distance shifts are in the base; multiply and divide belong to the optional M extension | The candidate includes those operations plus `MUL`, `DIV`, and `MOD` as target instructions. This increases the target implementation work, though the first board program need not execute all of them. |
| Errors and completion | The base ISA defines instructions such as `ECALL` and `EBREAK` whose behavior depends on the execution environment | `HALT` and `FAIL` give simple board self-check outcomes; hardware faults are separate. They are project-specific rather than RISC-V-compatible. |

## Questions to test before adding an opcode

1. Can a short program express the needed behavior using the current instructions?
2. How many instructions and registers does that version use?
3. Would a proposed opcode materially improve a real program or the first board demonstration?
4. What extra RTL, decoding, and tests would it require?

The first concrete experiments should be a list loop, a button-to-LED program, and a small function call. If those expose a recurring cost, revisit the remaining options in the table. `COUNT` and variable-distance shifts are **designed only**; no implementation has been verified.
