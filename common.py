import sys
import os
import json

initparams = '''{
    "output_prefix" : null,
    "output_prefix_sep" : " ",
    "output_indent" : 4,
    "output_end" : "\\n"
}'''

# loop
def loop(params):
    if params.loop_preproc is not None:
        params.loop_preproc()
    for f in params.targets:
        if os.path.isfile(f):
            params.cmd(f)
    if params.loop_postproc is not None:
        params.loop_postproc()

# initialize
def initialize_modules(name):
    params = Params()
    printlog = Printlog(params)
    set_logger(name)
    return params, printlog

# formatted now command
import datetime
def formattednow():
    return datetime.datetime.now().strftime('%y%m%d%H%M')

# singleton base class
class Singleton(object):
    '''base class of singleton'''
    def __new__(cls, *args, **kargs):
        if not hasattr(cls, "_instance"):
            if sys.version_info.major == 2:
                cls._instance = super(Singleton, cls).__new__(cls)
            elif sys.version_info.major == 3:
                cls._instance = super().__new__(cls)
        return cls._instance

## parameter related
import argparse
class Params(Singleton, argparse.Namespace):
    '''global parameter class'''
    def __repr__(self):
        return 'Params ({})'.format(len(self))
    def __len__(self):
        return len(vars(self))
    def displayall(self):
        '''display all parameters'''
        out = '{} = {{\n'.format(self.__repr__())
        for (k,v) in sorted(vars(self).items(), key=lambda x:x[0]):
            out = out + '    {} = {} ({}),\n'.format(k,v, type(v).__name__)
        out = out + '}\n'
        return out
    def loadjson(self, params_json):
        '''load from json'''
        params_dict = json.loads(params_json)
        for (k, v) in params_dict.items():
            setattr(self, k, v)
    def dumpjson(self):
        '''dump to formatted json'''
        params_dict = vars(self)
        for k in params_dict.keys():
            v = params_dict[k]
            try:
                j = json.dumps({k:v})
            except:
                params_dict[k] = str(v)
        return json.dumps(params_dict, indent=4, sort_keys=True)

# extend print function
class Printlog:
    ''' extend print function to output stdout and/or file with prefix'''
    def __init__(self, params):
        self.prefix = params.output_prefix
        self.prefix_sep = params.output_prefix_sep
        self.indent =params.output_indent
        self.output_file = None
        self.prefix_flag = False
        self.output_stdout_flag = False
        self.output_file_flag = False
        self.end = params.output_end
    def __repr__(self):
        return 'Printlog(outfile={},({},{}))'.format(self.output_file,
            self.output_stdout_flag, self.output_file_flag)
    def set_prefix(self):
        return self.prefix
    def log(self, message, end=None):
        output = message
        if end is None:
            end = self.end
        if self.prefix_flag and self.prefix is not None:
            output = self.prefix + self.prefix_sep + output
        if self.output_file_flag:
            if self.output_file is None:
                raise IOError('no logfile specified')
            with open(self.output_file, 'a') as OUT:
                OUT.write(output)
        if self.output_stdout_flag:
            print(output, end=end)
        return True
    def __call__(self, message, end=None):
        self.log(message, end=end)

logging_config = '''
{
    "version": 1,
    "disable_existing_loggers": false,
    "formatters": {
        "simple": {
            "format": "%(asctime)s %(name)s:%(lineno)s %(funcName)s [%(levelname)s]: %(message)s"
        }
    },

    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },
        "fileHandler": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": "to be replaced"
        }
    },

    "loggers": {
        "__main__": {
            "level": "DEBUG",
            "handlers": ["consoleHandler", "fileHandler"],
            "propagate": false
        },
        "same_hierarchy": {
            "level": "DEBUG",
            "handlers": ["consoleHandler", "fileHandler"],
            "propagate": false
        },
        "lower.sub": {
            "level": "DEBUG",
            "handlers": ["consoleHandler", "fileHandler"],
            "propagate": false
        }
    },

    "root": {
        "level": "INFO"
    }
}
'''
import logging
import logging.config
def root_logger(logfile=None, level=logging.DEBUG):
    config_dict = json.loads(logging_config)
    if logfile is not None:
        config_dict['handlers']['fileHandler']['filename'] = logfile
    else:
        del config_dict['handlers']['fileHandler']
        config_dict['loggers']['__main__']['handlers'] = ['consoleHandler']
        config_dict['loggers']['same_hierarchy']['handlers'] = ['consoleHandler']
        config_dict['loggers']['lower.sub']['handlers'] = ['consoleHandler']
    logging.config.dictConfig(config_dict)
    logger = logging.getLogger()
    logger.setLevel(level)
    return logger

