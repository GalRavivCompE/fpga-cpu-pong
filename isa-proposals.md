# ISA functionality proposals for review

For a single end-to-end candidate rather than reviewing items one at a time, see [Complete candidate ISA, revision 0.1](isa-complete-draft.md). This numbered file preserves the original alternatives and decision history.

**Status: proposals, not decisions.** Prepared 2026-09-22 from the [gap audit](isa-gap-audit.md) and the current [decision log](decisions.md). No ISA encoding, assembler, or RTL is implemented. The names below describe behavior; final mnemonics can be chosen later. Items can be marked **accept**, **change**, **defer**, or **question** during review.

The comparison baseline is [RISC-V RV32I](https://docs.riscv.org/reference/isa/v20240411/unpriv/rv32.html). Its optional extensions are described in the [ISA introduction](https://docs.riscv.org/reference/isa/v20240411/unpriv/intro.html). The aim is a coherent custom CPU, without RISC-V compatibility as a requirement.

## Machine state and instruction format

1. **Registers and reset.** Proposal: eight writable 32-bit registers `R0`–`R7`; a 32-bit program counter (PC); on reset, PC and all registers become zero. No register is hardwired to zero. Alternative: leave register contents unspecified after reset, requiring software to initialize each one. Zeroing eight registers costs little hardware and makes early debugging more predictable. RV32I instead has a hardwired zero register and more total registers.

2. **Instruction word and fields.** Proposal: every instruction occupies one 32-bit word at a four-byte-aligned program address. Use a common format with a 6-bit opcode, up to three 3-bit register fields, and a 16-bit immediate/count field; unused bits must be zero. This is a feasibility sketch, **not an assigned encoding**. Alternative: several differently packed formats that allow larger immediates but complicate decoding. Exact bit positions and opcode values wait until the operations below are reviewed.

3. **Instruction and data spaces.** Proposal: the PC fetches only from program memory; loads/stores access only data memory and mapped I/O. Both spaces use byte addresses. The first physical implementation can use a program ROM and data RAM. Alternative: one shared ISA address space, allowing programs to read code as data but needing more memory-system design. This choice is already provisional in the decision log.

## Values and calculation

4. **Basic arithmetic.** Proposal: `ADD Rd, Ra, Rb` and `SUB Rd, Ra, Rb`; each writes the low 32 bits. Signed values use two's complement. The two-operand spelling `ADD Rd, Rb` or `SUB Rd, Rb` is an assembler shorthand with `Ra=Rd`, not another hardware opcode. Alternative: separate two-operand opcodes, which would still occupy 32 bits each unless given another useful encoding advantage.

5. **Constants — provisionally adopted.** `SET_SMALL Rd, imm16` sign-extends a 16-bit value into all 32 bits. `SET_HIGH Rd, imm16` replaces bits 31:16 and preserves bits 15:0. Together they can construct any 32-bit pattern; common small values, including -1, take one instruction. Zero extension was considered, but it would make small negative values need a second instruction. A stored constant table remains available in data memory.

6. **Arithmetic with a constant — deferred.** `ADD_SMALL Rd, Ra, imm16` would add a signed 16-bit immediate modulo 2^32. A negative immediate would also perform subtraction. The current ISA draft omits it while the rest of the instructions are reviewed; programs load constants into registers and use `ADD`/`SUB`. Revisit after comparing sample programs.

7. **Bitwise operations.** Proposal: `AND`, `OR`, and `XOR` each read two registers and write one; `NOT Rd, Ra` inverts all 32 bits. `NOT` has already been discussed as a direct hardware instruction. Alternative: implement only a functionally sufficient subset and synthesize other operations from several instructions; smaller opcode set, longer programs. `AND` is useful for masks in button input registers.

8. **Shifts — provisionally simplified.** Use `SHL1 Rd, Ra` and `SHR1 Rd, Ra`, each moving by one bit. Left shift fills with zero; right shift copies the old top bit, preserving the sign bit. Software repeats a shift for larger distances. There is no direct zero-filling right shift for now; one can be synthesized by masking the top bit after `SHR1`, or reconsidered after sample programs. This replaces the earlier proposal for three shift modes with variable or immediate distances.

## Memory and I/O

9. **Loads and stores — revised provisional choice.** Use `LOAD Rd, [Ra]` and `STORE Rs, [Ra]` for aligned 32-bit word transfers. `Ra` holds the exact byte address; a non-multiple-of-four address is an error. The earlier base-plus-offset operations are removed from the current draft. Software can calculate an offset address with arithmetic. Revisit a direct offset form only if example programs justify it.

10. **Byte order and smaller accesses — deferred.** The current draft supports only aligned 32-bit word loads/stores. Byte and halfword transfers, including signed versus unsigned loads, can be revisited when needed by a program. Byte order is also deferred; it must be settled before smaller transfers are added or binary data formats are standardized. RV32I includes byte, halfword, and word operations in its base ISA.

11. **I/O map.** Proposal: reserve a high region of the data address space for 32-bit peripheral registers; ordinary load/store operations read button state and write output state. Exact addresses depend on the board. Alternative: special I/O instructions or separate I/O address space, adding ISA and bus complexity.

## Control flow

12. **Counted conditions — provisionally chosen.** `IF_EQ`, `IF_NE`, signed `IF_GT`, and unsigned `IF_UGT` each compare two registers and have an unsigned count `N`. If the condition is true, execute the next instruction normally; if false, skip the following `N` machine instructions. Equality and inequality do not depend on signedness. No hidden flags. Alternatives considered: synthesize conditions from fewer instructions or use a compare/flags register.

13. **Forward and backward movement.** Proposal: if the current instruction is at byte address `P`, `GHOST N` sets `PC = P + 4 × (N + 1)` and `REPEAT N` sets `PC = P - 4 × N`. Thus `GHOST 1` skips one following instruction; `REPEAT 1` reruns the previous instruction. `GHOST 0` advances normally; `REPEAT 0` is illegal. Out-of-range targets are errors. Alternative: count from the next PC instead of the current instruction; either convention works if defined consistently. A 16-bit unsigned count would reach up to 65,535 instructions (about 256 KiB), likely beyond the first program memory size.

14. **Assembler labels.** Proposal: assembly source can write `GHOST done` and `REPEAT loop`; the assembler calculates `N`. A counted conditional can also name the first instruction after its controlled block so the assembler calculates its count. The hardware only sees numeric counts. Alternative: programmers write counts by hand, which is simple for the assembler but fragile when lines are inserted or deleted.

15. **Reusable functions and returns — provisionally chosen.** `JUMP_REG Rtarget` jumps to a program address held in a register. `CALL_REG Rtarget, Rlink` reads the old target value, saves `PC + 4` in the chosen link register, then jumps to the target. A return is `JUMP_REG Rlink`; nested calls save the link value in data memory. The target must be an aligned valid program address. Exact encoding and software calling convention are open. Alternatives considered: dedicated `CALL`/`RETURN` with a hardware return stack (more special hardware and a depth limit), or deferring reusable functions. Fixed `GHOST`/`REPEAT` counts alone cannot return to different call sites.

## Completion, errors, and later extensions

16. **Finish and errors — partly reviewed.** Proposal: `HALT` stops instruction execution and exposes a success status for simulation/board debugging; invalid opcode, bad alignment, unmapped data access, and out-of-range PC halt with distinct error status. A dedicated `NOP` is removed because `GHOST 0` already advances PC without changing state. Alternative: programs write status to I/O and spin forever, with errors left unspecified. The explicit statuses are easier to debug. RV32I has `ECALL`/`EBREAK` and a broader execution environment rather than a basic HALT.

17. **Unsigned comparison — provisionally chosen.** `IF_UGT` belongs in the current ISA draft with the same counted-block semantics as signed `IF_GT`, but interprets both registers as unsigned 32-bit values. This is useful when comparing bit patterns, addresses, or sizes in the upper half of the range.

18. **Multiply and divide — provisionally included.** The target ISA includes `MUL` and `DIV` register operations. Their signedness and edge cases need a later review. A multicycle hardware implementation is possible; the first board self-check need not execute them. RISC-V places integer multiply/divide in its optional M extension.

19. **Interrupts and memory ordering.** Proposal: poll input registers in the first CPU; execute all loads/stores in program order with no cache or out-of-order behavior. Add interrupts, trap handlers, and memory fences only when a program or device requires them. Alternative: define them now for stronger general-purpose capability at substantial design cost. This still requires precise error behavior under item 16.

## First review pass

This was the initial review order, before the [complete candidate ISA](isa-complete-draft.md) and its sample program were drafted: **5 (constants), 6 (arithmetic immediate), 7 (bitwise), 12 (conditions), 13 (PC/count semantics), and 16 (finish/errors)**. Item 15 was provisionally selected; it still needs encoding and an implementation. Other items remain proposals until reviewed and recorded in the decision log.
