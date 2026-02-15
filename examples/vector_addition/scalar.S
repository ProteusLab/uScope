.section .data
    .align 4
    array_A: .word 1, 2, 3, 4, 5, 6, 7, 8
    array_B: .word 8, 7, 6, 5, 4, 3, 2, 1

.section .bss
    .align 4
    array_C: .space 32

.section .text
.global _start
_start:
    la x10, array_A
    la x11, array_B
    la x12, array_C
    li x13, 8

loop_scalar:
    lw x14, 0(x10)
    lw x15, 0(x11)
    add x16, x14, x15
    sw x16, 0(x12)

    addi x10, x10, 4
    addi x11, x11, 4
    addi x12, x12, 4
    addi x13, x13, -1
    bnez x13, loop_scalar

    li a0, 0
    li a7, 93
    ecall
