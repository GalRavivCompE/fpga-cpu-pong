# FPGA CPU Pong

Build a CPU with a custom ISA on an FPGA and demonstrate it executing an interactive game program. The game rules and state updates must execute as CPU instructions. Supporting hardware may sample inputs and produce video or other output.

## Current status

**Planning only.** No ISA, RTL, assembler, game, or FPGA implementation exists yet. Width, board, HDL, tools, and display are open decisions.

## Priority and first achievable demo

**Priority: get the CPU executing correctly on an FPGA board.** A screen is optional for the first hardware demonstration. The first board program should run a small self-check and expose a clear result through LEDs or a serial connection, depending on the board chosen. This proves fetch, decode, arithmetic, branching, memory, reset, and physical output with a reproducible test. Then run the game logic on the same CPU.

Before hardware, run a small program on the CPU in simulation that repeatedly reads two player inputs, updates paddle and ball positions, detects wall/paddle collisions, tracks a score, and writes the resulting game state to memory-mapped registers. A testbench checks the state transitions and observes at least one scored point. A simple software model of the same rules can serve as a reference.

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

**No width selected yet.** CPU word width and instruction width are separate choices. Compare both candidates with the same minimum program, assembler, simulation tests, and synthesis target once a board is shortlisted. Do not assume that a 16-bit CPU must use 16-bit instructions or that a 32-bit CPU must use 32-bit instructions.

## Proposed sequence

1. Specify a minimal game-state interface and write a Python reference step function with representative test cases.
2. Sketch two small ISA encodings (16-bit and 32-bit datapaths) sufficient for loads/stores, arithmetic, comparison/branch, and constants. Estimate instruction counts for one game update.
3. Choose a first architecture using those estimates, then document the ISA precisely: registers, instruction formats, addressing, flags/branches, reset, and memory map.
4. Implement and simulate the CPU, starting with tiny arithmetic and branch programs, then memory-mapped I/O.
5. Choose a board and put the CPU on it. Run a self-check program and show its result through a physical output. Record resource usage and timing.
6. Run the game program on the board with physical input and observable game state. Add video if it still fits the project's goals and schedule.

## Documenting progress on GitHub

This repository is the project record. For each milestone, update [progress.md](progress.md) with what ran, how to reproduce it, evidence (simulation output or board observation), and known limitations. Record architecture choices in [decisions.md](decisions.md). Keep example programs, testbenches, and build commands in the repository as they are developed. Label proposed features as planned and tested behavior as working.

The local repository has no commit or GitHub remote yet. Publishing requires a GitHub repository and a remote URL; neither has been selected here.

## Open decisions

See [decisions.md](decisions.md) for the decision log and what evidence each choice needs.
