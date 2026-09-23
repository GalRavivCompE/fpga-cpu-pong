# Example programs (design sketches)

**Status: not assembled, simulated, or run on a board.** These examples use the current [instruction reference](reference.md) to test whether the proposed ISA is practical to program. Labels and comments are assembly conveniences; binary encoding and an assembler do not exist yet. Both examples start after reset, when the current candidate's registers and PC are zero.

## Sum a length-prefixed list

Data memory at address 256 holds the number of elements. Elements begin at addresses 260, 264, 268, and so on. The result ends in A. H stays zero for the comparison. `ADD_CONST` avoids keeping constants 4 and 1 in separate registers.

```text
SET_LOW A, 0           ; sum
SET_LOW H, 0           ; constant zero
SET_LOW B, 256         ; address of the list length
READ C, [B]            ; remaining element count
ADD_CONST B, B, 4      ; address of the first element
loop:
IF_EQ C, H, 1          ; when count is zero, execute GHOST
GHOST done             ; otherwise IF_EQ skips this instruction
READ D, [B]
ADD A, A, D
ADD_CONST B, B, 4
ADD_CONST C, C, -1
REPEAT loop            ; assembler would calculate the count
done:
HALT
```

`IF_EQ` controls one following machine instruction, which is the `GHOST`. The loop checks the count before reading an element, so a zero-length list halts with sum zero. This example has not been executed; a simulator should test zero, one, and several elements, plus arithmetic wraparound.

## Mirror one button bit to an output

The addresses are **illustrative**, not a chosen board's memory map. Suppose the button bits are at data address `0xFFFF0000` and output bits at `0xFFFF0004`. The CPU polls input, masks bit 0, and writes the result. Supporting hardware supplies the input bits and drives the physical output.

```text
SET_LOW B, 0
SET_HIGH B, 0xFFFF     ; B = input address 0xFFFF0000
SET_LOW C, 4
SET_HIGH C, 0xFFFF     ; C = output address 0xFFFF0004
SET_LOW D, 1           ; mask for button bit 0
loop:
READ A, [B]
AND A, A, D
WRITE A, [C]
REPEAT loop
```

This loop does not reach `HALT` during normal operation. A future board test can map the output to an LED. For a Pong-like program, software would also update ball and paddle state, handle collisions and scores, and write game-state registers; hardware could turn those registers into pixels.

## Calling convention remains open

`CALL target_reg, link_reg` saves the byte address of the following instruction in `link_reg`; `LEAP link_reg` returns. One proposal is to use G as the usual link register. A nested call would save its incoming link value in data memory and restore it before returning. Argument, result, and stack conventions need a worked example before they are adopted.
