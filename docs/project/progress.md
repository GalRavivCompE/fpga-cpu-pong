# Progress log

## 2026-09-22 — project setup

**Status:** Planning. Defined the goal, a CPU/software versus hardware boundary, a 16-bit versus 32-bit comparison, and a board-first milestone sequence. No RTL, programs, simulation tests, or board results exist yet.

The public repository at [GalRavivCompE/fpga-cpu-pong](https://github.com/GalRavivCompE/fpga-cpu-pong) now holds the project record. Implementation remains planned.

## 2026-09-23 — functional ISA draft selected

**Status:** Design only. Reviewed the v1 instruction set and behavior, including explicit counted conditions and fixed-count `GHOST`/`REPEAT`. The next design pass is instruction naming, followed by binary encoding. No instruction has been assembled, simulated, or implemented in RTL; no board has been chosen.

## 2026-09-23 — instruction reference and Astro8 comparison

**Status:** Documentation only. Added an indexed, instruction-by-instruction [ISA reference](../isa/reference.md) with syntax and behavior, modeled on the organization of Astro8's reference. [Compared Astro8 features](../isa/comparisons.md) and recorded candidate extensions without adding them to v1. Opcode IDs and bit fields are still unassigned; no instruction has been simulated or run on an FPGA.

## 2026-09-23 — PC read and variable-distance shifts

**Status:** Design only. Added `COUNT dst` to read the current PC byte address. Revised `LSHIFT`, `RSHIFT`, and `RSHIFT_SIGN` to use `dst, src1, src2`, with `src2` holding an unsigned shift distance. Defined zero-distance and 32-or-greater behavior. Eight versus 16 writable registers remains open pending program examples and hardware constraints; dedicated constant registers are set aside. No opcode encoding or hardware result exists yet.

## 2026-09-23 — documentation cleanup

**Status:** Documentation organization only. Moved the current ISA reference, examples, and comparisons into `docs/isa/`, and project decisions and progress into `docs/project/`. Removed superseded proposal and audit files from the current tree; Git history retains them. No CPU behavior or implementation changed.

## 2026-10-14 — byte read added to ISA draft

**Status:** Design only. Added `READ_BYTE dst, [address_reg]` for zero-extended 8-bit reads from any valid data byte address and specified little-endian word layout. Byte writes remain outside v1. Updated the ISA comparison and decision log. Opcode encoding, RTL, and simulation are still pending.

## 2026-10-14 — candidate binary encoding assigned

**Status:** Design only. Assigned six-bit opcode values to all 30 candidate instructions, five-bit register fields, and 16-bit immediate/count fields where needed. Specified zero reserved bits, invalid register codes, and two manually encoded examples. No assembler, decoder, RTL, or simulation result exists yet. The first CPU still proposes eight physical registers; wider register fields reserve room for future choices.

## 2026-10-14 — register codes assigned

**Status:** Design only. Revised the candidate to use all 32 register codes: R0 always reads as zero and discards writes; R1–R31 are writable. Updated instruction examples and ISA comparisons. The register-file circuit and its FPGA cost remain unmeasured; no CPU behavior has been verified in simulation or on a board.

## 2026-10-29 — first executable CPU slice

**Status:** Python simulation only. Implemented `DUPE`, `SET_LOW`, `ADD_CONST`, and `HALT` in a small fetch/decode/execute simulator. A four-word program produces R0=0, R1=7, and R2=12 and halts at byte PC=12. Three unit tests check the trace result, R0 behavior and upper-half preservation, and signed immediate wraparound. Reproduce with the commands in the [first simulator slice](../simulation/first-slice.md). This does not verify RTL or FPGA behavior; RAM, loops, and the rest of the ISA remain to be implemented.

## 2026-10-29 — list program assembled and simulated

**Status:** Python simulation only. Added a 1,024-byte byte-addressed data RAM, the `READ`, `READ_BYTE`, `WRITE`, `IF_EQ`, `GHOST`, `REPEAT`, `ADD`, and `SET_HIGH` operations, and a small two-pass assembler. The length-prefixed list program sums `[7, 12, 5]` to 24 and halts; tests also cover empty and one-item lists, 32-bit wraparound, little-endian byte reads, and bad alignment. Reproduce with the commands in [running an ISA program in Python](../simulation/list-sum.md). The simulator now covers 12 of 30 candidate instructions. No RTL or FPGA result exists.

## Milestone entry template

Template for future milestone entries:

### YYYY-MM-DD — milestone name

- **Status:** Planned / simulated / working on board
- **Question or prediction:** What did I expect, and why?
- **What changed:**
- **How to reproduce:** Exact commands, board settings, and input steps
- **Evidence:** Test output, waveform, synthesis report, or observed output
- **What I learned:** Explain the result and how it changed my understanding
- **Limitations and next step:**
