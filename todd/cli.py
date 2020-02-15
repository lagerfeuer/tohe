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
from todd.util.editor import call_editor

__VERSION__ = '0.1.0'


def id_style(txt, rjust=0):
    if rjust > 0:
        txt = txt.rjust(rjust)
    return Fore.BLUE + txt + '.' + Style.RESET_ALL


def todo_style(txt, max_length):
    txt = txt.split('\n')[0]
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
        tags = tags_style(tags, rjust=longest_id + 1)

        print(id, end=' ')
        print(todo, end=('' if todo.endswith('\n') else '\n'))
        print(tags)


def main(argv: List[str] = sys.argv) -> None:
    arg_parser = ArgumentParser(
        'todd', description='todd - The TODO list manager')
    arg_parser.add_argument(
        '-v', '--version', action='store_true', help='show version number and exit')

    ops = arg_parser.add_argument_group('OPERATIONS')
    ops.add_argument('-a', '--add', nargs='?', metavar='CONTENT',
                     help='add a new todo: if content is not supplied, $EDITOR will be opened',
                     const='_default', default=None)
    ops.add_argument('-l', '--list', help='list all todos',
                     action='store_true', default=False)
    ops.add_argument('-e', '--edit', help='edit a todo', metavar='ID')
    ops.add_argument('-s', '--search', help='search all todos: TERM can be a phrase, word or tag',
                     metavar='TERM')
    ops.add_argument('-d', '--delete',
                     help='delete todo by ID or tag', metavar='(ID|tag)')

    optops = arg_parser.add_argument_group('OPTIONAL')
    optops.add_argument(
        '-t', '--tag', help='add list of tags: -t tag1,tag2', metavar='TAGS')
    optops.add_argument(
        '-nt', '--notag', help='delete list of tags: -t tag1,tag2', metavar='TAGS')

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
        # FIXME: find better way to deal with tags
        # else:
        #     tags = call_editor(
        #         '# Enter tags below (one per line):').split('\n')
        #     tags = [t for t in tags if not t.startswith('#')]
        tags = args.tag.split(',') if args.tag else []
        TODD.add(content, tags=tags)

    elif args.list:
        rows = TODD.list()
        print_rows(rows)

    elif args.edit:
        pass
    elif args.search:
        pass
    elif args.delete:
        pass
    else:
        arg_parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
