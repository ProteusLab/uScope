.section .data
    .align 4
    int_a:  .word 10, 20
    int_b:  .word 5, 4
    int_c:  .space 32

    .align 4
    fp_a:   .float 1.0, 2.0
    fp_b:   .float 0.125, 0.0625
    fp_c:   .space 32

    .align 4
    vec_a:  .word 100, 200
    vec_b:  .word 1, 2
    vec_c:  .space 32

.section .text
.global _start
_start:
    # IntALU
    la   x10, int_a
    la   x11, int_b
    la   x12, int_c
    li   x13, 2

int_alu_loop:
    lw   x14, 0(x10)     # ReadPort
    lw   x15, 0(x11)     # ReadPort
    add  x16, x14, x15   # IntALU
    sub  x17, x14, x15   # IntALU
    and  x18, x14, x15   # IntALU
    or   x19, x14, x15   # IntALU
    sw   x20, 0(x12)     # WritePort

    addi x10, x10, 4
    addi x11, x11, 4
    addi x12, x12, 4
    addi x13, x13, -1
    bnez x13, int_alu_loop

    # IntMultDiv
    la   x10, int_a
    la   x11, int_b
    li   x13, 2

int_mul_loop:
    lw   x14, 0(x10)     # ReadPort
    lw   x15, 0(x11)     # ReadPort
    mul  x16, x14, x15   # IntMult
    div  x17, x14, x15   # IntDiv
    sw   x18, 0(x12)     # WritePort

    addi x10, x10, 4
    addi x11, x11, 4
    addi x13, x13, -1
    bnez x13, int_mul_loop

    # FP_ALU
    la   x10, fp_a
    la   x11, fp_b
    la   x12, fp_c
    li   x13, 2

fp_alu_loop:
    flw  f0, 0(x10)      # ReadPort
    flw  f1, 0(x11)      # ReadPort
    fadd.s f2, f0, f1    # FloatAdd
    fsub.s f3, f0, f1    # FloatAdd
    feq.s x14, f0, f1    # FloatCmp
    fsw  f2, 0(x12)      # WritePort
    addi x12, x12, 4
    fsw  f3, 0(x12)      # WritePort
    addi x12, x12, 4

    addi x10, x10, 4
    addi x11, x11, 4
    addi x13, x13, -1
    bnez x13, fp_alu_loop

    # FP_MultDiv
    la   x10, fp_a
    la   x11, fp_b
    la   x12, fp_c
    li   x13, 2

fp_mul_loop:
    flw  f0, 0(x10)      # ReadPort
    flw  f1, 0(x11)      # ReadPort
    fmul.s f2, f0, f1    # FloatMult
    fdiv.s f3, f0, f1    # FloatDiv
    fsw  f2, 0(x12)      # WritePort
    addi x12, x12, 4
    fsw  f3, 0(x12)      # WritePort
    addi x12, x12, 4

    addi x10, x10, 4
    addi x11, x11, 4
    addi x13, x13, -1
    bnez x13, fp_mul_loop

    # 5. SIMD_Unit
    la   x10, vec_a
    la   x11, vec_b
    la   x12, vec_c
    li   t0, 4
    vsetvli t0, t0, e32, m1, ta, ma

    vle32.v v1, (x10)      # ReadPort
    vle32.v v2, (x11)      # ReadPort
    vadd.vv v3, v1, v2     # SimdAdd
    vmul.vv v4, v1, v2     # SimdMult
    vse32.v v3, (x12)      # WritePort
    addi x12, x12, 32
    vse32.v v4, (x12)      # WritePort

    li   a0, 0
    li   a7, 93
    ecall
