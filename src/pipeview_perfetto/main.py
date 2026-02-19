#!/usr/bin/env python3

import argparse
import sys
import json
from pathlib import Path
import logging

from .parser import PipeViewParser
from .converter import ChromeTracingConverter
from .config import load_config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
        description="Convert gem5 O3PipeView trace to Perfetto / Chrome Tracing JSON format."
    )
    parser.add_argument(
        "--input-file", '-i',
        help="Path to the input trace file (e.g., trace.out)"
    )
    parser.add_argument(
        "--output-file", "-o",
        help="Output JSON file name. If not specified, it will be derived from input_file"
    )
    parser.add_argument(
        "--config-path", "-c",
        type=Path,
        default=None,
        help="Directory containing configuration JSON files. "
             "If not provided, uses './configs' relative to the script."
    )
    parser.add_argument(
        "--exclude-pipeline",
        default=False,
        help="Exclude Pipeline events in the converter",
        action='store_true',
    )
    parser.add_argument(
        "--exclude-exec",
        default=False,
        help="Exclude FuncUnits events in the converter",
        action='store_true',
    )

    args = parser.parse_args()

    input_file = args.input_file

    if args.output_file:
        output_file = args.output_file
    else:
        if input_file.endswith('.out'):
            output_file = input_file[:-4] + '.json'
        else:
            output_file = input_file + '.json'

    logging.warning(f"Parsing {input_file}")
    trace_parser = PipeViewParser()
    trace_parser.parse_file(input_file)

    if not trace_parser.instructions:
        logging.error("Error: No instructions with valid timestamps found!")
        sys.exit(1)

    logging.warning(f"Loading configuration from {args.config_path if args.config_path else 'default location'}")

    config = load_config(args.config_path)

    converter = ChromeTracingConverter(trace_parser, config, args.exclude_exec, args.exclude_pipeline)
    events = converter.convert()

    logging.warning(f"Loading {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2)

    logging.warning(f"Total events: {len(events)}")

if __name__ == "__main__":
    main()
