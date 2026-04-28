"""CLI interface for SwayCap"""

import argparse
import sys
from . import capture

def create_parser():
    parser = argparse.ArgumentParser(
        prog='swaycap',
        description='Screen capture tool for Sway/Wayland'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    capture_parser = subparsers.add_parser('capture', help='Capture screenshot or video')
    capture_parser.add_argument('--screenshot', action='store_true', help='Capture screenshot')
    capture_parser.add_argument('--video', action='store_true', help='Record video')
    capture_parser.add_argument('--fullscreen', action='store_true', help='Capture full screen')
    capture_parser.add_argument('--window', action='store_true', help='Capture active window')
    capture_parser.add_argument('--area', action='store_true', help='Capture selected area')
    capture_parser.add_argument('--stop', action='store_true', help='Stop recording')

    subparsers.add_parser('gui', help='Launch GUI')

    subparsers.add_parser('stop', help='Stop active recording')

    return parser

def run_capture(args):
    if args.stop:
        capture.stop_recording()
        return

    if not args.screenshot and not args.video:
        print("Error: Specify --screenshot or --video")
        sys.exit(1)

    if args.video and args.window:
        print("Error: Video recording does not support window capture. Use --fullscreen or --area.")
        sys.exit(1)

    if not args.fullscreen and not args.window and not args.area:
        print("Error: Specify --fullscreen, --window, or --area")
        sys.exit(1)

    capture_type = None
    if args.fullscreen:
        capture_type = 'fullscreen'
    elif args.window:
        capture_type = 'window'
    elif args.area:
        capture_type = 'area'

    if args.screenshot:
        capture.screenshot(capture_type)
    elif args.video:
        capture.video(capture_type)

def run_stop(args):
    capture.stop_recording()

def main(args=None):
    parser = create_parser()
    parsed = parser.parse_args(args)

    if parsed.command == 'capture':
        run_capture(parsed)
    elif parsed.command == 'stop':
        run_stop(parsed)
    elif parsed.command == 'gui':
        from . import gui
        gui.main()
    elif parsed.command is None:
        parser.print_help()
    else:
        parser.print_help()