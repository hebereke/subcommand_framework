import os
import stat
import shutil
import glob
import argparse
from pathlib import Path

## check if yaml library is available
import importlib.util
if importlib.util.find_spec('yaml') is None:
    raise ImportError('yaml module is required')
from configfile import load_package_config

def create_script(scriptpath, installdir, python_command):
    print(f'Create executable script as {scriptpath}')
    script_out =   '#!/bin/sh\n'
    script_out += f'PYTHON_CMD="{python_command}"\n'
    script_out += f'PACKAGE_DIR="{installdir}"\n'
    script_out +=  'if [[ -n "${PYTHONPATH}" ]]; then\n'
    script_out +=  '    export PYTHONPATH=${PACKAGE_DIR}:${PYTHONPATH}\n'
    script_out +=  'else\n'
    script_out +=  '    export PYTHONPATH=${PACKAGE_DIR}\n'
    script_out +=  'fi\n'
    script_out +=  '${PYTHON_CMD} ${PACKAGE_DIR} "$@"\n'
    with open(scriptpath, 'w') as OUT:
        OUT.write(script_out)
    cmode = os.stat(scriptpath).st_mode
    cmode = cmode | stat.S_IRUSR | stat.S_IXUSR
    os.chmod(scriptpath, cmode)

def testscript(args):
    create_script('test', Path.cwd(), args.pythoncmd)

def package_installation(args):
    ## decide parameters
    python_command = args.pythoncmd
    script_name = args.scriptname

    # package directory check
    package_dir = Path(args.packagedir).resolve()
    if not package_dir.is_dir():
        raise IOError(f'{package_dir} is not directory')

    # installation directory check
    install_dir = Path(args.installdir).resolve()
    print(f'Install {package_dir.name} to {install_dir}')

    # package installation
    files = glob.glob(f'{package_dir}/*.py')
    files += glob.glob(f'{package_dir}/subcommands/*.py')
    files += glob.glob(f'{package_dir}/data/*')
    files += glob.glob(f'{package_dir}/*.yaml')
    for f in files:
        bn = Path(f.replace(f'{package_dir}/', ''))
        src = package_dir / bn
        dst = install_dir / bn
        print(f'    Copy {bn}')
        if not dst.parent.is_dir():
            os.makedirs(dst.parent)
        shutil.copyfile(src, dst)

    # execute script installation
    execdir = os.path.join(os.path.dirname(install_dir), 'bin')
    if args.execdir is not None:
        execdir = args.execdir
    if not os.path.isdir(execdir):
        print('create {}'.format(execdir))
        os.makedirs(execdir)
    create_script(os.path.join(execdir, script_name), install_dir, python_command)

def packagedir_argument(package_dir):
    parser_packagedir = argparse.ArgumentParser(add_help=False)
    parser_packagedir.add_argument(
        '--packagedir',
        help='directory of installation package (default: "%(default)s")',
        metavar='DIR',
        default=package_dir
    )
    return parser_packagedir

def install_argument(script_name, install_dir, python_command, parser_packagedir):
    parser_install = argparse.ArgumentParser(
        description='TFlex SMO utility installation script',
        parents=[parser_packagedir]
    )
    parser_install.add_argument(
        '--execdir', '-e',
        help='directory to create execute script (default: "installdir/../bin")',
        metavar='DIR',
        default=None
    )
    parser_install.add_argument(
        '--scriptname', '-s',
        help='execute script name (default: "%(default)s")',
        metavar='FILE',
        default=script_name
    )
    parser_install.add_argument(
        '--pythoncmd', '-p',
        help='python command',
        metavar='STR',
        default=python_command
    )
    parser_install.add_argument(
        '--testscript', '-t',
        help='create test execute script without package installation',
        action='store_true',
        dest='test_flag'
    )
    parser_install.add_argument(
        'installdir',
        nargs='?',
        help='installation directory (default: "%(default)s")',
        default=install_dir
    )
    return parser_install

if __name__ == '__main__':
    ## default values
    python_command = 'python'                     # python command
    script_name = 'sample'                        # script name
    package_dir = Path(__file__).resolve().parent # source of installation

    ## decide package directory
    parser_packagedir = packagedir_argument(package_dir)
    args_packagedir, _ = parser_packagedir.parse_known_args()
    if args_packagedir.packagedir:
        package_dir = Path(args_packagedir.packagedir)

    ## load package configuration
    package_config = load_package_config(package_dir)
    if 'package' in package_config:
        if 'prog' in package_config['package']:
            script_name = package_config['package']['prog']
        if 'pythoncmd' in package_config['package']:
            python_command = package_config['package']['pythoncmd']
    install_dir = Path(os.path.join(os.getenv('HOME', ''), 'local', script_name)) # destination of installation

    ## parse arguments
    parser_install = install_argument(
        script_name,
        install_dir,
        python_command,
        parser_packagedir
    )
    args = parser_install.parse_args()

    # create test execute script without package installation
    if args.test_flag:
        testscript(args)
    else:
        package_installation(args)
