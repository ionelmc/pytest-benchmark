import argparse

import py

from . import plugin
from .plugin import Logger
from .plugin import add_display_options
from .plugin import add_global_options
from .storage import Storage
from .table import ResultsTable
from .utils import first_or_value


class HelpAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        namespace.command = values
        namespace.help = True


class CommandArgumentParser(argparse.ArgumentParser):
    commands = None
    commands_dispatch = None

    def __init__(self, *args, **kwargs):
        kwargs['add_help'] = False

        super(CommandArgumentParser, self).__init__(*args,
                                                    formatter_class=argparse.RawDescriptionHelpFormatter,
                                                    **kwargs)
        self.add_argument(
            '-h', '--help',
            metavar='COMMAND',
            nargs='?', action=HelpAction, help='Display help and exit.'
        )
        self.add_command(
            'help',
            description='Display help and exit.'
        ).add_argument(
            'command',
            nargs='?', action=HelpAction
        )

    def add_command(self, name, **opts):
        if self.commands is None:
            self.commands = self.add_subparsers(
                title='commands', dest='command', parser_class=argparse.ArgumentParser
            )
            self.commands_dispatch = {}
        if 'description' in opts and 'help' not in opts:
            opts['help'] = opts['description']

        command = self.commands.add_parser(
            name, formatter_class=argparse.RawDescriptionHelpFormatter, **opts
        )
        self.commands_dispatch[name] = command
        return command

    def parse_args(self):
        args = super(CommandArgumentParser, self).parse_args()
        if args.help:
            if args.command:
                return super(CommandArgumentParser, self).parse_args([args.command, '--help'])
            else:
                self.print_help()
                self.exit()
        elif not args.command:
            self.error('the following arguments are required: COMMAND (choose from %s)' % ', '.join(
                map(repr, self.commands.choices)))
        return args


def strip_prefix(callback, force_argument=False):
    def add_argument(dest, **kwargs):
        if not dest.startswith('--benchmark-'):
            raise RuntimeError("Bad argument %s with options %s" % (dest, kwargs))
        callback(dest[12:] if force_argument else '--' + dest[12:], **kwargs)

    return add_argument


def main():
    parser = CommandArgumentParser('py.test-benchmark', description="pytest_benchmark's management commands.")
    add_global_options(strip_prefix(parser.add_argument))

    parser.add_command(
        'list',
        description='List saved runs.',
    )

    display_command = parser.add_command(
        'compare',
        description='Compare saved runs.',
        epilog='''examples:

    pytest-benchmark compare 'Linux-CPython-3.5-64bit/*'

        Loads all benchmarks ran with that interpreter. Note the special quoting that disables your shell's glob
        expansion.

    pytest-benchmark compare 0001

        Loads first run from all the interpreters.

    pytest-benchmark compare /foo/bar/0001_abc.json /lorem/ipsum/0001_sir_dolor.json

        Loads runs from exactly those files.''')
    add_display_options(strip_prefix(display_command.add_argument))
    display_command.add_argument(
        'glob_or_file',
        nargs='*', help='Glob or exact path for json files. If not specified all runs are loaded.'
    )
    args = parser.parse_args()
    logger = Logger(args.verbose)
    storage = Storage(args.storage, logger)
    print(args)
    if args.command == 'list':
        for file in storage.query():
            print(file)
    elif args.command == 'compare':
        results_table = ResultsTable(args.columns, args.sort, first_or_value(args.histogram, False), logger)
        groups = plugin.pytest_benchmark_group_stats(
            benchmarks=storage.load_benchmarks(*args.glob_or_file),
            group_by=args.group_by,
            config=None,
        )
        results_table.display(TerminalReporter(), groups)


class TerminalReporter(object):
    def __init__(self):
        self._tw = py.io.TerminalWriter()

    def ensure_newline(self):
        self._tw.line()

    def write(self, content, **markup):
        self._tw.write(content, **markup)

    def write_line(self, line, **markup):
        if not py.builtin._istext(line):
            line = py.builtin.text(line, errors="replace")
        self.ensure_newline()
        self._tw.line(line, **markup)

    def rewrite(self, line, **markup):
        line = str(line)
        self._tw.write("\r" + line, **markup)

    def write_sep(self, sep, title=None, **markup):
        self.ensure_newline()
        self._tw.sep(sep, title, **markup)

    def section(self, title, sep="=", **kw):
        self._tw.sep(sep, title, **kw)

    def line(self, msg, **kw):
        self._tw.line(msg, **kw)
