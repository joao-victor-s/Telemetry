import argparse
import sys


def get_argparser():
    parser = argparse.ArgumentParser("backend_emulator")

    parser.add_argument(
        "--update-frequency",
        "-f",
        type=float,
        default=1.0,
        help="metric update frequency in seconds",
    )

    return parser


def parse_args():
    parser = get_argparser()
    raw_args = parser.parse_args(sys.argv[1:])

    args = {"update_frequency": raw_args.update_frequency}

    return args
