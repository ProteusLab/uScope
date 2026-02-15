# Refence Program

- [Reference sample](reference.S) assembly program is designed to test a wide range of [Functional Units in an O3CPU Gem5 simulation](https://github.com/gem5/gem5/blob/stable/src/cpu/o3/FUPool.py).

- It sequentially executes blocks of instructions targeting ```IntALU```, ```IntMultDiv```, ```FP_ALU```, ```FP_MultDiv```, ```SIMD_Unit```, ```ReadPort```, and ```WritePort```. [The resulting O3PipeView trace](reference.json) is used as a reference to verify that PipeViewPerfetto correctly maps all operation classes to their respective functional units in the Perfetto JSON output.

## Usage

### 1. Compile

From the `examples/reference` directory, run:

```bash
riscv64-linux-gnu-gcc reference.S -O0 -march=rv64imafdv -mabi=lp64d -static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles -o reference
```

### 2. Collect an O3PipeView trace with gem5

Navigate to your gem5 build directory and execute:

```bash
/path/to/gem5.opt               \
    --debug-flags=O3PipeView    \
    --debug-file=reference.out  \
    configs/example/se.py       \
    --cpu-type=O3CPU            \
    --caches                    \
    --cmd=/path/to/reference    \
    --mem-size=8GB
```

The trace file reference.out will be created in the gem5 output directory (usually ```m5out/```).

### 3. Convert the trace using PipeViewPerfetto

In the gem5 output directory (e.g., ```m5out```), run tool:

```bash
pipeview-perfetto --input-file reference.out --output reference.json
```

### 4. Visualize the result

Open the generated reference.json in the Perfetto UI. You can also use the built-in Chrome Tracing viewer at chrome://tracing.

### 5. Compare with the reference
A pre‑converted reference JSON (```reference.json```) is provided in this directory.
You can use it to verify that your conversion matches the expected output.
