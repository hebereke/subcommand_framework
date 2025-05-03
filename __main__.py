#!/usr/bin/env python
from __future__ import print_function

### Modules
import sys
import os
import json
import common, args

### declare singleton instances
params, printlog = common.initialize_modules('main')

### parameters for script by json
scriptparams = '''
{
    "version" : 0.0,
    "prog" : "sample"
}'''

### core modules
core_modules = (
    'args',
    'common'
)

### subcommand modules by tuple
subcommand_modules = (
    'sample',
)

def set_params(initparams_json, subcommand_modules):
    ''' set parameters to be used '''
    params = common.Params()
    # load init params
    params.loadjson(initparams_json)
    # define extra params
    params.dotfile = '.{}'.format(params.prog)
    params.tmpfile = os.path.join(os.getcwd(), '.{}_{}'.format(params.prog, os.getpid()))
    # load subcommand modules
    for m in subcommand_modules:
        exec('from subcommand import {}'.format(m))
        exec('params.loadjson({}.initparams)'.format(m))
    # load default
    if os.getenv('HOME') is not None:
        dotfile = os.path.join(os.getenv('HOME'), params.dotfile)
    else:
        dotfile = os.path.join(os.getcwd(), params.dotfile)
    if not os.path.isfile(dotfile):
        dotfile = None
    if dotfile is not None:
        with open(dotfile) as DOTFILE:
            params.loadjson(DOTFILE.read())
    # parse arguments of each subcommands
    parser, subparsers, parent = args.common_arguments(params)
    for m in subcommand_modules:
        exec('subparsers = {}.argument(subparsers, parent)'.format(m))
    params = parser.parse_args(namespace=params)
    # check parameter
    if params.jobname_prefix_flag:
        params.quiet_flag = True
    return params

def initparams(scriptparams, core_modules):
    d = json.loads(scriptparams)
    for m in core_modules:
        exec('import {}'.format(m))
        exec('d.update(json.loads({}.initparams))'.format(m))
    return json.dumps(d)

def main(scriptparams, core_modules, subcommand_modules=None):
    initparams_json = initparams(scriptparams, core_modules)
    # parameters
    if initparams_json is None or subcommand_modules is None:
        raise Exception('no initparams and subcommand modules are defined')
    params = set_params(initparams_json, subcommand_modules)
    # logger
    printlog = common.SingletonPrintlog(logfile=params.logfile)
    logger = common.root_logger(params.logfile)
    # call subcommand
    params.handler()

if __name__ == '__main__':
    #subcommand_modules = ('sample',) # subcommands for debugging
    main(scriptparams, core_modules, subcommand_modules)