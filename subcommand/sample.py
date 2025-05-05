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
    parser_subcommand.add_argument('--debug', dest='debug_flag',
        action='store_true',
        default=params.flag,
        help='enable debug mode')
    parser_subcommand.add_argument('--nodebug', dest='debug_flag',
        action='store_false',
        default=not params.flag,
        help='disable debug mode')
    parser_subcommand.add_argument('--prefix', dest='prefix',
        default=params.prefix,
        help='prefix', metavar='STRINGS')
    return subparsers

def cmd(f):
    printlog.output_stdout_flag = True
    if params.debug_flag:
        printlog(os.path.abspath(f))
    with open(f) as F:
        for line in F.readlines():
            printlog(line.rstrip())