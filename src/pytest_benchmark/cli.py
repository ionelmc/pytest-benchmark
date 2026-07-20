"""
..
  PYTEST_DONT_REWRITE
"""

from argparse import Action
from argparse import ArgumentParser
from argparse import Namespace
from argparse import RawDescriptionHelpFormatter
from collections.abc import Callable
from collections.abc import Sequence
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import Any
from typing import NoReturn
from typing import Self

import pytest
from _pytest import pathlib as _pathlib  # TODO: Change name of import
from _pytest._io import TerminalWriter
from _pytest.config.findpaths import locate_config
from _pytest.mark.expression import Expression

from pytest_benchmark.csv import CSVResults

from . import plugin
from .logger import Logger
from .plugin import add_csv_options
from .plugin import add_display_options
from .plugin import add_global_options
from .plugin import add_histogram_options
from .table import CompareBetweenResults
from .table import TableResults
from .utils import DEFAULT_COLUMNS
from .utils import NAME_FORMATTERS
from .utils import first_or_value
from .utils import load_storage
from .utils import parse_columns
from .utils import report_noprogress

COMPARE_HELP = """examples:

    pytest-benchmark {0} 'Linux-CPython-3.5-64bit/*'

        Loads all benchmarks ran with that interpreter. Note the special quoting that disables your shell's glob
        expansion.

    pytest-benchmark {0} 0001

        Loads first run from all the interpreters.

    pytest-benchmark {0} /foo/bar/0001_abc.json /lorem/ipsum/0001_sir_dolor.json

        Loads runs from exactly those files."""


class HelpAction(Action):
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> NoReturn:
        if values:
            command = values if isinstance(values, str) else str(values[0])
            make_parser().parse_args([command, '--help'])

        else:
            parser.print_help()

        parser.exit()


class CommandArgumentParser(ArgumentParser):
    commands = None
    commands_dispatch: dict[str, Any] | None = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs['add_help'] = False

        kwargs.setdefault('formatter_class', RawDescriptionHelpFormatter)
        super().__init__(*args, **kwargs)

        self.add_argument('-h', '--help', metavar='COMMAND', nargs='?', action=HelpAction, help='Display help and exit.')

        help_command = self.add_command('help', description='Display help and exit.')
        help_command.add_argument('command', nargs='?', action=HelpAction)

    def add_command(self, name: str, **opts: Any) -> ArgumentParser:
        if self.commands is None:
            self.commands = self.add_subparsers(
                title='commands',
                dest='command',
                parser_class=ArgumentParser,
            )
            self.commands_dispatch = {}

        if 'description' in opts and 'help' not in opts:
            opts['help'] = opts['description']

        command = self.commands.add_parser(name, formatter_class=RawDescriptionHelpFormatter, **opts)
        assert self.commands_dispatch is not None
        self.commands_dispatch[name] = command
        return command


def add_glob_or_file(addoption: Callable[..., Any]) -> None:
    addoption('glob_or_file', nargs='*', help='Glob or exact path for JSON files. If not specified all runs are loaded.')


def make_parser() -> CommandArgumentParser:
    parser = CommandArgumentParser('py.test-benchmark', description="pytest_benchmark's management commands.")
    add_global_options(parser.add_argument, prefix='')

    parser.add_command('list', description='List saved runs.')

    compare_command = parser.add_command(
        'compare',
        description='Compare saved runs.',
        epilog="""examples:

    pytest-benchmark compare 'Linux-CPython-3.5-64bit/*'

        Loads all benchmarks ran with that interpreter. Note the special quoting that disables your shell's glob
        expansion.

    pytest-benchmark compare 0001

        Loads first run from all the interpreters.

    pytest-benchmark compare /foo/bar/0001_abc.json /lorem/ipsum/0001_sir_dolor.json

        Loads runs from exactly those files.""",
    )
    add_display_options(compare_command.add_argument, prefix='')
    add_histogram_options(compare_command.add_argument, prefix='')
    compare_command.add_argument(
        '--between',
        metavar='COLUMNS',
        type=parse_columns,
        default=None,
        help='Compare same-named benchmarks across different source files. '
        'Takes a comma-separated list of metric columns to compare (e.g. min,mean,ops).',
    )
    add_glob_or_file(compare_command.add_argument)
    add_csv_options(compare_command.add_argument, prefix='')
    compare_command.add_argument(
        '-k',
        metavar='EXPR',
        dest='filter_expr',
        default=None,
        help="Only show benchmarks matching the given expression. Uses the same syntax as pytest's -k option (e.g. 'foo and not bar').",
    )

    return parser


