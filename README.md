# PipeViewPerfetto

[![Research Project](https://img.shields.io/badge/Research-Project-blue)](https://github.com/ProteusLab/PipeViewPerfetto)
[![gem5](https://img.shields.io/badge/gem5-simulation-green)](https://www.gem5.org)
[![Computer Architecture](https://img.shields.io/badge/Computer-Architecture-orange)](https://en.wikipedia.org/wiki/Computer_architecture)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen)](https://github.com/ProteusLab/PipeViewPerfetto)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

<p align="center">
  <img src="images/quick_start.gif" alt="Video">
</p>

**PipeViewPerfetto** converts the [O3PipeView debug output](https://www.gem5.org/documentation/general_docs/cpu_models/visualization/) from the [gem5](https://www.gem5.org) simulator into a JSON trace that can be loaded into [Perfetto](https://perfetto.dev/) (or any Chrome Tracing viewer).

This gives researchers an interactive, zoomable timeline of O3CPU pipeline stages and execution unit occupancy, making microarchitectural analysis much easier.

## Features

- 🔗 **Integration with Perfetto / Chrome Tracing** – leverage a modern, fast visualization platform for in‑depth pipeline analysis.
- 🚀 **Extends gem5's performance analysis capabilities** – transform textual O3PipeView logs into an interactive timeline, making it easier to spot microarchitectural inefficiencies.
- 🎯 **Identify compute‑bound and memory‑bound bottlenecks** – visualize pipeline stage occupancy and execution unit utilization to quickly determine whether performance is limited by computation or memory access.
- 🔍 **Interactive exploration** – zoom, pan, and inspect individual instructions in Perfetto.

## Quick Start

```bash
pip install --upgrade pip setuptools wheel
git clone https://github.com/ProteusLab/PipeViewPerfetto.git
cd PipeViewPerfetto
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
pipeview-perfetto --input-file trace.out --output trace.json
```

3. Open ```trace.json``` in Perfetto UI to explore the pipeline.

## Examples

- Check the [examples/](examples/) directory for assembly programs and their corresponding tracings.

## Current Status & Roadmap

✅ Standalone converter.

🚧 Planned: Native integration into gem5 as a new --debug-flag option to generate Perfetto JSON directly during simulation.

## Contributing
We welcome contributions! Feel free to open issues or submit pull requests.
