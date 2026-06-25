#!/usr/bin/env python3

import argparse
import os
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


def _make_output_path(output_dir: str, input_stem: str, core_id: int, gzip_enabled: bool) -> str:
    output = str(Path(output_dir) / f"{input_stem}_{core_id}.json")
    if gzip_enabled:
        output += '.gz'
    return output


def _convert_and_dump(
    trace_parser: PipeViewParser,
    config,
    args,
    output_file: str,
    progress: bool,
):
    converter = ChromeTracingConverter(
        trace_parser, config,
        args.exclude_exec, args.exclude_pipeline,
        args.only_committed, args.store_completions,
    )
    events = converter.convert(progress=progress)
    logger.info(f"Writing {output_file}")
    with (gzip.open if args.gzip else open)(output_file, 'wt', encoding='utf-8') as f:
        json.dump(events, f, indent=2)
    return len(events)

def main():
    parser = argparse.ArgumentParser(
        description="Convert gem5 O3PipeView trace to Perfetto / Chrome Tracing JSON format."
    )
    parser.add_argument(
        "--input-file", '-i',
        required=True,
        help="Path to the input trace file (e.g., trace.out)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=".",
        help="Output directory for JSON traces. Defaults to current directory."
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
    parser.add_argument(
        "--quiet", "-q",
        default=False,
        action="store_true",
        help="Suppress progress bar and reduce log output"
    )
    parser.add_argument(
        "--only-committed",
        default=False,
        action="store_true",
        help="Exclude squashed (incomplete) instructions from output"
    )
    parser.add_argument(
        "--store-completions",
        default=True,
        action="store_true",
        help="Include store completion tick events (enabled by default)"
    )
    parser.add_argument(
        "--no-store-completions",
        dest="store_completions",
        action="store_false",
        help="Disable store completion tick events"
    )


    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    input_file = args.input_file
    output_dir = args.output_dir

    try:
        if not Path(input_file).exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        os.makedirs(output_dir, exist_ok=True)

        logger.info(f"Parsing {input_file}")
        trace_parser = PipeViewParser()
        trace_parser.parse_file(input_file)

        if not trace_parser.instructions:
            raise ValueError("No instructions with valid timestamps found")

        logger.info(f"Loading configuration from {args.config_path if args.config_path else 'default location'}")
        config = load_config(args.config_path)

        all_instructions = trace_parser.instructions
        core_ids = trace_parser.get_core_ids()
        input_stem = Path(input_file).stem
        progress = not args.quiet

        if len(core_ids) == 1:
            core_id = core_ids[0]
            core_output = _make_output_path(output_dir, input_stem, core_id, args.gzip)
            total = _convert_and_dump(trace_parser, config, args, core_output, progress)
            logger.info(f"Total events: {total}")
        else:
            logger.info(f"Detected {len(core_ids)} cores: {core_ids}")
            for core_id in core_ids:
                trace_parser.instructions = {
                    seq: instr
                    for seq, instr in all_instructions.items()
                    if instr.core_id == core_id
                }
                core_output = _make_output_path(output_dir, input_stem, core_id, args.gzip)
                total = _convert_and_dump(trace_parser, config, args, core_output, progress)
                logger.info(f"Core {core_id}: {total} events")

    except ValueError as e:
        logging.error(f"Value error: {e}")
        sys.exit(1)

    except FileNotFoundError as e:
        logging.error(f"File error: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