class HookDispatch:
    conftest: ModuleType | None

    def __init__(self, *, root: Path, **kwargs: str) -> None:
        _, _, config, *_ = locate_config(invocation_dir=root, args=())
        conftest_file = Path('conftest.py')
        if conftest_file.exists():
            self.conftest = _pathlib.import_path(
                conftest_file,
                **kwargs,
                root=root,
                consider_namespace_packages=bool(config.get('consider_namespace_packages')),
            )
        else:
            self.conftest = None

    def __getattr__(self, item: str) -> Any:
        # TODO: inspect a way to get clean or explain what do the function
        default = getattr(plugin, item)
        return getattr(self.conftest, item, default)


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()
    level = Logger.QUIET if args.quiet else Logger.NORMAL

    if args.verbose:
        level = Logger.VERBOSE

    logger = Logger(level)
    storage = load_storage(args.storage, logger=logger, netrc=args.netrc)

    hook = HookDispatch(mode=args.importmode, root=Path())

    if args.command == 'list':
        for file in storage.query():
            print(file)

    elif args.command == 'compare':
        histogram = first_or_value(args.histogram, False)

        if args.between:
            if args.columns:
                parser.error('--between is not compatible with --columns (--between already specifies the columns)')

            if histogram:
                parser.error('--between is not compatible with --histogram')
            results_table_cls: Any = CompareBetweenResults
            args.columns = args.between

        else:
            results_table_cls = TableResults

            if not args.columns:
                args.columns = DEFAULT_COLUMNS

        results_table = results_table_cls(
            columns=args.columns,
            sort=args.sort,
            histogram=histogram,
            name_format=NAME_FORMATTERS[args.name],
            logger=logger,
            scale_unit=partial(
                hook.pytest_benchmark_scale_unit,
                config=pytest.Config.fromdictargs(
                    {'benchmark_time_unit': args.time_unit},
                    [],
                ),
            ),
        )
        benchmarks = storage.load_benchmarks(*args.glob_or_file)

        if args.filter_expr:
            expr = Expression.compile(args.filter_expr)

            def _evaluate_expr(benchmark: Any) -> bool:
                name = benchmark.get('fullname') or benchmark.get('name', '')

                def matcher(key: str, **kwargs: str | int | bool | None) -> bool:
                    return key in name

                return expr.evaluate(matcher)  # type: ignore[arg-type]

            benchmarks = filter(_evaluate_expr, benchmarks)

        groups = hook.pytest_benchmark_group_stats(
            benchmarks=benchmarks,
            group_by=args.group_by,
            config=None,
        )
        results_table.display(TerminalReporter(), groups, progress_reporter=report_noprogress)

        if args.csv:
            results_csv = CSVResults(args.columns, args.sort, logger)
            (output_file,) = args.csv

            results_csv.render(output_file, groups)

    elif args.command is None:
        assert parser.commands is not None
        parser.error('missing command (available commands: {})'.format(', '.join(map(repr, parser.commands.choices))))

    else:
        parser.error(f'unexpected command {args.command!r}')


class TerminalReporter:
    def __init__(self) -> None:
        self._tw = TerminalWriter()

    def ensure_newline(self: Self) -> None:
        pass

    def write(self: Self, content: str, **markup: bool) -> None:
        self._tw.write(content, **markup)

    def write_line(self: Self, line: str | bytes = '', **markup: bool) -> None:
        if not isinstance(line, str):  # TODO: Unnecessary isinstance call; "str" is always an instance of "str"
            line = line.decode(errors='replace')

        self._tw.line(line, **markup)

    def rewrite(self: Self, line: str, **markup: bool) -> None:
        line = str(line)
        self._tw.write('\r' + line, **markup)

    def write_sep(self: Self, sep: str, title: str | None = None, **markup: bool) -> None:
        self._tw.sep(sep, title, **markup)

    def section(self: Self, title: str, sep: str = '=', **kw: Any) -> None:
        self._tw.sep(sep, title, **kw)

    def line(self: Self, msg: str, **kw: Any) -> None:
        self._tw.line(msg, **kw)
