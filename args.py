import argparse

initparams = '''
{
    "verbose_level" : 0,
    "logfile" : null,
    "loglevel" : "DEBUG"
}'''

class ListArgumentAction(argparse.Action):
    ''' new action to take CSV as list '''
    def __call__(self, parser, namespace, values, option_string=None):
        print('{} {} {}'.format(namespace, values, option_string))
        setattr(namespace, self.dest, values.split(','))

class CustomHelpFormatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):
    def __init__(self, prog, indent_increment=2, max_help_position=32, width=None):
        super(CustomHelpFormatter, self).__init__(prog, indent_increment, max_help_position, width)
    def _get_help_string(self, action):
        help = action.help
        if help is None:
            help = ''
        if action.required:
            help += ' [required]'
        if '%(default)' not in help:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    if action.default is not None:
                        if type(action.default) == str:
                            help += ' (default: "%(default)s")'
                        elif type(action.default) == int or type(action.default) == float:
                            help += ' (default: %(default)s)'
                        elif type(action.default) == list:
                            defaults = []
                            for d in action.default:
                                if type(d) == str:
                                    defaults.append('"{}"'.format(d))
                                elif type(d) == int or type(d) == float:
                                    default.append(d)
                                elif d:
                                    default.append('on')
                                elif not d:
                                    default.append('off')
                            help += ' (default: {})'.format(','.join(defaults))
                        elif action.default:
                            help += ' (default: on)'
                        elif not action.default:
                            help += ' (default: off)'
                        else:
                            help += ' (default: %(default)s)'
        return help

class SubcommandHelpFormatter(CustomHelpFormatter):
    ''' new formatter of argparse to hide metavar in command listing
    https://stackoverflow.com/questions/13423540/argparse-subparser-hide-metavar-in-command-listing '''
    def _format_action(self, action):
        parts = super(argparse.RawDescriptionHelpFormatter, self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts

def error_nosubcommand(parser):
    err = 'no subcommand is specified'
    parser.print_usage()
    print(err)

def common_arguments(params):
    '''parse arguments'''
    parser = argparse.ArgumentParser(description='Sample',
        prog = params.prog,
        formatter_class=SubcommandHelpFormatter)
    parser.set_defaults(handler=lambda params: error_nosubcommand(parser))
    parser.add_argument('-v', '--version', action='version',
        version='%(prog)s {}'.format(params.version))
    parser.add_argument('--loglevel', default=params.loglevel,
        help='loglevel from "CRITICAL|ERROR|WARNING|INFO|DEBUG"', metavar='LEVEL')
    parser.add_argument('--logfile', default=params.logfile,
        help='logfile', metavar='FILE')
    subparsers = parser.add_subparsers(
        description='"%(prog)s <subcommand> --help" to see usage of subcommand',
        metavar='')
    common_args = subparsers.add_parser('print_params', add_help=False)
    common_args.set_defaults(handler=print_params)
    parser_common = common_args.add_argument_group('common options')
    parser_common.add_argument('--verbose', dest='verbose_level',
        default=params.verbose_level, type=int,
        help='Verbose level', metavar='NUM')
    parser_common.add_argument('targets', nargs='+', # nargs='*',
        help='target files', metavar='FILE')
    return parser, subparsers, common_args

def print_params():
    return printlog(params.dumpjson())

def csv2list(csv, element_type='strings'):
    if element_type == 'int':
        return [int(e) for e in csv.split(',')]
    elif element_type == 'float':
        return [float(e) for e in csv.split(',')]
    elif element_type == 'strings':
        return [str(e).strip() for e in csv.split(',')]
    else:
        return [e for e in csv.split(',')]