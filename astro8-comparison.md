# Astro8 functionality comparison

**Status: review notes, not additions to this project's ISA.** Compared on 2026-09-23 with the [Astro8 instruction set reference](https://sam-astro.github.io/Astro8-Computer/docs/Architecture/Instruction%20Set.html). Astro8's names and instruction IDs describe *its* machine, not ours. Our [instruction reference](isa-reference.md) remains a candidate design with no assigned opcode IDs or working implementation.

The question is whether Astro8 can do something useful that our current instructions cannot, or can do only awkwardly. Similar instruction names do not guarantee identical behavior: Astro8 uses registers A/B/C for several fixed-purpose operations, whereas our instructions usually name any of eight registers.

| Astro8 feature | Current route in our ISA | Possible choice and tradeoff |
| --- | --- | --- |
| `AIN`, `BIN`, `CIN`, `STA`, `LDLGE`, `STLGE`: read/write using an address supplied in or after the instruction | Build an address with `SET_LOW`/`SET_HIGH`, then use `READ`/`WRITE`. An assembler could hide the setup as a shortcut. | **Keep register-addressed memory for v1** for a small, regular CPU; consider a direct-address instruction later if real programs spend too many instructions building addresses. |
| `LDIA`, `LDIB`, `LDW`, `LDWB`: load a value, including a value in the following word | `SET_LOW` plus `SET_HIGH` builds any 32-bit constant. The halves can also be updated separately. | **Keep two half-setting instructions for v1**; a literal-in-next-word format might shorten source code but creates variable-length instructions and complicates counted `GHOST`/`IF_*` semantics. |
| `BSL`, `BSR`: shift by a distance held in a register | Repeat `LSHIFT`, `RSHIFT`, or `RSHIFT_SIGN` in a software loop. | **Worth measuring.** A register-distance shift is much faster for large or varying counts, but a barrel shifter costs more FPGA logic. An immediate-distance shift is another option, with fewer source registers but a fixed amount per instruction. |
| `PCR`: copy the program counter to a register | No direct equivalent. `CALL` gives a return address to its link register while also jumping, and absolute code labels can be assembled into constants. | **Most interesting functional gap.** A `GET_PC dst` instruction could make position-independent code and PC-relative tables easier. Alternatively, add a PC-relative address instruction or keep absolute addresses for the first fixed-ROM programs. Which benefit matters depends on planned software. |
| `JMP`, `JMPZ`, `JMPC`, `JREG`: unconditional, zero, carry, and register jumps | `GHOST`/`REPEAT` handle fixed forward/backward movement; `LEAP` handles a register target. Compare against a zero register with `IF_EQ`; after unsigned addition, compare the result with an input using `IF_UGT` to detect wraparound. | **No immediate need for special zero/carry branches.** A direct condition-and-target branch could reduce instruction count, but it would change the distinctive counted-block model. Measure code size first. |
| `SWP`, `SWPC`: exchange register contents | Use a temporary register and `DUPE` three times, or use `XOR` operations when no scratch register is free. | **Optional convenience.** A `SWAP a, b` could save instructions without adding new computational ability. Its usefulness should be judged from actual programs. |
| `BNK`, `BNKC`: select a memory bank | Our data addresses are 32-bit numbers; the first physical RAM can simply implement a small valid region. | **Do not add for the first board.** Banking is useful when a physical address space exceeds the simple address hardware, but it introduces hidden state to every memory access. |
| `VBUF`: copy video memory to the display | The CPU can `WRITE` to a memory-mapped video control register; supporting hardware can swap buffers or render state. | **Keep video control in the hardware memory map.** If a display later needs buffer swapping, document the register and its behavior rather than reserve a CPU opcode for it. |
| Expansion-port and fixed input/output operations | `READ`/`WRITE` access memory-mapped peripheral registers. | **Keep one I/O model** for buttons, LEDs, serial, and later video. The exact addresses are platform decisions, still open. |
| `NOP` | `GHOST 0` advances without changing registers or data memory. | **Already covered.** A separate opcode would duplicate this behavior. |

Astro8's page also lists ordinary arithmetic and bitwise operations already present in our draft. Our candidate additionally has `XOR`, `MOD`, unsigned greater-than, a sign-preserving right shift, `CALL` with a link register, and explicit `HALT`/`FAIL` outcomes. Those differences reflect design choices; they do not by themselves make either ISA better for a particular program.

## Questions to test before adding an opcode

1. Can a short program express the needed behavior using the current instructions?
2. How many instructions and registers does that version use?
3. Would a proposed opcode materially improve a real program or the first board demonstration?
4. What extra RTL, decoding, and tests would it require?

The first concrete experiments should be a list loop, a button-to-LED program, and a small function call. If those expose a recurring cost, revisit the table. **No Astro8-inspired instruction has been added as a result of this comparison.**
