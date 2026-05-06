"""
CLI entry point. Parses arguments and delegates execution to main().
"""

import argparse
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="fetch-video-data-ytb",
        description="Extract YouTube playlist metadata and save to a local JSON file.",
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="YouTube playlist URL",
    )
    parser.add_argument(
        "--url",
        dest="url_flag",
        metavar="URL",
        help="YouTube playlist URL (alternative flag form)",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        help="Override output file path (default: outputs/<title>__<id>.json)",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        default="outputs",
        help="Directory for the output file (default: outputs/)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args(argv)

    # Resolve URL from positional or flag — flag wins if both given
    args.resolved_url = args.url_flag or args.url
    if not args.resolved_url:
        parser.error("A playlist URL is required. Pass it as a positional argument or with --url.")

    return args
