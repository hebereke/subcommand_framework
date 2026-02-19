## formatted now command
import datetime
import os
import stat
import tarfile
import shutil

def formattednow():
    return datetime.datetime.now().strftime('%y%m%d%H%M')

#@ chmod and recursive chmod
def chmod(path, mode):
    perm_bits = {'ur' : stat.S_IRUSR,'uw' : stat.S_IWUSR,'ux' : stat.S_IXUSR,
                'gr' : stat.S_IRGRP,'gw' : stat.S_IWGRP,'gx' : stat.S_IXGRP,
                'or' : stat.S_IROTH,'ow' : stat.S_IWOTH,'ox' : stat.S_IXOTH}
    cmode = os.stat(path).st_mode
    op = None
    for o in ['=','+','-']:
        if o in mode:
            op = o
            break
    if op is None:
        raise ValueError('invalid mode format')
    modes = mode.split(op)
    for t in modes[0]:
        if op == '=':
            cmode &= ~perm_bits.get(t+'r', 0)
            cmode &= ~perm_bits.get(t+'w', 0)
            cmode &= ~perm_bits.get(t+'x', 0)
        for m in modes[1]:
            if op == '+' or op == '=':
                cmode |= perm_bits.get(t+m, 0)
            elif op == '-':
                cmode &= ~perm_bits.get(t+m, 0)
    os.chmod(path, cmode)

def recursive_chmod(path, mode):
    chmod(path, mode)
    for root, dirs, files in os.walk(path):
        for d in dirs:
            chmod(os.path.join(root, d), mode)
        for f in files:
            chmod(os.path.join(root, f), mode)

## tarball
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
