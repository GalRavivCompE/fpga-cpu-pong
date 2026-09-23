# Progress log

## 2026-09-22 — project setup

**Status:** Planning. Defined the goal, a CPU/software versus hardware boundary, a 16-bit versus 32-bit comparison, and a board-first milestone sequence. No RTL, programs, simulation tests, or board results exist yet.

The public repository at [GalRavivCompE/fpga-cpu-pong](https://github.com/GalRavivCompE/fpga-cpu-pong) now holds the project record. Implementation remains planned.

## 2026-09-23 — functional ISA draft selected

**Status:** Design only. Reviewed the v1 instruction set and behavior, including explicit counted conditions and fixed-count `GHOST`/`REPEAT`. The next design pass is instruction naming, followed by binary encoding. No instruction has been assembled, simulated, or implemented in RTL; no board has been chosen.

## 2026-09-23 — instruction reference and Astro8 comparison

**Status:** Documentation only. Added an indexed, instruction-by-instruction [ISA reference](isa-reference.md) with syntax and behavior, modeled on the organization of Astro8's reference. [Compared Astro8 features](astro8-comparison.md) and recorded candidate extensions without adding them to v1. Opcode IDs and bit fields are still unassigned; no instruction has been simulated or run on an FPGA.

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
