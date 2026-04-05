"""CLI entry point (deprecated — use FastAPI app instead)."""
import sys
import argparse

parser = argparse.ArgumentParser(description="UI Test Generator CLI (deprecated)")
parser.add_argument('--generate', action='store_true', help='(deprecated — use POST /generate)')
parser.add_argument('--continue', dest='continue_file', metavar='EXCEL_FILE', help='(deprecated — use POST /continue)')
args = parser.parse_args()

if args.generate or args.continue_file:
    print("CLI is deprecated. Please use the FastAPI app at http://localhost:8000/docs")
else:
    parser.print_help()
    sys.exit(1)
