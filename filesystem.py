import time
import json
from datetime import datetime
import hashlib

class INode:
    def __init__(self, name, is_dir=False, content=b'', permissions='755', owner='root', group='root'):
        self.name = name
        self.is_dir = is_dir
        self.content = content if isinstance(content, bytes) else content.encode()
        self.permissions = permissions
        self.owner = owner
        self.group = group
        self.created = time.time()
        self.modified = time.time()
        self.accessed = time.time()
        self.size = len(self.content) if not is_dir else 4096
        self.children = {} if is_dir else None
        self.links = 1
        self.inode_number = hash(f"{name}{time.time()}") % 1000000

    def to_dict(self):
        return {
            'name': self.name,
            'is_dir': self.is_dir,
            'content': self.content.decode('utf-8', errors='ignore') if self.content else '',
            'permissions': self.permissions,
            'owner': self.owner,
            'group': self.group,
            'created': self.created,
            'modified': self.modified,
            'accessed': self.accessed,
            'size': self.size,
            'children': {k: v.to_dict() for k, v in self.children.items()} if self.is_dir else None,
            'links': self.links,
            'inode_number': self.inode_number
        }

    @staticmethod
    def from_dict(data):
        inode = INode(
            data['name'],
            data['is_dir'],
            data.get('content', '').encode() if not data['is_dir'] else b'',
            data.get('permissions', '755'),
            data.get('owner', 'root'),
            data.get('group', 'root')
        )
        inode.created = data.get('created', time.time())
        inode.modified = data.get('modified', time.time())
        inode.accessed = data.get('accessed', time.time())
        inode.size = data.get('size', 0)
        inode.links = data.get('links', 1)
        inode.inode_number = data.get('inode_number', 0)
        if data['is_dir'] and data.get('children'):
            inode.children = {k: INode.from_dict(v) for k, v in data['children'].items()}
        return inode

