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