def set_logger(name):
    logger = logging.getLogger(name)
    logger.addHandler(logging.NullHandler())
    logger.setLevel(logging.DEBUG)
    logger.propagate = True

# chmod and recursive chmod
def chmod(path, mode):
    perm_bits = {'ur' : stat.S_IRUSR,'uw' : stat.S_IWUSR,'ux' : stat.S_IXUSR,
                'gr' : stat.S_IRGRP,'gw' : stat.S_IWGRP,'gx' : stat.S_IXGRP,
                'or' : stat.S_IROTH,'ow' : stat.S_IWOTH,'ox' : stat.S_IXOTH}
    cmode = os.stat(path).st_mode
    for op in ['=','+','-']:
        if op in mode:
            break
    modes = mode.split(op)
    for t in modes[0]:
        if op == '=':
            cmode -= perm_bits[t+'r']
            cmode -= perm_bits[t+'w']
            cmode -= perm_bits[t+'x']
        for m in modes[1]:
            if op == '+' or op == '=':
                cmode |= perm_bits[t+m]
            elif op == '-':
                cmode -= perm_bits[t+m]
    os.chmod(path, cmode)

def recursive_chmod(path, mode):
    chmod(path, mode)
    for root, dirs, files in os.walk(path):
        for d in dirs:
            chmod(os.path.join(root, d), mode)
        for f in files:
            chmod(os.path.join(root, f), mode)

# tarball
import tarfile
import stat
import shutil
TIMESTAMP_FILE = '.tarball-timestamp'
def tarball_create(target, suffix=None, delete_target=False):
    ''' create tarball '''
    now = formattednow()
    srcpdir = os.path.dirname(os.path.abspath(target))
    srcbname = os.path.basename(target)
    tsout =  '#TARBALL\n'
    tsout += '#SRC {}\n'.format(srcbname)
    tsout += '#DST {}\n'.format(srcpdir)
    tsout += '#TIME {}\n'.format(now)
    cwd = os.getcwd()
    cmode = os.stat(target).st_mode
    chmod(target, 'u+wx')
    os.chdir(srcpdir)
    timestamp = os.path.join(srcbname, TIMESTAMP_FILE)
    with open(timestamp, 'w') as TS:
        TS.write(tsout)
    os.chmod(target, cmode)
    if suffix is None:
        suffix = now
    tarout = '{}-{}.tar.gz'.format(srcbname, suffix)
    tar = tarfile.open(tarout, 'w:gz')
    tar.add(srcbname)
    tar.close()
    chmod(target, 'u+wx')
    os.remove(timestamp)
    if delete_target:
        recursive_chmod(target, 'u+rwx')
        shutil.rmtree(target)
    else:
        os.chmod(target, cmode)
    os.chdir(cwd)
    return os.path.abspath(tarout)

def tarball_restore(target):
    ''' restore tarball '''
    srcpdir = None
    srcbname = None
    tsflag = False
    tar = tarfile.open(target, 'r:gz')
    timestamp = os.path.join(tar.getnames()[0], TIMESTAMP_FILE)
    if not timestamp in tar.getnames():
        print('no timestamp file')
        return False
    tar.extract(timestamp)
    with open(timestamp) as TS:
        for line in TS.readlines():
            item = line.split()
            if item[0] == '#TARBALL':
                tsflag = True
            elif item[0] == '#DST':
                srcpdir = item[1]
            elif item[0] == '#SRC' and item[1] == tar.getnames()[0]:
                srcbname = item[1]
    shutil.rmtree(tar.getnames()[0])
    if (not tsflag or srcpdir is None or srcbname is None):
        print('no valid timestamp: {}'.format(timestamp))
        return False
    if os.path.exists(srcpdir) and os.path.isfile(srcpdir):
        print('existed file: {}'.format(srcpdir))
        return False
    elif not os.path.exists(srcpdir):
        print('no destination. make {}'.format(srcpdir))
        os.makedirs(srcpdir)
    print('restore to {}'.format(srcpdir))
    cwd = os.getcwd()
    os.chdir(srcpdir)
    tar.extractall()
    os.remove(timestamp)
    os.chdir(cwd)
    return os.path.join(srcpdir, srcbname)

def csv2list(csv, element_type='strings'):
    if element_type == 'int':
        return [int(e) for e in csv.split(',')]
    elif element_type == 'float':
        return [float(e) for e in csv.split(',')]
    elif element_type == 'strings':
        return [str(e).strip() for e in csv.split(',')]
    else:
        return [e for e in csv.split(',')]