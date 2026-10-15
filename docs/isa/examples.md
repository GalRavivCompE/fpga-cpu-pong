# Example programs (design sketches)

**Status: not assembled, simulated, or run on a board.** These examples use the current [instruction reference](reference.md) to test whether the proposed ISA is practical to program. Labels and comments are assembly conveniences; binary encoding is specified, but an assembler does not exist yet. Both examples start after reset, when the current candidate's registers and PC are zero.

## Sum a length-prefixed list

Data memory at address 256 holds the number of elements. Elements begin at addresses 260, 264, 268, and so on. The result ends in R1. R0 stays zero for the comparison. `ADD_CONST` avoids keeping constants 4 and 1 in separate registers.

```text
DUPE R1, R0             ; sum = zero
SET_LOW R2, 256         ; address of the list length
READ R3, [R2]           ; remaining element count
ADD_CONST R2, R2, 4     ; address of the first element
loop:
IF_EQ R3, R0, 1         ; when count is zero, execute GHOST
GHOST done             ; otherwise IF_EQ skips this instruction
READ R4, [R2]
ADD R1, R1, R4
ADD_CONST R2, R2, 4
ADD_CONST R3, R3, -1
REPEAT loop            ; assembler would calculate the count
done:
HALT
```

`IF_EQ` controls one following machine instruction, which is the `GHOST`. The loop checks the count before reading an element, so a zero-length list halts with sum zero. This example has not been executed; a simulator should test zero, one, and several elements, plus arithmetic wraparound.

## Mirror one button bit to an output

The addresses are **illustrative**, not a chosen board's memory map. Suppose the button bits are at data address `0xFFFF0000` and output bits at `0xFFFF0004`. The CPU polls input, masks bit 0, and writes the result. Supporting hardware supplies the input bits and drives the physical output.

```text
SET_LOW R2, 0
SET_HIGH R2, 0xFFFF    ; R2 = input address 0xFFFF0000
SET_LOW R3, 4
SET_HIGH R3, 0xFFFF    ; R3 = output address 0xFFFF0004
SET_LOW R4, 1          ; mask for button bit 0
loop:
READ R1, [R2]
AND R1, R1, R4
WRITE R1, [R3]
REPEAT loop
```

This loop does not reach `HALT` during normal operation. A future board test can map the output to an LED. For a Pong-like program, software would also update ball and paddle state, handle collisions and scores, and write game-state registers; hardware could turn those registers into pixels.

## Read one byte from a packed word

Suppose data memory contains the 32-bit word `0x44332211` at byte address 256. With little-endian layout, address 257 holds `0x22`.

```text
SET_LOW R2, 257
READ_BYTE R1, [R2]     ; R1 = 0x00000022
HALT
```

This is a design sketch. It assumes the upper half of R2 is zero after reset; otherwise `SET_HIGH R2, 0` is also needed. A simulator should check reads at addresses 256, 257, 258, and 259, including the zero-filled upper 24 bits.

## Calling convention remains open

`CALL target_reg, link_reg` saves the byte address of the following instruction in `link_reg`; `LEAP link_reg` returns. One proposal is to use R7 as the usual link register. A nested call would save its incoming link value in data memory and restore it before returning. Argument, result, and stack conventions need a worked example before they are adopted.
