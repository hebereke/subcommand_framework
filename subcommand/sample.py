'''subcommand module sample'''
import common, args
params, printlog = common.initialize_modules(__name__)

initparams = '''
{
    "flag" : false,
    "prefix" : "SAMPLE: "
}'''

def argument(subparsers, parent):
    '''sample arguments'''
    parser = subparsers.add_parser('sample',
        help='subcommand sample',
        parents=[parent],
        formatter_class=args.CustomHelpFormatter)
    parser.set_defaults(handler=common.loop, cmd=cmd)
    parser_subcommand = parser.add_argument_group('subcommand options')
    parser_subcommand.add_argument('--debug', dest='flag',
        action='store_true',
        default=params.flag,
        help='debug')
    parser_subcommand.add_argument('--nodebug', dest='flag',
        action='store_false',
        default=not params.flag,
        help='debug')
    parser_subcommand.add_argument('--prefix', dest='prefix',
        default=params.prefix,
        help='prefix', metavar='STRINGS')
    return subparsers

def cmd(f):
    if params.debug_flag:
        printlog(os.path.abspath(f))
    with open(f) as F:
        printlog(F.readlines())