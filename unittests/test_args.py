import argparse

from args import ListArgumentAction, config_arguments, build_root_parser
from template.package_config import positional_arguments


def test_list_argument_action_splits_csv():
    p = argparse.ArgumentParser()
    p.add_argument('--list', action=ListArgumentAction)
    ns = p.parse_args(['--list', 'a,b,c'])
    assert ns.list == ['a', 'b', 'c']


def test_config_arguments_parses_config_option():
    p = config_arguments(['.app'])
    ns = p.parse_args(['--config', 'my.yaml'])
    assert ns.config == 'my.yaml'


def test_positional_arguments_parses_targets():
    ppos = positional_arguments()
    ns = ppos.parse_args(['file1', 'file2'])
    assert ns.target == ['file1', 'file2']


def test_build_root_parser_creates_subparsers():
    parser, subparsers = build_root_parser('prog', 'desc', [])
    assert getattr(subparsers, 'dest', None) == 'command'
    usage = parser.format_usage()
    assert '[subcommand]' in usage
