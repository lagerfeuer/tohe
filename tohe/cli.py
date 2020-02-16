#!/usr/bin/env python3

import os
import sys
import tempfile
from argparse import ArgumentParser
from colorama import init, Fore, Style  # type: ignore
from subprocess import call
from typing import Optional, List, Tuple, cast
from shutil import get_terminal_size

from tohe import __version__
from tohe.db import ToheDB
from tohe.util.editor import call_editor
from tohe.util.status import Status


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
    return Fore.GREEN + sign + ' ' + Fore.CYAN + txt + Style.RESET_ALL


def INFO(msg: str) -> None:
    print(Fore.GREEN + Style.BRIGHT + msg + Style.RESET_ALL)


def ERROR(msg: str) -> None:
    print(Fore.RED + Style.BRIGHT + msg + Style.RESET_ALL)


def print_rows(rows):
    if not rows:
        return
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
        prog='tohe', description='tohe - The TODO list manager')
    arg_parser.add_argument(
        '-v', '--version', action='store_true', help='show version number and exit')
    arg_parser.add_argument('-db', help='database file to use')
    arg_parser.add_argument(
        '-L', '--loglevel', help='set the log level', choices='DEBUG INFO WARN ERROR'.split())
    # TODO add option to sort tags

    subparsers = arg_parser.add_subparsers(
        title='Operations', description='modifying the TODOs', dest='operation')

    add_p = subparsers.add_parser(
        'add', help='add todo')
    add_p.add_argument('content', nargs='?', metavar='CONTENT',
                       help='add a new todo (if content is not supplied, $EDITOR will be opened)',
                       const='_default', default=None)
    add_p.add_argument(
        '-t', '--tag', help='tags for the new todo', metavar='TAG',
        nargs='+', default=[], dest='tags')

    list_p = subparsers.add_parser('list', help='list all todos')
    list_p.add_argument(
        '-t', '--tag', help='filter by tags', metavar='TAG', nargs='+', default=[], dest='tags')

    edit_p = subparsers.add_parser('edit', help='edit a todo')
    edit_p.add_argument(
        'id', type=int, help='ID of entry to be modified', metavar='ID')
    edit_p.add_argument(
        '-t', '--tag', help='add tags to entry', nargs='+', dest='tags')
    edit_p.add_argument(
        '-r', '--rtag', help='remove tags from entry', nargs='+', default=[], dest='rtags')

    search_p = subparsers.add_parser('search', help='search all todos')
    search_p.add_argument('term', help='search term', metavar='TERM')
    search_p.add_argument(
        '-w', '--wildcard', help='enable wildcards in search terms (default is off)',
        action='store_true', default=False)

    delete_p = subparsers.add_parser('delete', help='delete a todo')
    delete_p.add_argument(
        'id', type=int, help='ID of entry to be deleted', metavar='ID')

    help_p = subparsers.add_parser('help', help='print help message')

    parsers = {'add': add_p, 'list': list_p, 'edit': edit_p,
               'search': search_p, 'delete': delete_p, 'help': help_p}

    args = arg_parser.parse_args()
    if args.db or args.loglevel:
        if args.db:
            option = '-db'
        if args.loglevel:
            option = '--loglevel'
        ERROR("Currently unsupported option: %s" % (option,))
        sys.exit(-1)

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

    TOHE = ToheDB()

    if args.operation == 'add':
        content = call_editor() if args.content is None else args.content
        TOHE.add(content, tags=args.tags)

    elif args.operation == 'list':
        tags = args.tags if args.tags else None
        rows = TOHE.list(tags=tags)
        if rows is None or not rows:
            INFO('No entries yet!')
        print_rows(rows)

    elif args.operation == 'edit':
        entry = TOHE.get(args.id)
        if entry == Status.FAIL:
            sys.exit(1)
        (_, content, tags) = cast(Tuple, entry)
        if tags is None:
            tags = []
        if args.rtags:
            tags = [t for t in tags if t not in args.rtags]
        if args.tags:
            tags += args.tags

        if args.tags or args.rtags:
            status = TOHE.edit(id=args.id, tags=tags)
            if status != Status.OK:
                sys.exit(1)
        else:  # only open editor of no tags are changing
            content = call_editor(content=content)
            status = TOHE.edit(id=args.id, todo=content)
            if status != Status.OK:
                sys.exit(1)

    elif args.operation == 'search':
        entries = TOHE.search(term=args.term, wildcards=args.wildcard)
        if entries is None or not entries:
            INFO('No results!')
        print_rows(entries)

    elif args.operation == 'delete':
        # TODO add option to delete by tag/tags
        status = TOHE.delete(args.id)
        if status != Status.OK:
            sys.exit(1)
    else:
        # unreachable because of argparser
        ERROR("Unrecognized operation '%s'!" % (args.operation,))
        sys.exit(1)


if __name__ == "__main__":
    main()
