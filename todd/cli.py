#!/usr/bin/env python3

import sys

from argparse import ArgumentParser

__VERSION__ = '0.0.1'


def main(argv=sys.argv):
    arg_parser = ArgumentParser(
        'todd', description='todd - The TODO list manager')
    arg_parser.add_argument('-v', '--version', action='store_true', help='show version number and exit')
    ops = arg_parser.add_argument_group('operations')
    ops.add_argument('-a', '--add')

    args = arg_parser.parse_args()

    if args.version:
        print(__VERSION__)
        sys.exit(0)


if __name__ == "__main__":
    main()
