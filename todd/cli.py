#!/usr/bin/env python3

import os
import sys
import tempfile
from argparse import ArgumentParser
from colorama import init, Fore, Style
from subprocess import call
from typing import Optional, List
from shutil import get_terminal_size

from todd.db import ToddDB

__VERSION__ = '0.1.0'


def id_style(txt, rjust=0):
    if rjust > 0:
        txt = txt.rjust(rjust)
    return Fore.BLUE + Style.BRIGHT + txt + Style.RESET_ALL


def todo_style(txt, max_length):
    if len(txt) >= max_length:
        txt = txt[:max_length - 4] + '...'
    return Fore.RED + Style.BRIGHT + txt + Style.RESET_ALL


def tags_style(tags, sign='#', rjust=0, join_char=','):
    txt = join_char.join(tags) if tags else ''
    if rjust > 0:
        sign = sign.rjust(rjust)
    return Fore.GREEN + Style.BRIGHT + sign + ' ' + Fore.CYAN + txt + Style.RESET_ALL


def ERROR(msg: str) -> None:
    print(Fore.RED + Style.BRIGHT + msg + Style.RESET_ALL)


def print_rows(rows):
    longest_id = len(str(rows[-1][0])) + 1
    term_width = get_terminal_size()[0]
    for row in rows:
        (id, todo, tags) = row
        id = id_style(str(id), rjust=longest_id)
        todo = todo_style(todo, term_width)
        tags = tags_style(tags, rjust=longest_id)

        print(id, end=' ')
        print(todo, end=('' if todo.endswith('\n') else '\n'))
        print(tags)


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
        rows = TODD.list()
        print_rows(rows)


if __name__ == "__main__":
    main()
