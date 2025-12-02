import time


class FileNode:
    def __init__(self, name, is_dir=False, content='', permissions=0o644, owner='root', group='root'):
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.permissions = permissions if not is_dir else 0o755
        self.owner = owner
        self.group = group
        self.children = {} if is_dir else None
        self.created = time.time()
        self.modified = time.time()
        self.accessed = time.time()
        self.size = len(content) if content else 0
        self.inode = id(self) % 1000000
        self.links = 1
        self.symlink_target = None

    def to_dict(self):
        data = {
            'name': self.name,
            'is_dir': self.is_dir,
            'content': self.content,
            'permissions': self.permissions,
            'owner': self.owner,
            'group': self.group,
            'created': self.created,
            'modified': self.modified,
            'accessed': self.accessed,
            'size': self.size,
            'inode': self.inode,
            'links': self.links,
            'symlink_target': self.symlink_target
        }
        if self.is_dir and self.children:
            data['children'] = {k: v.to_dict() for k, v in self.children.items()}
        return data

    @classmethod
    def from_dict(cls, data):
        node = cls(
            data['name'],
            data['is_dir'],
            data.get('content', ''),
            data.get('permissions', 0o644),
            data.get('owner', 'root'),
            data.get('group', 'root')
        )
        node.created = data.get('created', time.time())
        node.modified = data.get('modified', time.time())
        node.accessed = data.get('accessed', time.time())
        node.size = data.get('size', 0)
        node.inode = data.get('inode', id(node) % 1000000)
        node.links = data.get('links', 1)
        node.symlink_target = data.get('symlink_target')
        if data['is_dir'] and 'children' in data:
            node.children = {k: cls.from_dict(v) for k, v in data['children'].items()}
        return node


