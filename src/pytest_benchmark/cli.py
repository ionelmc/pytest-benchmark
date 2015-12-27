"""

py.test-benchmark

"""
import argparse

from .plugin import add_display_options


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
            action='store_true', help='Display help and exit.'
        )
        self.add_command('help', description='Display help and exit.').add_argument('command', nargs='?', action=HelpAction)

    @property
    def epilog(self):
        return '\n'.join('  %-20s %s' % (name, parser.description) for name, parser in self.commands_dispatch.items())

    @epilog.setter
    def epilog(self, value):
        pass

    def add_command(self, name, **opts):
        if self.commands is None:
            self.commands = self.add_subparsers(
                title='commands', dest='command', help='', parser_class=argparse.ArgumentParser
            )
            self.commands_dispatch = {}

        command = self.commands.add_parser(name, formatter_class=argparse.RawDescriptionHelpFormatter, **opts)
        # command.add_argument(
        #     '-h', '--help',
        #     action='store_true', help='Show this help message and exit.'
        # )
        self.commands_dispatch[name] = command
        return command

    def parse_args(self):
        args = super(CommandArgumentParser, self).parse_args()
        print(args)
        if args.help:
            if args.command:
                return super(CommandArgumentParser, self).parse_args([args.command, '--help'])
            else:
                self.print_help()
                self.exit()


def main():
    parser = CommandArgumentParser('py.test-benchmark', description="pytest_benchmark's management commands.")

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
    add_display_options(display_command.add_argument)
    display_command.add_argument('run', nargs='+', help='Glob to match stored runs.')
    args = parser.parse_args()
    print(args)
