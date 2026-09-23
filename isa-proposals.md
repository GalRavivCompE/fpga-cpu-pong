# ISA functionality options and review notes

For the current instruction index, syntax, and behavior, see the [instruction set reference](isa-reference.md). For an end-to-end design draft and example programs, see [Complete candidate ISA, revision 0.2](isa-complete-draft.md). This numbered file preserves the original alternatives and decision history.

**Status: option history, not the authoritative ISA specification.** Prepared 2026-09-22 from the [gap audit](isa-gap-audit.md) and updated during review. The [decision log](decisions.md) records current scope; the [complete candidate ISA](isa-complete-draft.md) lists the proposed v1 instructions. No ISA encoding, assembler, or RTL is implemented. Names remain provisional.

The comparison baseline is [RISC-V RV32I](https://docs.riscv.org/reference/isa/v20240411/unpriv/rv32.html). Its optional extensions are described in the [ISA introduction](https://docs.riscv.org/reference/isa/v20240411/unpriv/intro.html). The aim is a coherent custom CPU, without RISC-V compatibility as a requirement.

## Machine state and instruction format

1. **Registers and reset.** Current candidate: eight writable 32-bit registers `A`–`H`; a 32-bit program counter (PC); on reset, PC and all registers become zero. No register is hardwired to zero. Sixteen writable registers are an open alternative pending sample programs and hardware constraints; reserved constant registers are set aside for now. Leaving register contents unspecified after reset was another option, but zeroing registers makes early debugging more predictable. RV32I instead has a hardwired zero register and more total registers.

2. **Instruction word and fields.** Proposal: every instruction occupies one 32-bit word at a four-byte-aligned program address. With eight registers, a feasibility sketch uses a 6-bit opcode, up to three 3-bit register fields, and a 16-bit immediate/count field; unused bits must be zero. This is **not an assigned encoding**. Sixteen registers would require 4-bit register identifiers; three-register operations and immediate operations could use different field layouts within the same 32-bit instruction width. Exact bit positions and opcode values remain open.

3. **Instruction and data spaces.** Proposal: the PC fetches only from program memory; loads/stores access only data memory and mapped I/O. Both spaces use byte addresses. The first physical implementation can use a program ROM and data RAM. Alternative: one shared ISA address space, allowing programs to read code as data but needing more memory-system design. This choice is already provisional in the decision log.

## Values and calculation

4. **Basic arithmetic.** Proposal: `ADD dst, src1, src2` and `SUB dst, src1, src2`; each writes the low 32 bits. Signed values use two's complement. The two-operand spelling `ADD dst, src2` or `SUB dst, src2` is an assembler shorthand with `src1=dst`, not another hardware opcode. Alternative: separate two-operand opcodes, which would still occupy 32 bits each unless given another useful encoding advantage.

5. **Constants — revised provisional choice.** `SET_LOW dst, imm16` replaces bits 15:0 and preserves bits 31:16; `SET_HIGH dst, imm16` does the converse. Together they construct any 32-bit pattern from an unknown register value. This replaces the earlier sign-extending `SET_CONST` behavior so the two half-setting instructions form a symmetric pair. A small negative value such as -1 now requires both halves unless the untouched half is already known. A stored constant table remains available in data memory.

6. **Arithmetic with a constant — provisionally chosen.** `ADD_CONST dst, src1, imm16` adds a signed 16-bit immediate modulo 2^32. A negative immediate also performs subtraction, so no separate `SUB_CONST` is needed. This is not needed for computational completeness, but it saves registers and setup instructions in the list-sum example. The name replaces the confusing `ADD_SMALL` working name.

7. **Bitwise operations.** Proposal: `AND`, `OR`, and `XOR` each read two registers and write one; `NOT dst, src1` inverts all 32 bits. `NOT` has already been discussed as a direct hardware instruction. Alternative: implement only a functionally sufficient subset and synthesize other operations from several instructions; smaller opcode set, longer programs. `AND` is useful for masks in button input registers.

8. **Shifts — revised provisional choice.** Use `LSHIFT dst, src1, src2`, `RSHIFT dst, src1, src2`, and `RSHIFT_SIGN dst, src1, src2`. The second source register holds an unsigned shift distance. Left and ordinary right shift fill with zero; `RSHIFT_SIGN` copies the old top bit into open positions. A zero distance copies the value; distances of 32 or more produce zero or a full sign-bit pattern as appropriate. This replaces the earlier fixed one-bit form. The CPU may use a multicycle shifter or a faster barrel shifter; choose after hardware exploration. Alternate left-fill and rotate operations are excluded from v1.

## Memory and I/O

9. **Loads and stores — accepted v1 scope.** Use `READ dst, [src1]` and `WRITE src, [src1]` for aligned 32-bit word transfers. `src1` holds the exact byte address; a non-multiple-of-four address is an error. Base-plus-offset operations are excluded from v1. Software calculates an offset address with arithmetic.

10. **Byte order and smaller accesses — excluded from v1.** Version 1 supports only aligned 32-bit word loads/stores. Byte and halfword transfers, including signed versus unsigned loads, are outside its opcode set. Byte order must be settled in an explicit future version before smaller transfers or binary data formats are standardized. RV32I includes byte, halfword, and word operations in its base ISA.

11. **I/O map.** Proposal: reserve a high region of the data address space for 32-bit peripheral registers; ordinary load/store operations read button state and write output state. Exact addresses depend on the board. Alternative: special I/O instructions or separate I/O address space, adding ISA and bus complexity.

## Control flow

12. **Counted conditions — accepted v1 form.** `IF_EQ`, `IF_NE`, signed `IF_GT`, and unsigned `IF_UGT` each compare two registers and require an explicit unsigned count `N`. If the condition is true, execute the next instruction normally; if false, skip the following `N` machine instructions. Equality and inequality do not depend on signedness. No hidden flags or implicit-count shorthand. Alternatives considered: synthesize conditions from fewer instructions or use a compare/flags register.

13. **Forward and backward movement — accepted v1 count source.** If the current instruction is at byte address `P`, `GHOST N` sets `PC = P + 4 × (N + 1)` and `REPEAT N` sets `PC = P - 4 × N`. Thus `GHOST 1` skips one following instruction; `REPEAT 1` reruns the previous instruction. `GHOST 0` advances normally; `REPEAT 0` is illegal. `N` is encoded as a fixed number, not read from a register. Out-of-range targets are errors. A 16-bit unsigned count reaches up to 65,535 instructions (about 256 KiB), likely beyond the first program memory size.

14. **Assembler labels.** Proposal: assembly source can write `GHOST done` and `REPEAT loop`; the assembler calculates `N`. A counted conditional can also name the first instruction after its controlled block so the assembler calculates its count. The hardware only sees numeric counts. Alternative: programmers write counts by hand, which is simple for the assembler but fragile when lines are inserted or deleted.

15. **Reusable functions and returns — provisionally chosen.** `LEAP target_reg` jumps to a program address held in a register. `CALL target_reg, link_reg` reads the old target value, saves `PC + 4` in the chosen link register, then jumps to the target. A return is `LEAP link_reg`; nested calls save the link value in data memory. The target must be an aligned valid program address. Exact encoding and software calling convention are open. Alternatives considered: a paired call/return mechanism with a hardware return stack (more special hardware and a depth limit), or deferring reusable functions. Fixed `GHOST`/`REPEAT` counts alone cannot return to different call sites.

## Completion, errors, and later extensions

16. **Finish and errors — provisionally chosen.** `HALT` stops successfully; `FAIL` lets software report a failed self-check and stop. Invalid opcode, bad alignment, unmapped data access, and out-of-range PC stop automatically with a distinct hardware fault cause. A dedicated `NOP` is removed because `GHOST 0` already advances PC without changing state. A continuing `ERR_WARNING` is excluded from v1. RV32I instead has `ECALL`/`EBREAK` and a broader execution environment.

17. **Unsigned comparison — provisionally chosen.** `IF_UGT` belongs in the current ISA draft with the same counted-block semantics as signed `IF_GT`, but interprets both registers as unsigned 32-bit values. This is useful when comparing bit patterns, addresses, or sizes in the upper half of the range.

18. **Multiply, divide, and remainder — provisionally chosen.** The target ISA includes `MUL`, `DIV`, and `MOD` register operations. `MUL` keeps the low 32 bits. `DIV` uses signed two's-complement operands and truncates toward zero. `MOD` returns the corresponding signed remainder, so `-17 MOD 5 = -2`. A zero divisor causes a hardware fault for `DIV` or `MOD`; `-2147483648 / -1` wraps to `0x80000000` and has remainder zero. A multicycle implementation may let `DIV` and `MOD` share hardware; the first board self-check need not execute them. RISC-V places integer multiply/divide in its optional M extension.

19. **Interrupts and memory ordering.** Proposal: poll input registers in the first CPU; execute all loads/stores in program order with no cache or out-of-order behavior. Add interrupts, trap handlers, and memory fences only when a program or device requires them. Alternative: define them now for stronger general-purpose capability at substantial design cost. This still requires precise error behavior under item 16.

20. **Program-counter read — selected for candidate ISA.** `COUNT dst` writes the current instruction's PC byte address to `dst` and then advances normally. `LINE_COUNT` was considered but could be confused with source-code lines. Astro8 calls the comparable operation `PCR`. A fixed program can construct absolute addresses instead, but `COUNT` makes location-relative code easier to write. Exact encoding remains open.

## First review pass

This was the initial review order, before the [complete candidate ISA](isa-complete-draft.md) and its example programs were drafted: **5 (constants), 6 (arithmetic immediate), 7 (bitwise), 12 (conditions), 13 (PC/count semantics), and 16 (finish/errors)**. The current status of each choice is in the [decision log](decisions.md). No choice is marked *working* without an implementation test.
