import argparse

class ListArgumentAction(argparse.Action):
    '''new action to take CSV as list'''
    def __call__(self, namespace, values):
        setattr(namespace, self.dest, values.split(','))

class CustomHelpFormatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):
    '''formatter to handle default properly'''
    def __init__(self, prog, indent_increment=2, max_help_position=32, width=None):
        super(CustomHelpFormatter, self).__init__(prog, indent_increment, max_help_position, width)
    def _get_help_string(self, action):
        help_text = action.help

        ## mark required
        if getattr(action, 'required', False):
            help_text += ' [required]'

        ## do nothing if default is already explicitly formatted in the help
        if '%(default)s' in help_text:
            return help_text

        ## skip if argparse is suppressing the default
        if action.default is argparse.SUPPRESS:
            return help_text

        ## append default info for optional/zero-or-more
        defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
        if action.option_strings or action.nargs in defaulting_nargs:
            default_val = action.default

            ## no default
            if default_val is None:
                pass

            ## list default
            elif isinstance(default_val, list):
                defaults = []
                for d in default_val:
                    if isinstance(d, str):
                        defaults.append(f'"{d}"')
                    elif isinstance(d, (int, float)):
                        defaults.append(str(d))
                    elif isinstance(d, bool):
                        defaults.append('on' if d else 'off')
                    else:
                        defaults.append(str(d))
                help_text += f' (default: {','.join(defaults)})'

            ## other single scaler default
            elif isinstance(default_val, str):
                help_text += ' (default: "%(default)s")'
            elif isinstance(default_val, (int, float)):
                help_text += ' (default: %(default)s)'
            elif isinstance(default_val, bool):
                help_text += ' (default: on)' if default_val else ' (default: off)'
            else:
                help_text += ' (default: %(default)s)'

        return help_text

class RootHelpFormatter(CustomHelpFormatter):
    '''formatter for root parser'''
    argparse to 
    def _format_action(self, action):
        '''hide the top metavar line subcommands block referring to
https://stackoverflow.com/questions/13423540/argparse-subparser-hide-metavar-in-command-listing'''
        parts = super()._format_action(action)
        if isinstance(action, argparse._SubParsersAction):
            lines = parts.splitlines()
            if lines:
                parts = '\n'.join(lines[1:])
        return parts
    def add_usage(self, usage, actions, groups, prefix=None):
        '''root only "[subcommand]" injection'''
        if usage is None:
            actions_usage = self.__format_action_usage(actions, groups)
            has_subparsers = any(isinstance(a, argparse._SubParsersAction) for a in actions)
            if has_subparsers:
                usage = '%(prog)s [subcommand] ' + actions_usage
            else:
                usage = '%(prog)s ' + actions_usage
        return super().add_usage(usage, actions, groups, prefix)

def config_arguments(default_configfiles: list) -> tuple[argparse.ArgumentParser, str]:
    '''parse argument for config file'''
    parser_config = argparse.ArgumentParser(add_help=False)
    config_files = ' or '.join(map(str, default_configfiles))
    parser_config.add_argument(
        '--config',
        help=f'config file (YAML format)\n(default: {config_files})'
    )
    return parser_config

def positional_arguments() -> argparse.ArgumentParser:
    '''parser of positional arguments for subcommands'''
    parser_positional = argparse.ArgumentParser(add_help=False)
    parser_positional.add_argument(
        'target',
        nargs='+',
        metavar='FILE',
        help='target files'
    )
    return parser_positional

def error_nosubcommand(parser: argparse.ArgumentParser):
    '''print error if no subcommand is specified'''
    print(f'ERROR: missing subcommand and any other arguments')
    print(f'usage: {parser.prog} <subcommand> [options] ...')
    print(f'try "{parser.prog} --help"')

def build_root_parser(prog: str, description: str, parent_parsers: list) -> tuple[argparse.ArgumentParser, argparse.ArgumentParser]:
    '''build root parser with specified parent parsers'''
    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        formatter_class=RootHelpFormatter,
        parents=parent_parsers
    )
    subparsers = parser.add_subparsers(
        title='subcommands',
        description='"%(prog)s <subcommand> --help" to see usage of subcommand',
        metavar=''
    )
    subparsers.dest = 'command'
    return parser, subparsers
