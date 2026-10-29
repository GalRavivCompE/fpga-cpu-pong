; A length-prefixed list starts at data address 256.
; The list values are loaded into simulator RAM before execution.
DUPE R1, R0             ; sum = 0
SET_LOW R2, 256         ; address of the length word
READ R3, [R2]           ; number of items left
ADD_CONST R2, R2, 4     ; first element address
loop:
IF_EQ R3, R0, 1         ; if done, execute GHOST
GHOST done             ; jump forward to HALT
READ R4, [R2]
ADD R1, R1, R4
ADD_CONST R2, R2, 4
ADD_CONST R3, R3, -1
REPEAT loop
done:
HALT
