# Decision log

Status meanings: **open** = being explored; **provisional** = useful working choice, subject to evidence; **accepted** = selected and recorded with rationale; **working** = verified in implementation.

| Decision | Status | Candidates / evidence needed |
| --- | --- | --- |
| CPU word width | Open | 16 or 32 bits. Compare ISA encoding, game-program size, simulated behavior, and synthesis cost. |
| Instruction width and encoding | Open | Fixed 16, fixed 32, or a simple longer-immediate format. Decide after writing example game-loop code. |
| Registers, flags, and memory map | Open | Keep the initial ISA small; define exact behavior before RTL. |
| Microarchitecture | Open | A simple multicycle CPU is a plausible starting point; compare against single-cycle complexity after ISA sketch. Avoid a pipeline initially unless there is a measured need. |
| HDL and simulator | Open | Choose based on learning preference, board tools, and ability to run automated simulation locally. |
| FPGA board | Open | Check cost/availability, tool support, on-chip memory, I/O voltage/connectors, and a usable input/output path. |
| First physical output | Open | LEDs, serial terminal, or display. Video connector and monitor support matter if selecting video. |
| Game input | Open | Buttons or other controller; synchronize physical inputs in hardware. |
| First game | Provisional | Pong-like rules, because a small state update can be tested independently of rendering. |
| Software/hardware boundary | Provisional | CPU computes game state and rules; hardware handles physical I/O and optional video timing/rendering. |
| First hardware priority | Accepted (2026-09-22) | Run a functioning CPU on an FPGA board first. Initial output may be LEDs or serial; video follows only if useful. User preference. |
| Project documentation | Accepted (2026-09-22) | Maintain this repository as the GitHub project record, with reproducible milestone notes and explicit planned/working status. User preference. |
| Primary project objective | Accepted (2026-09-22) | Learning and understanding take priority over finishing a polished demo. Use design exercises, predictions, review, and small tests; avoid unexplained end-to-end AI implementation. User preference. |
| ISA comparison method | Accepted (2026-09-22) | Compare major design choices with established ISAs such as RISC-V, explaining similarities and differences before deciding what to adopt. User preference. |
| ISA design discussion method | Accepted (2026-09-22) | For each design problem, present viable options and tradeoffs before asking the user to choose. Treat existing ISAs as references; document why a feature is adopted, adapted, or intentionally different so the custom ISA has its own coherent design. User preference. |
| Addressing and first load/store size | Provisional (2026-09-22) | Memory addresses identify bytes. The first CPU supports aligned 32-bit loads and stores; byte and halfword operations can be considered later. This keeps the initial datapath and memory interface simple while allowing finer-grained accesses in a future extension. Similar to RISC-V's byte-addressed space and word operations. |
| Conditional and skip operations | Provisional (2026-09-22) | `IF_EQ Ra, Rb, N` compares two registers; if equal, the following N machine instructions execute normally, and if not equal they are skipped. `GHOST N` unconditionally skips the following N machine instructions. The operations are separate; an `IF_EQ` block can control a `GHOST`. Compared with RISC-V's BEQ, which branches to a PC-relative target when equal, this design uses counted sequential skipping and needs instruction-count semantics. |
| Instruction width | Provisional (2026-09-22) | Fixed 32-bit instructions. This makes counted skipping straightforward: advance the byte-addressed PC by four bytes for each skipped instruction. RV32I also uses fixed 32-bit base instructions, though it has an optional compressed extension; our reason is to simplify the first implementation of counted skips. |
| Instruction/data memory organization | Provisional (2026-09-22) | Keep separate logical instruction-fetch and data-load/store address spaces in the first CPU (Harvard-style programmer-visible organization). `LOAD`/`STORE` and memory-mapped I/O use the data space; program fetch uses the instruction space. This makes the fetch-versus-data distinction explicit and supports a simple read-only program memory plus writable data memory. It means constants needed by a running program must be encoded in instructions or initialized in data memory; programs cannot read their own instruction words as data. This ISA-level choice is distinct from using separate physical FPGA RAM blocks: RISC-V specifies one byte-addressed address space even though a RISC-V implementation may use separate physical instruction/data paths or memories. |

## Evidence and change rule

Record each accepted decision with date, rationale, alternatives, and the measurement or simulation that supported it. If a later test contradicts the rationale, revise the choice and note why. Mark features **working** only after a reproducible simulation or hardware observation, with the command or procedure recorded here.
