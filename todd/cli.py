#!/usr/bin/env python3

import os
import sys
import tempfile
from argparse import ArgumentParser
from colorama import init, Fore, Style
from subprocess import call
from typing import Optional, List
from shutil import get_terminal_size

from todd import __version__
from todd.db import ToddDB
from todd.util.editor import call_editor


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
        prog='todd', description='todd - The TODO list manager')
    arg_parser.add_argument(
        '-v', '--version', action='store_true', help='show version number and exit')

    subparsers = arg_parser.add_subparsers(
        title='Operations', description='modifying the TODOs', dest='operation')

    add_p = subparsers.add_parser(
        'add', help='add todo')
    add_p.add_argument('content', nargs='?', metavar='CONTENT',
                       help='add a new todo (if content is not supplied, $EDITOR will be opened)',
                       const='_default', default=None)
    add_p.add_argument(
        '-t', '--tag', help='tags for the new todo', metavar='TAG', nargs='+', default=[])

    list_p = subparsers.add_parser('list', help='list all todos')
    list_p.add_argument(
        '-t', '--tag', help='filter by tags', metavar='TAG', nargs='+', default=[])

    edit_p = subparsers.add_parser('edit', help='edit a todo')
    edit_p.add_argument('id', help='ID of entry to be modified', metavar='ID')
    edit_p.add_argument('-t', '--tag', help='add tags to entry', nargs='+')
    edit_p.add_argument(
        '-r', '--rtag', help='remove tags from entry', nargs='+', default=[])

    search_p = subparsers.add_parser('search', help='search all todos')
    search_p.add_argument('term', help='search term')

    delete_p = subparsers.add_parser('delete', help='delete a todo')
    delete_p.add_argument('id', help='ID of entry to be deleted', metavar='ID')

    help_p = subparsers.add_parser('help', help='print help message')

    parsers = {'add': add_p, 'list': list_p, 'edit': edit_p,
               'search': search_p, 'delete': delete_p, 'help': help_p}

    args = arg_parser.parse_args()

    if args.version:
        print(__version__)
        sys.exit(0)

    if not args.operation:
        ERROR('No arguments given!')
        arg_parser.print_help()
        sys.exit(1)

    if args.operation == 'help':
        arg_parser.print_help()
        sys.exit(1)

    TODD = ToddDB()

    if args.operation == 'add':
        content = call_editor() if args.content is None else args.content
        tags = args.tag
        TODD.add(content, tags=tags)

    elif args.operation == 'list':
        rows = TODD.list()
        print_rows(rows)

    elif args.operation == 'edit':
        pass
    elif args.operation == 'search':
        pass
    elif args.operation == 'delete':
        pass
    else:
        # unreachable because of argparser
        ERROR("Unrecognized operation '%s'!" % (args.operation,))
        sys.exit(1)


if __name__ == "__main__":
    main()
