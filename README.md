# FPGA CPU Pong

I'm designing a custom CPU, building it on an FPGA, and using software running on that CPU to control a simple interactive game. My main goal is to **learn how the CPU works**. This public repository records decisions, experiments, mistakes, and results as I go.

## Current status

**A list-summing ISA program runs in a Python simulator; no RTL or FPGA CPU exists yet.** The candidate ISA has 32-bit values and instructions, 30 proposed operations, and 32 register codes: `R0` always reads as zero and `R1`–`R31` are writable. Six-bit opcode values and instruction fields are documented. The simulator executes 12 instructions, including RAM access and counted control flow; the other 18 operations remain design proposals. The register-file circuit, FPGA board, HDL, tools, and display method have not been chosen.

## Project documents

| Read this | For |
| --- | --- |
| [Instruction reference](docs/isa/reference.md) | The proposed syntax and behavior of each instruction |
| [Example programs](docs/isa/examples.md) | Small assembly sketches that exercise the ISA |
| [First simulator slice](docs/simulation/first-slice.md) | How to run and understand the first executable program |
| [List program in simulation](docs/simulation/list-sum.md) | Assemble and run a loop using RAM |
| [ISA comparisons](docs/isa/comparisons.md) | Tradeoffs against Astro8 and RISC-V |
| [Decision log](docs/project/decisions.md) | Chosen, provisional, excluded, and open design choices |
| [Progress log](docs/project/progress.md) | What has actually been tested and learned |

## First milestones

1. Use the Python simulator to test programs written for the candidate ISA; extend its instruction subset as real programs need it.
2. Choose a board and toolchain, implement a small CPU subset, and verify it in HDL simulation.
3. Run a CPU self-check on the board with an observable result such as an LED or serial output.
4. Add memory-mapped input and output, then run game rules as CPU software. Add a display if the board, time, and interest support it.

The CPU software will update paddle and ball state, collisions, and scores. Supporting hardware may handle physical input, video timing, and drawing from software-written state. Each milestone should record a prediction, a reproducible test, the observed result, and what I learned. Proposed features stay labeled as proposals until they work in simulation or on a board.

[Public repository](https://github.com/GalRavivCompE/fpga-cpu-pong)
