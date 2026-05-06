"""
Main orchestrator. Wires CLI → validation → extraction → export → summary.
"""

import sys
from pathlib import Path

from app.cli import parse_args
from app.services.export_service import build_output_path, export_to_json
from app.services.playlist_extractor import extract_playlist
from app.utils.logging_utils import configure_logging
from app.utils.validators import is_valid_playlist_url


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging(verbose=args.verbose)

    url = args.resolved_url

    if not is_valid_playlist_url(url):
        _print_error(f"Invalid or unsupported playlist URL: {url}")
        _print_error("Expected format: https://www.youtube.com/playlist?list=PLxxxxxxxx")
        return 1

    print(f"Fetching playlist: {url}")

    try:
        playlist_meta, items = extract_playlist(url)
    except RuntimeError as exc:
        _print_error(str(exc))
        return 1
    except Exception as exc:
        _print_error(f"Unexpected error during extraction: {exc}")
        return 1

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = build_output_path(playlist_meta, Path(args.output_dir))

    try:
        export_to_json(playlist_meta, items, output_path)
    except OSError as exc:
        _print_error(f"Failed to write output file: {exc}")
        return 1

    _print_summary(playlist_meta, items, output_path)
    return 0


def _print_summary(playlist_meta, items, output_path) -> None:
    available = [i for i in items if i.availability_status == "available"]
    parsed = [i for i in available if i.artist is not None and i.track is not None]
    unavailable_count = len(items) - len(available)

    print()
    print("─" * 50)
    print(f"  Playlist : {playlist_meta.title}")
    print(f"  Total    : {len(items)} item(s)")
    print(f"  Available: {len(available)}")
    if unavailable_count:
        print(f"  Skipped  : {unavailable_count} (private/removed/unavailable)")
    print(f"  Parsed   : {len(parsed)} with artist + track identified")
    print(f"  Output   : {output_path}")
    print("─" * 50)


def _print_error(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
