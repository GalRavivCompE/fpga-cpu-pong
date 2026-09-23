# FPGA CPU Pong

I'm designing a custom CPU, building it on an FPGA, and using software running on that CPU to control a simple interactive game. My main goal is to **learn how the CPU works**. This public repository records decisions, experiments, mistakes, and results as I go.

## Current status

**ISA behavior is a design draft. No CPU has been implemented or tested.** The current candidate has 32-bit values and instructions, eight writable registers, and 29 proposed operations. Eight versus 16 registers remains open. Opcode encodings, FPGA board, HDL, tools, and display method have not been chosen.

## Project documents

| Read this | For |
| --- | --- |
| [Instruction reference](docs/isa/reference.md) | The proposed syntax and behavior of each instruction |
| [Example programs](docs/isa/examples.md) | Small assembly sketches that exercise the ISA |
| [ISA comparisons](docs/isa/comparisons.md) | Tradeoffs against Astro8 and RISC-V |
| [Decision log](docs/project/decisions.md) | Chosen, provisional, excluded, and open design choices |
| [Progress log](docs/project/progress.md) | What has actually been tested and learned |

## First milestones

1. Assign binary instruction encodings and test small programs in a reference simulator.
2. Choose a board and toolchain, implement a small CPU subset, and verify it in HDL simulation.
3. Run a CPU self-check on the board with an observable result such as an LED or serial output.
4. Add memory-mapped input and output, then run game rules as CPU software. Add a display if the board, time, and interest support it.

The CPU software will update paddle and ball state, collisions, and scores. Supporting hardware may handle physical input, video timing, and drawing from software-written state. Each milestone should record a prediction, a reproducible test, the observed result, and what I learned. Proposed features stay labeled as proposals until they work in simulation or on a board.

[Public repository](https://github.com/GalRavivCompE/fpga-cpu-pong)
