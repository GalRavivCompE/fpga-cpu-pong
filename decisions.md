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

## Evidence and change rule

Record each accepted decision with date, rationale, alternatives, and the measurement or simulation that supported it. If a later test contradicts the rationale, revise the choice and note why. Mark features **working** only after a reproducible simulation or hardware observation, with the command or procedure recorded here.
