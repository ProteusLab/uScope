#!/usr/bin/env python3

import argparse
import sys
import json
import logging
import gzip

from pathlib import Path

from . import __version__
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
        help="Exclude Functional Units events in the converter",
        action='store_true',
    )
    parser.add_argument(
        "--gzip", "-z",
        default=False,
        action="store_true",
        help="Compress output JSON with gzip"
    )
    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"uScope {__version__}",
        help="Show version and exit"
    )
    parser.add_argument(
        "--verbose", "-v",
        default=False,
        action="store_true",
        help="Enable verbose (DEBUG level) output"
    )


    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    input_file = args.input_file

    if args.output_file:
        output_file = args.output_file
    else:
        if input_file.endswith('.out'):
            output_file = input_file[:-4] + '.json'
        else:
            output_file = input_file + '.json'

    if args.gzip and not output_file.endswith('.gz'):
        output_file += '.gz'

    try:
        if not Path(input_file).exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        logger.info(f"Parsing {input_file}")
        trace_parser = PipeViewParser()
        trace_parser.parse_file(input_file)

        if not trace_parser.instructions:
            raise ValueError("No instructions with valid timestamps found")

        logger.info(f"Loading configuration from {args.config_path if args.config_path else 'default location'}")

        config = load_config(args.config_path)

        converter = ChromeTracingConverter(trace_parser, config, args.exclude_exec, args.exclude_pipeline)
        events = converter.convert()

        logger.info(f"Writing {output_file}")

        with (gzip.open if args.gzip else open)(output_file, 'wt', encoding='utf-8') as f:
            json.dump(events, f, indent=2)

        logger.info(f"Total events: {len(events)}")

    except ValueError as e:
        logging.error(f"Value error: {e}")
        sys.exit(1)

    except FileNotFoundError as e:
        logging.error(f"File error: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
