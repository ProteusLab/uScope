# uScope

[![CI](https://github.com/ProteusLab/uScope/actions/workflows/ci.yml/badge.svg)](https://github.com/ProteusLab/uScope/actions/workflows/ci.yml)
[![Research Project](https://img.shields.io/badge/Research-Project-blue)](https://github.com/ProteusLab/uScope)
[![gem5](https://img.shields.io/badge/gem5-simulation-green)](https://www.gem5.org)
[![Computer Architecture](https://img.shields.io/badge/Computer-Architecture-orange)](https://en.wikipedia.org/wiki/Computer_architecture)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen)](https://github.com/ProteusLab/uScope)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

**uScope** gives you a microscopic view of a [gem5](https://www.gem5.org) O3CPU simulation by transforming [PipeView traces]((https://www.gem5.org/documentation/general_docs/cpu_models/visualization/)) into [Perfetto](https://perfetto.dev/) timelines.

Verify, optimize, and explore cycle-approximate simulation with uScope!

<p align="center">
  <img src="images/quick_start.gif" alt="Video">
</p>

## Features

- 📊 **Integration with Perfetto / Chrome Tracing** – leverage a modern, fast visualization platform for in‑depth pipeline analysis.
- 🚀 **Extends gem5's performance analysis** – transform O3PipeView traces into an interactive timeline, offering a novel perspective on verification and performance analysis of PipeView traces..
- 🎯 **Identify compute‑bound and memory‑bound bottlenecks** – visualize pipeline stage occupancy and execution unit utilization to quickly determine whether performance is limited by computation or memory access.
- 🔍 **Interactive exploration** – zoom, pan, and inspect individual instructions in Perfetto.

## Quick Start

```bash
pip install --upgrade pip setuptools wheel
git git@github.com:ProteusLab/uScope.git
cd uScope
pip install -e .
```

## Usage

1. Collect a trace from gem5 with the O3PipeView debug flag:

```bash
/path/to/gem5.opt                   \
    --debug-flags=O3PipeView        \
    --debug-file=trace.out          \
    configs/example/se.py           \
    --cpu-type=O3CPU                \
    --cmd=/path/to/your-program
```

2. Convert the trace:

```bash
uScope --input-file trace.out --output trace.json
```

3. Open ```trace.json``` in Perfetto UI to explore the pipeline.

## Examples

- Explore the [examples/](examples/) directory for assembly programs and their corresponding tracings.

## Contributing
We welcome contributions! Feel free to open issues or submit pull requests.