class FileSystem:
    def __init__(self):
        self.root = INode('/', is_dir=True, permissions='755')
        self.current_dir = '/'
        self.total_blocks = 1048576
        self.used_blocks = 0
        self._initialize_filesystem()

    def _initialize_filesystem(self):
        dirs = [
            '/bin', '/boot', '/dev', '/etc', '/home', '/lib', '/lib64',
            '/media', '/mnt', '/opt', '/proc', '/root', '/run', '/sbin',
            '/srv', '/sys', '/tmp', '/usr', '/var',
            '/usr/bin', '/usr/sbin', '/usr/lib', '/usr/local',
            '/usr/local/bin', '/usr/local/sbin', '/usr/share',
            '/var/log', '/var/tmp', '/var/cache', '/var/lib',
            '/etc/init.d', '/etc/network', '/home/user'
        ]
        
        for dir_path in dirs:
            self.mkdir(dir_path, recursive=True)
        
        files = {
            '/etc/hostname': b'localhost\n',
            '/etc/hosts': b'127.0.0.1\tlocalhost\n::1\t\tlocalhost\n',
            '/etc/fstab': b'# /etc/fstab: static file system information\n',
            '/etc/passwd': b'root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:user:/home/user:/bin/bash\n',
            '/etc/group': b'root:x:0:\nuser:x:1000:\n',
            '/etc/shadow': b'root:*:19000:0:99999:7:::\nuser:*:19000:0:99999:7:::\n',
            '/etc/os-release': b'NAME="LinuxTerminal"\nVERSION="1.0"\nID=linuxterminal\nPRETTY_NAME="Linux Terminal 1.0"\n',
            '/proc/version': b'Linux version 5.15.0 (user@localhost) (gcc version 11.2.0) #1 SMP\n',
            '/proc/cpuinfo': b'processor\t: 0\nvendor_id\t: GenuineIntel\nmodel name\t: Virtual CPU\n',
            '/proc/meminfo': b'MemTotal: 2048000 kB\nMemFree: 1024000 kB\n',
            '/var/log/syslog': b'',
            '/var/log/dmesg': b'[    0.000000] Linux version 5.15.0\n',
        }
        
        for path, content in files.items():
            self.write_file(path, content)

    def _parse_path(self, path):
        if not path:
            return []
        if path == '/':
            return []
        path = path.strip('/')
        return path.split('/')

    def _get_node(self, path):
        if path == '/':
            return self.root
        
        parts = self._parse_path(path)
        current = self.root
        
        for part in parts:
            if not current.is_dir:
                return None
            if part not in current.children:
                return None
            current = current.children[part]
            current.accessed = time.time()
        
        return current

    def _get_parent_and_name(self, path):
        if path == '/':
            return None, '/'
        
        parts = self._parse_path(path)
        if not parts:
            return None, '/'
        
        name = parts[-1]
        parent_path = '/' + '/'.join(parts[:-1]) if len(parts) > 1 else '/'
        parent = self._get_node(parent_path)
        
        return parent, name

    def resolve_path(self, path):
        if not path:
            return self.current_dir
        
        if path.startswith('/'):
            return self._normalize_path(path)
        else:
            return self._normalize_path(f"{self.current_dir}/{path}")

    def _normalize_path(self, path):
        parts = []
        for part in path.split('/'):
            if part == '' or part == '.':
                continue
            elif part == '..':
                if parts:
                    parts.pop()
            else:
                parts.append(part)
        return '/' + '/'.join(parts) if parts else '/'

    def exists(self, path):
        resolved = self.resolve_path(path)
        return self._get_node(resolved) is not None

    def is_directory(self, path):
        resolved = self.resolve_path(path)
        node = self._get_node(resolved)
        return node is not None and node.is_dir

    def is_file(self, path):
        resolved = self.resolve_path(path)
        node = self._get_node(resolved)
        return node is not None and not node.is_dir

    def mkdir(self, path, recursive=False, permissions='755'):
        resolved = self.resolve_path(path)
        
        if self.exists(resolved):
            return False
        
        parent, name = self._get_parent_and_name(resolved)
        
        if parent is None:
            return False
        
        if not parent.is_dir:
            return False
        
        parent.children[name] = INode(name, is_dir=True, permissions=permissions)
        parent.modified = time.time()
        self.used_blocks += 1
        return True

    def read_file(self, path):
        resolved = self.resolve_path(path)
        node = self._get_node(resolved)
        
        if node is None:
            return None
        
        if node.is_dir:
            return None
        
        node.accessed = time.time()
        return node.content

    def write_file(self, path, content, append=False):
        resolved = self.resolve_path(path)
        parent, name = self._get_parent_and_name(resolved)
        
        if parent is None or not parent.is_dir:
            return False
        
        content_bytes = content if isinstance(content, bytes) else content.encode()
        
        if name in parent.children:
            node = parent.children[name]
            if node.is_dir:
                return False
            if append:
                node.content += content_bytes
            else:
                node.content = content_bytes
            node.modified = time.time()
            node.size = len(node.content)
        else:
            parent.children[name] = INode(name, is_dir=False, content=content_bytes)
            parent.modified = time.time()
            self.used_blocks += len(content_bytes) // 4096 + 1
        
        return True

    def list_directory(self, path):
        resolved = self.resolve_path(path)
        node = self._get_node(resolved)
        
        if node is None or not node.is_dir:
            return None
        
        node.accessed = time.time()
        return list(node.children.keys())

    def get_node_info(self, path):
        resolved = self.resolve_path(path)
        node = self._get_node(resolved)
        
        if node is None:
            return None
        
        return {
            'name': node.name,
            'is_dir': node.is_dir,
            'size': node.size,
            'permissions': node.permissions,
            'owner': node.owner,
            'group': node.group,
            'created': node.created,
            'modified': node.modified,
            'accessed': node.accessed,
            'links': node.links,
            'inode': node.inode_number
        }

    def remove(self, path, recursive=False):
        resolved = self.resolve_path(path)
        
        if resolved == '/':
            return False
        
        parent, name = self._get_parent_and_name(resolved)
        
        if parent is None or name not in parent.children:
            return False
        
        node = parent.children[name]
        
        if node.is_dir and node.children and not recursive:
            return False
        
        del parent.children[name]
        parent.modified = time.time()
        self.used_blocks -= 1
        return True

    def copy(self, src, dst):
        src_resolved = self.resolve_path(src)
        dst_resolved = self.resolve_path(dst)
        
        src_node = self._get_node(src_resolved)
        if src_node is None:
            return False
        
        if src_node.is_dir:
            return False
        
        return self.write_file(dst_resolved, src_node.content)

    def move(self, src, dst):
        if self.copy(src, dst):
            return self.remove(src)
        return False

    def get_disk_usage(self):
        total = self.total_blocks * 4
        used = self.used_blocks * 4
        available = total - used
        percent = int((used / total) * 100) if total > 0 else 0
        
        return {
            'total': total,
            'used': used,
            'available': available,
            'percent': percent
        }

    def serialize(self):
        return json.dumps({
            'root': self.root.to_dict(),
            'current_dir': self.current_dir,
            'used_blocks': self.used_blocks
        })

    def deserialize(self, data):
        try:
            obj = json.loads(data)
            self.root = INode.from_dict(obj['root'])
            self.current_dir = obj.get('current_dir', '/')
            self.used_blocks = obj.get('used_blocks', 0)
            return True
        except:
            return False