class FileSystem:
    def __init__(self):
        self.root = FileNode('/', is_dir=True, permissions=0o755)
        self.cwd = '/root'
        self.mounts = {'/': {'device': '/dev/sda1', 'fstype': 'ext4', 'options': 'rw,relatime'}}

    def initialize(self):
        dirs = [
            '/bin', '/sbin', '/usr', '/usr/bin', '/usr/sbin', '/usr/lib',
            '/etc', '/etc/init.d', '/etc/systemd', '/etc/apt',
            '/var', '/var/log', '/var/run', '/var/cache', '/var/lib',
            '/tmp', '/home', '/root', '/boot', '/dev', '/proc', '/sys',
            '/run', '/opt', '/srv', '/mnt', '/media', '/lib'
        ]
        for d in dirs:
            self._mkdir_p(d)
        self._create_etc_files()
        self._create_proc_files()
        self._create_dev_files()
        self._create_bin_files()
        self._create_root_files()

    def _mkdir_p(self, path):
        parts = path.strip('/').split('/')
        current = self.root
        for part in parts:
            if part not in current.children:
                current.children[part] = FileNode(part, is_dir=True)
            current = current.children[part]

    def _create_file(self, path, content, permissions=0o644):
        parts = path.strip('/').split('/')
        filename = parts[-1]
        dirpath = '/' + '/'.join(parts[:-1]) if len(parts) > 1 else '/'
        self._mkdir_p(dirpath)
        parent = self._get_node(dirpath)
        if parent and parent.is_dir:
            node = FileNode(filename, is_dir=False, content=content, permissions=permissions)
            parent.children[filename] = node

    def _get_node(self, path):
        if path == '/':
            return self.root
        parts = path.strip('/').split('/')
        current = self.root
        for part in parts:
            if not part:
                continue
            if current.children and part in current.children:
                current = current.children[part]
            else:
                return None
        return current

    def _create_etc_files(self):
        import psutil
        
        self._create_file('/etc/hostname', 'localhost\n')
        self._create_file('/etc/hosts', '127.0.0.1\tlocalhost\n::1\tlocalhost\n')
        
        self._create_file('/etc/passwd', 
            'root:x:0:0:root:/root:/bin/bash\n'
            'daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n'
            'nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin\n'
            'user:x:1000:1000:User:/home/user:/bin/bash\n'
        )
        
        self._create_file('/etc/shadow', 
            'root:$6$hash:19000:0:99999:7:::\nuser:$6$hash:19000:0:99999:7:::\n',
            permissions=0o640
        )
        
        self._create_file('/etc/group',
            'root:x:0:\ndaemon:x:1:\nuser:x:1000:\n'
        )
        
        self._create_file('/etc/os-release',
            'PRETTY_NAME="PyLinux 6.1.0"\nNAME="PyLinux"\nVERSION_ID="6.1"\nID=pylinux\n'
        )
        
        self._create_file('/etc/fstab',
            '/dev/sda1       /       ext4    errors=remount-ro 0 1\ntmpfs   /tmp    tmpfs   defaults 0 0\n'
        )
        
        self._create_file('/etc/resolv.conf', 'nameserver 8.8.8.8\nnameserver 8.8.4.4\n')
        self._create_file('/etc/motd', '\nWelcome to PyLinux 6.1.0!\n\n')
        self._create_file('/etc/shells', '/bin/sh\n/bin/bash\n')
        
        self._create_file('/etc/profile',
            'export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"\n'
        )

    def _create_proc_files(self):
        import psutil
        
        mem = psutil.virtual_memory()
        
        self._create_file('/proc/version', f'Linux version 6.1.0-pylinux\n')
        
        cpuinfo = ""
        for i in range(psutil.cpu_count() or 1):
            cpuinfo += f'processor\t: {i}\nmodel name\t: Virtual CPU\ncpu MHz\t\t: 2400.000\n\n'
        self._create_file('/proc/cpuinfo', cpuinfo)
        
        meminfo = f'MemTotal:       {mem.total // 1024} kB\nMemFree:        {mem.free // 1024} kB\nMemAvailable:   {mem.available // 1024} kB\n'
        self._create_file('/proc/meminfo', meminfo)
        
        self._create_file('/proc/loadavg', '0.00 0.00 0.00 1/100 1234\n')
        self._create_file('/proc/uptime', f'{time.time() - psutil.boot_time():.2f} 0.00\n')

    def _create_dev_files(self):
        devices = ['null', 'zero', 'random', 'urandom', 'tty', 'console', 'sda', 'sda1']
        for dev in devices:
            self._create_file(f'/dev/{dev}', '', 0o666)

    def _create_bin_files(self):
        bins = ['ls', 'cat', 'echo', 'pwd', 'cd', 'mkdir', 'rm', 'cp', 'mv', 'touch',
                'chmod', 'chown', 'grep', 'find', 'head', 'tail', 'wc', 'sort',
                'ps', 'top', 'kill', 'df', 'du', 'free', 'mount', 'umount',
                'ifconfig', 'ip', 'ping', 'netstat', 'curl', 'wget',
                'useradd', 'userdel', 'passwd', 'su', 'sudo', 'id', 'whoami',
                'date', 'cal', 'uptime', 'hostname', 'uname', 'dmesg',
                'systemctl', 'service', 'apt', 'dpkg', 'man', 'clear',
                'env', 'export', 'alias', 'history', 'bash', 'sh']
        for b in bins:
            self._create_file(f'/bin/{b}', f'#!/bin/bash\n# {b}\n', 0o755)
            self._create_file(f'/usr/bin/{b}', f'#!/bin/bash\n# {b}\n', 0o755)

    def _create_root_files(self):
        self._create_file('/root/.bashrc',
            'export PS1="\\u@\\h:\\w\\$ "\nalias ls="ls --color=auto"\nalias ll="ls -la"\n'
        )
        self._create_file('/root/.profile', 'if [ -f ~/.bashrc ]; then . ~/.bashrc; fi\n')
        self._create_file('/root/.bash_history', '')
        
        self._mkdir_p('/home/user')
        self._create_file('/home/user/.bashrc', 'export PS1="\\u@\\h:\\w\\$ "\n')

    def resolve_path(self, path):
        if not path:
            return self.cwd
        if path.startswith('~'):
            path = '/root' + path[1:]
        if not path.startswith('/'):
            path = self.cwd + '/' + path if self.cwd != '/' else '/' + path
        parts = path.split('/')
        resolved = []
        for part in parts:
            if part == '' or part == '.':
                continue
            elif part == '..':
                if resolved:
                    resolved.pop()
            else:
                resolved.append(part)
        return '/' + '/'.join(resolved) if resolved else '/'

    def exists(self, path):
        return self._get_node(self.resolve_path(path)) is not None

    def is_dir(self, path):
        node = self._get_node(self.resolve_path(path))
        return node is not None and node.is_dir

    def is_file(self, path):
        node = self._get_node(self.resolve_path(path))
        return node is not None and not node.is_dir

    def read_file(self, path):
        node = self._get_node(self.resolve_path(path))
        if node and not node.is_dir:
            node.accessed = time.time()
            return node.content
        return None

    def write_file(self, path, content, append=False):
        resolved = self.resolve_path(path)
        node = self._get_node(resolved)
        if node:
            if node.is_dir:
                return False
            if append:
                node.content += content
            else:
                node.content = content
            node.modified = time.time()
            node.size = len(node.content)
            return True
        else:
            parts = resolved.strip('/').split('/')
            filename = parts[-1]
            dirpath = '/' + '/'.join(parts[:-1]) if len(parts) > 1 else '/'
            parent = self._get_node(dirpath)
            if parent and parent.is_dir:
                parent.children[filename] = FileNode(filename, is_dir=False, content=content)
                return True
        return False

    def delete(self, path, recursive=False):
        resolved = self.resolve_path(path)
        if resolved == '/':
            return False
        parts = resolved.strip('/').split('/')
        filename = parts[-1]
        dirpath = '/' + '/'.join(parts[:-1]) if len(parts) > 1 else '/'
        parent = self._get_node(dirpath)
        if parent and parent.is_dir and filename in parent.children:
            node = parent.children[filename]
            if node.is_dir and node.children and not recursive:
                return False
            del parent.children[filename]
            return True
        return False

    def mkdir(self, path, parents=False):
        resolved = self.resolve_path(path)
        if parents:
            self._mkdir_p(resolved)
            return True
        parts = resolved.strip('/').split('/')
        dirname = parts[-1]
        parent_path = '/' + '/'.join(parts[:-1]) if len(parts) > 1 else '/'
        parent = self._get_node(parent_path)
        if parent and parent.is_dir:
            if dirname not in parent.children:
                parent.children[dirname] = FileNode(dirname, is_dir=True)
                return True
        return False

    def list_dir(self, path=None):
        if path is None:
            path = self.cwd
        node = self._get_node(self.resolve_path(path))
        if node and node.is_dir:
            return list(node.children.keys())
        return None

    def get_file_info(self, path):
        node = self._get_node(self.resolve_path(path))
        if node:
            return {
                'name': node.name,
                'is_dir': node.is_dir,
                'size': node.size if not node.is_dir else 4096,
                'permissions': node.permissions,
                'owner': node.owner,
                'group': node.group,
                'modified': node.modified,
                'inode': node.inode,
                'links': node.links
            }
        return None

    def chmod(self, path, mode):
        node = self._get_node(self.resolve_path(path))
        if node:
            node.permissions = mode
            return True
        return False

    def chown(self, path, owner=None, group=None):
        node = self._get_node(self.resolve_path(path))
        if node:
            if owner:
                node.owner = owner
            if group:
                node.group = group
            return True
        return False

    def copy(self, src, dst):
        src_node = self._get_node(self.resolve_path(src))
        if not src_node or src_node.is_dir:
            return False
        return self.write_file(dst, src_node.content)

    def move(self, src, dst):
        if self.copy(src, dst):
            return self.delete(src)
        return False

    def to_dict(self):
        return {'root': self.root.to_dict(), 'cwd': self.cwd, 'mounts': self.mounts}

    def load_from_dict(self, data):
        if 'root' in data:
            self.root = FileNode.from_dict(data['root'])
        if 'cwd' in data:
            self.cwd = data['cwd']
        if 'mounts' in data:
            self.mounts = data['mounts']
