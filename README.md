# FPGA CPU Pong

I'm designing a CPU with my own instruction set, building it on an FPGA, and using it to run an interactive game. This repository documents the design, experiments, mistakes, and working results as the project develops.

The current [instruction set reference](isa-reference.md) documents each proposed instruction. The longer [ISA design draft](isa-complete-draft.md) explains example programs and rationale. No CPU has been implemented yet.

## Learning comes first

My main goal is to learn CPU design, digital verification, FPGA tools, and engineering tradeoffs. A finished Pong demo matters only if I understand how it works.

For each major step, I want to compare options, make a prediction, then test it. I plan to sketch instructions, write and modify modules, inspect waveforms, and record why I made each design choice. Drafts and suggestions are starting points for my review, not evidence that a feature works.

I will keep milestones small enough to test and understand. Each milestone should record my prediction, the simulation or board result, and what I learned.

## Current status

**Functional ISA draft selected; implementation not started.** The v1 instruction set, intended behavior, and current instruction names have been reviewed. Binary opcode IDs and field positions remain to be chosen. No RTL, assembler, game, simulation result, or FPGA implementation exists yet. A 32-bit datapath and fixed 32-bit instructions are provisional choices; board, HDL, tools, and display remain open.

## Priority and first achievable demo

**My first hardware priority is to get the CPU executing correctly on an FPGA board.** A screen is optional for the first demonstration. A small self-check program can show a result through LEDs or a serial connection, depending on the board chosen. That would give me a reproducible way to check fetch, decode, arithmetic, control flow, memory, reset, and physical output before adding the game.

Before hardware, I want to simulate small programs that exercise arithmetic, memory, and control flow. Once the CPU passes those checks and runs on a board, I can add game software that reads player inputs, updates paddle and ball positions, handles collisions and scoring, and writes game state to memory-mapped registers. Simulation can check those state changes before I try the game on hardware.

The first physical game demo can use the same program and register interface. Its output could be LEDs or a serial terminal. Video is a later integration milestone if time, board features, and interest support it.

## CPU and hardware boundary

| CPU software | Supporting hardware |
| --- | --- |
| Initialize and update ball/paddle state, collision rules, scoring, game loop | Clock/reset, program and data storage, input synchronization and sampling |
| Read input registers and write game-state registers | Optional video timing and drawing from game-state registers |
| Decide direction, speed, and score changes | Physical buttons/controllers and display electrical signals |

The hardware must not decide collisions or scores for the game demo. A renderer may turn software-written coordinates into pixels. This keeps game behavior attributable to instruction execution while avoiding a CPU that must generate every pixel in real time.

## Width comparison to test before choosing

| Consideration | 16-bit candidate | 32-bit candidate |
| --- | --- | --- |
| Datapath and register storage | Smaller, easier to inspect in waveforms | Wider and somewhat more RTL to inspect |
| Coordinates and scores | Easily fits a simple game | Easily fits; more headroom for future software |
| Constants and address space | Needs careful instruction/immediate design | Often simpler for larger constants and memory maps, depending on encoding |
| FPGA resource use | Likely lower, but measure after synthesis | Likely higher, but may still be modest on a suitable board |
| Instruction encoding | A 16-bit fixed instruction can be tight; longer instructions are possible | A 32-bit fixed instruction has room for fields but uses more program memory |
| Learning value | Forces clear tradeoffs and a compact ISA | Makes software and future extensions easier to express |

**32-bit is the provisional CPU word width.** CPU word width and instruction width are separate choices; the current draft also uses fixed 32-bit instructions. Compare the 32-bit candidate with a 16-bit alternative using sample programs and synthesis results before treating the choice as final.

## Proposed sequence

1. Review the [instruction reference](isa-reference.md) and decide which instructions the first board program needs.
2. Choose a board, HDL, simulator, and toolchain based on availability and a simple input/output path. Revisit the provisional 32-bit width if the board or synthesis results give a reason to.
3. Define binary encodings and build a small assembler or encoder plus a reference simulator.
4. Implement and simulate the CPU with small arithmetic, memory, and control-flow programs.
5. Put the CPU on the board, run a self-check program, and show its result through a physical output. Record resource usage and timing.
6. Develop and simulate game software, then run it on the board with physical input and observable game state. Add video if it fits the project's goals and schedule.

## Documenting progress on GitHub

This repository is my project record. For each milestone, I will update [progress.md](progress.md) with a prediction, what ran, how to reproduce it, evidence, what I learned, and known limitations. [decisions.md](decisions.md) records architecture choices. Proposed features stay labeled as proposals until testing shows what actually works.

The public project repository is [GalRavivCompE/fpga-cpu-pong](https://github.com/GalRavivCompE/fpga-cpu-pong).

## Open decisions

See [decisions.md](decisions.md) for the decision log and what evidence each choice needs.

See [isa-gap-audit.md](isa-gap-audit.md) for a comparison of the working ISA ideas with RISC-V RV32I and the gaps to resolve before an ISA version is frozen.

See [isa-proposals.md](isa-proposals.md) for numbered functionality proposals to review and revise; none of those proposals is adopted merely by appearing there.

See [astro8-comparison.md](astro8-comparison.md) for a feature-by-feature comparison with Astro8 and possible future additions.
