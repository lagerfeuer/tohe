#!/usr/bin/env python3

import os
import sys
import tempfile
from argparse import ArgumentParser
from colorama import init, Fore, Style
from subprocess import call
from typing import Optional, List

from todd.db import ToddDB

__VERSION__ = '0.1.0'


def ERROR(msg: str) -> None:
    print(Fore.RED + Style.BRIGHT + msg + Style.RESET_ALL)


def call_editor(content: Optional[str] = None) -> str:
    EDITOR = os.environ.get('EDITOR')
    if EDITOR is None:
        raise EnvironmentError('No $EDITOR specified!')
    with tempfile.NamedTemporaryFile(prefix='todd_', suffix='.tmp') as tf:
        if content:
            tf.write(bytes(content, 'utf-8'))
            tf.flush()
        call([EDITOR, tf.name])
        tf.seek(0)
        return tf.read().decode('utf-8')


def main(argv: List[str] = sys.argv) -> None:
    arg_parser = ArgumentParser(
        'todd', description='todd - The TODO list manager')
    arg_parser.add_argument(
        '-v', '--version', action='store_true', help='show version number and exit')

    ops = arg_parser.add_argument_group('OPERATIONS')
    ops.add_argument('-a', '--add', nargs='?',
                     metavar='CONTENT', help='add a new todo', const='_default', default=None)
    ops.add_argument('-e', '--edit', help='edit a todo')
    ops.add_argument('-l', '--list', help='add a new todo',
                     action='store_true', default=False)
    ops.add_argument('-s', '--search', help='search all todos')
    ops.add_argument('-d', '--delete', help='delete todo')

    optops = arg_parser.add_argument_group('OPTIONAL')
    optops.add_argument('-t', '--tag', help='list of tags: -t tag1,tag2')

    args = arg_parser.parse_args()

    if args.version:
        print(__VERSION__)
        sys.exit(0)

    if not any([args.add, args.edit, args.list, args.search, args.delete]):
        ERROR('No arguments given!')
        arg_parser.print_help()
        sys.exit(1)

    TODD = ToddDB()

    if args.add:
        content = call_editor() if args.add == '_default' else args.add
        if args.tag:
            tags = args.tag.split(',')
        # FIXME: find better way to deal with tags
        # else:
        #     tags = call_editor(
        #         '# Enter tags below (one per line):').split('\n')
        #     tags = [t for t in tags if not t.startswith('#')]
        TODD.add(content, tags=tags)

    if args.list:
        todos = TODD.list()
        print(todos)


if __name__ == "__main__":
    main()
