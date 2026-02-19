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
    li t0, 8
    vsetvli t0, t0, e32, m1, ta, ma

    la x10, array_A
    la x11, array_B
    la x12, array_C

    vle32.v v1, (x10)
    vle32.v v2, (x11)
    vadd.vv v3, v1, v2
    vse32.v v3, (x12)

    li a0, 0
    li a7, 93
    ecall
