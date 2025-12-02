import time
import json
import os
import stat
import pwd
import grp

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
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.root = FileNode('/', is_dir=True, permissions=0o755)
        self.cwd = '/root'
        self.mounts = {'/': {'device': '/dev/sda1', 'fstype': 'ext4', 'options': 'rw,relatime'}}
        self.open_files = {}
        self.fd_counter = 3

    def initialize(self):
        dirs = [
            '/bin', '/sbin', '/usr', '/usr/bin', '/usr/sbin', '/usr/lib', '/usr/lib64',
            '/usr/local', '/usr/local/bin', '/usr/local/sbin', '/usr/local/lib',
            '/usr/share', '/usr/share/man', '/usr/share/doc', '/usr/share/info',
            '/etc', '/etc/init.d', '/etc/default', '/etc/sysconfig', '/etc/systemd',
            '/etc/systemd/system', '/etc/network', '/etc/apt', '/etc/apt/sources.list.d',
            '/var', '/var/log', '/var/run', '/var/lock', '/var/tmp', '/var/spool',
            '/var/cache', '/var/cache/apt', '/var/lib', '/var/lib/apt', '/var/lib/dpkg',
            '/tmp', '/home', '/root', '/boot', '/boot/grub',
            '/dev', '/proc', '/sys', '/sys/class', '/sys/devices', '/sys/kernel',
            '/run', '/run/lock', '/run/user',
            '/opt', '/srv', '/mnt', '/media',
            '/lib', '/lib64', '/lib/modules', '/lib/firmware'
        ]
        
        for d in dirs:
            self._mkdir_p(d)

        self._create_etc_files()
        self._create_proc_files()
        self._create_dev_files()
        self._create_sys_files()
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
        
        hostname = os.uname().nodename if hasattr(os, 'uname') else 'localhost'
        
        self._create_file('/etc/hostname', f'{hostname}\n')
        self._create_file('/etc/hosts', f'127.0.0.1\tlocalhost\n127.0.1.1\t{hostname}\n::1\tlocalhost ip6-localhost ip6-loopback\nff02::1\tip6-allnodes\nff02::2\tip6-allrouters\n')
        
        self._create_file('/etc/passwd', 
            'root:x:0:0:root:/root:/bin/bash\n'
            'daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n'
            'bin:x:2:2:bin:/bin:/usr/sbin/nologin\n'
            'sys:x:3:3:sys:/dev:/usr/sbin/nologin\n'
            'sync:x:4:65534:sync:/bin:/bin/sync\n'
            'games:x:5:60:games:/usr/games:/usr/sbin/nologin\n'
            'man:x:6:12:man:/var/cache/man:/usr/sbin/nologin\n'
            'lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin\n'
            'mail:x:8:8:mail:/var/mail:/usr/sbin/nologin\n'
            'news:x:9:9:news:/var/spool/news:/usr/sbin/nologin\n'
            'uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin\n'
            'proxy:x:13:13:proxy:/bin:/usr/sbin/nologin\n'
            'www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\n'
            'backup:x:34:34:backup:/var/backups:/usr/sbin/nologin\n'
            'list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin\n'
            'irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin\n'
            'gnats:x:41:41:Gnats Bug-Reporting:/var/lib/gnats:/usr/sbin/nologin\n'
            'nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin\n'
            'systemd-network:x:100:102:systemd Network Management:/run/systemd:/usr/sbin/nologin\n'
            'systemd-resolve:x:101:103:systemd Resolver:/run/systemd:/usr/sbin/nologin\n'
            'messagebus:x:102:105::/nonexistent:/usr/sbin/nologin\n'
            'sshd:x:103:65534::/run/sshd:/usr/sbin/nologin\n'
            'user:x:1000:1000:User:/home/user:/bin/bash\n'
        )
        
        self._create_file('/etc/shadow', 
            'root:$6$rounds=4096$salt$hash:19000:0:99999:7:::\n'
            'user:$6$rounds=4096$salt$hash:19000:0:99999:7:::\n',
            permissions=0o640
        )
        
        self._create_file('/etc/group',
            'root:x:0:\n'
            'daemon:x:1:\n'
            'bin:x:2:\n'
            'sys:x:3:\n'
            'adm:x:4:\n'
            'tty:x:5:\n'
            'disk:x:6:\n'
            'lp:x:7:\n'
            'mail:x:8:\n'
            'news:x:9:\n'
            'uucp:x:10:\n'
            'man:x:12:\n'
            'proxy:x:13:\n'
            'kmem:x:15:\n'
            'dialout:x:20:\n'
            'fax:x:21:\n'
            'voice:x:22:\n'
            'cdrom:x:24:\n'
            'floppy:x:25:\n'
            'tape:x:26:\n'
            'sudo:x:27:user\n'
            'audio:x:29:\n'
            'dip:x:30:\n'
            'www-data:x:33:\n'
            'backup:x:34:\n'
            'operator:x:37:\n'
            'list:x:38:\n'
            'irc:x:39:\n'
            'src:x:40:\n'
            'gnats:x:41:\n'
            'shadow:x:42:\n'
            'utmp:x:43:\n'
            'video:x:44:\n'
            'sasl:x:45:\n'
            'plugdev:x:46:\n'
            'staff:x:50:\n'
            'games:x:60:\n'
            'users:x:100:\n'
            'nogroup:x:65534:\n'
            'user:x:1000:\n'
        )
        
        self._create_file('/etc/os-release',
            'PRETTY_NAME="PyLinux 6.1.0"\n'
            'NAME="PyLinux"\n'
            'VERSION_ID="6.1"\n'
            'VERSION="6.1.0 (Stable)"\n'
            'ID=pylinux\n'
            'ID_LIKE=debian\n'
            'HOME_URL="https://pylinux.example.com"\n'
            'SUPPORT_URL="https://pylinux.example.com/support"\n'
            'BUG_REPORT_URL="https://pylinux.example.com/bugs"\n'
        )
        
        self._create_file('/etc/lsb-release',
            'DISTRIB_ID=PyLinux\n'
            'DISTRIB_RELEASE=6.1\n'
            'DISTRIB_CODENAME=stable\n'
            'DISTRIB_DESCRIPTION="PyLinux 6.1.0"\n'
        )
        
        self._create_file('/etc/fstab',
            '# /etc/fstab: static file system information\n'
            '#\n'
            '# <file system> <mount point> <type> <options> <dump> <pass>\n'
            '/dev/sda1       /               ext4    errors=remount-ro 0       1\n'
            '/dev/sda2       none            swap    sw              0       0\n'
            'tmpfs           /tmp            tmpfs   defaults        0       0\n'
            'tmpfs           /run            tmpfs   defaults        0       0\n'
            'proc            /proc           proc    defaults        0       0\n'
            'sysfs           /sys            sysfs   defaults        0       0\n'
            'devpts          /dev/pts        devpts  defaults        0       0\n'
        )
        
        self._create_file('/etc/resolv.conf',
            '# Generated by NetworkManager\n'
            'nameserver 8.8.8.8\n'
            'nameserver 8.8.4.4\n'
            'nameserver 1.1.1.1\n'
        )
        
        self._create_file('/etc/nsswitch.conf',
            'passwd:         files systemd\n'
            'group:          files systemd\n'
            'shadow:         files\n'
            'gshadow:        files\n'
            'hosts:          files dns\n'
            'networks:       files\n'
            'protocols:      files\n'
            'services:       files\n'
            'ethers:         files\n'
            'rpc:            files\n'
        )
        
        self._create_file('/etc/shells',
            '/bin/sh\n'
            '/bin/bash\n'
            '/bin/dash\n'
            '/bin/zsh\n'
            '/usr/bin/zsh\n'
        )
        
        self._create_file('/etc/profile',
            '# /etc/profile: system-wide .profile file\n\n'
            'if [ "$(id -u)" -eq 0 ]; then\n'
            '  PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"\n'
            'else\n'
            '  PATH="/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games"\n'
            'fi\n'
            'export PATH\n\n'
            'if [ -d /etc/profile.d ]; then\n'
            '  for i in /etc/profile.d/*.sh; do\n'
            '    if [ -r $i ]; then\n'
            '      . $i\n'
            '    fi\n'
            '  done\n'
            'fi\n'
        )
        
        self._create_file('/etc/bash.bashrc',
            '# System-wide .bashrc file\n\n'
            'if ! shopt -oq posix; then\n'
            '  if [ -f /usr/share/bash-completion/bash_completion ]; then\n'
            '    . /usr/share/bash-completion/bash_completion\n'
            '  elif [ -f /etc/bash_completion ]; then\n'
            '    . /etc/bash_completion\n'
            '  fi\n'
            'fi\n'
        )
        
        self._create_file('/etc/inputrc',
            '# Readline initialization file\n'
            'set bell-style none\n'
            'set show-all-if-ambiguous on\n'
            'set completion-ignore-case on\n'
            '"\\e[A": history-search-backward\n'
            '"\\e[B": history-search-forward\n'
        )
        
        self._create_file('/etc/motd',
            '\n'
            '  ____        _     _                  \n'
            ' |  _ \\ _   _| |   (_)_ __  _   ___  __\n'
            ' | |_) | | | | |   | | \'_ \\| | | \\ \\/ /\n'
            ' |  __/| |_| | |___| | | | | |_| |>  < \n'
            ' |_|    \\__, |_____|_|_| |_|\\__,_/_/\\_\\\n'
            '        |___/                          \n'
            '\n'
            ' Welcome to PyLinux 6.1.0!\n\n'
        )
        
        self._create_file('/etc/issue', 'PyLinux 6.1.0 \\n \\l\n\n')
        self._create_file('/etc/issue.net', 'PyLinux 6.1.0\n')
        
        self._create_file('/etc/timezone', 'UTC\n')
        self._create_file('/etc/localtime', '')
        
        self._create_file('/etc/environment', 'PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"\n')
        
        self._create_file('/etc/apt/sources.list',
            'deb http://deb.pylinux.org/pylinux stable main contrib non-free\n'
            'deb-src http://deb.pylinux.org/pylinux stable main contrib non-free\n'
            'deb http://security.pylinux.org/pylinux-security stable-security main contrib non-free\n'
            'deb-src http://security.pylinux.org/pylinux-security stable-security main contrib non-free\n'
        )

    def _create_proc_files(self):
        import psutil
        
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        self._create_file('/proc/version', f'Linux version 6.1.0-pylinux (root@buildhost) (gcc version 12.2.0) #1 SMP PREEMPT_DYNAMIC {time.strftime("%a %b %d %H:%M:%S UTC %Y")}\n')
        
        cpuinfo = ""
        for i in range(psutil.cpu_count()):
            cpuinfo += f'''processor\t: {i}
vendor_id\t: GenuineIntel
cpu family\t: 6
model\t\t: 142
model name\t: Intel(R) Core(TM) i7 CPU
stepping\t: 10
microcode\t: 0xea
cpu MHz\t\t: {psutil.cpu_freq().current if psutil.cpu_freq() else 2400.000:.3f}
cache size\t: 8192 KB
physical id\t: 0
siblings\t: {psutil.cpu_count()}
core id\t\t: {i}
cpu cores\t: {psutil.cpu_count(logical=False) or psutil.cpu_count()}
apicid\t\t: {i}
initial apicid\t: {i}
fpu\t\t: yes
fpu_exception\t: yes
cpuid level\t: 22
wp\t\t: yes
flags\t\t: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss ht syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon rep_good nopl xtopology cpuid pni pclmulqdq ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand hypervisor lahf_lm abm 3dnowprefetch cpuid_fault invpcid_single pti ssbd ibrs ibpb stibp fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid rdseed adx smap clflushopt xsaveopt xsavec xgetbv1 xsaves arat md_clear
bugs\t\t: spectre_v1 spectre_v2 spec_store_bypass mds swapgs itlb_multihit srbds
bogomips\t: {psutil.cpu_freq().current * 2 if psutil.cpu_freq() else 4800.00:.2f}
clflush size\t: 64
cache_alignment\t: 64
address sizes\t: 45 bits physical, 48 bits virtual
power management:

'''
        self._create_file('/proc/cpuinfo', cpuinfo)
        
        meminfo = f'''MemTotal:       {mem.total // 1024:>12} kB
MemFree:        {mem.free // 1024:>12} kB
MemAvailable:   {mem.available // 1024:>12} kB
Buffers:        {mem.buffers // 1024 if hasattr(mem, 'buffers') else 0:>12} kB
Cached:         {mem.cached // 1024 if hasattr(mem, 'cached') else 0:>12} kB
SwapCached:     {0:>12} kB
Active:         {mem.active // 1024 if hasattr(mem, 'active') else 0:>12} kB
Inactive:       {mem.inactive // 1024 if hasattr(mem, 'inactive') else 0:>12} kB
SwapTotal:      {swap.total // 1024:>12} kB
SwapFree:       {swap.free // 1024:>12} kB
Dirty:          {0:>12} kB
Writeback:      {0:>12} kB
AnonPages:      {0:>12} kB
Mapped:         {0:>12} kB
Shmem:          {mem.shared // 1024 if hasattr(mem, 'shared') else 0:>12} kB
Slab:           {0:>12} kB
SReclaimable:   {0:>12} kB
SUnreclaim:     {0:>12} kB
KernelStack:    {0:>12} kB
PageTables:     {0:>12} kB
NFS_Unstable:   {0:>12} kB
Bounce:         {0:>12} kB
WritebackTmp:   {0:>12} kB
CommitLimit:    {(mem.total + swap.total) // 2 // 1024:>12} kB
Committed_AS:   {mem.used // 1024:>12} kB
VmallocTotal:   {34359738367:>12} kB
VmallocUsed:    {0:>12} kB
VmallocChunk:   {0:>12} kB
'''
        self._create_file('/proc/meminfo', meminfo)
        
        try:
            loadavg = psutil.getloadavg()
            self._create_file('/proc/loadavg', f'{loadavg[0]:.2f} {loadavg[1]:.2f} {loadavg[2]:.2f} 1/100 1234\n')
        except:
            self._create_file('/proc/loadavg', '0.00 0.00 0.00 1/100 1234\n')
        
        self._create_file('/proc/uptime', f'{time.time() - psutil.boot_time():.2f} {time.time() - psutil.boot_time():.2f}\n')
        
        stat_content = f'''cpu  {psutil.cpu_times().user:.0f} {psutil.cpu_times().nice:.0f} {psutil.cpu_times().system:.0f} {psutil.cpu_times().idle:.0f} {psutil.cpu_times().iowait:.0f} 0 {psutil.cpu_times().irq:.0f} {psutil.cpu_times().softirq:.0f} 0 0
'''
        for i in range(psutil.cpu_count()):
            times = psutil.cpu_times(percpu=True)[i]
            stat_content += f'cpu{i} {times.user:.0f} {times.nice:.0f} {times.system:.0f} {times.idle:.0f} {times.iowait:.0f} 0 {times.irq:.0f} {times.softirq:.0f} 0 0\n'
        
        stat_content += f'''intr 0
ctxt 0
btime {int(psutil.boot_time())}
processes 1234
procs_running 1
procs_blocked 0
softirq 0 0 0 0 0 0 0 0 0 0 0
'''
        self._create_file('/proc/stat', stat_content)
        
        self._create_file('/proc/filesystems',
            'nodev\tsysfs\n'
            'nodev\ttmpfs\n'
            'nodev\tbdev\n'
            'nodev\tproc\n'
            'nodev\tcgroup\n'
            'nodev\tcgroup2\n'
            'nodev\tcpuset\n'
            'nodev\tdevtmpfs\n'
            'nodev\tdebugfs\n'
            'nodev\tsecurityfs\n'
            'nodev\tpstore\n'
            'nodev\tbpf\n'
            '\text3\n'
            '\text4\n'
            '\text2\n'
            '\txfs\n'
            '\tbtrfs\n'
            '\tvfat\n'
            'nodev\tfuseblk\n'
            'nodev\tfuse\n'
            'nodev\tfusectl\n'
        )
        
        mounts = '''/dev/sda1 / ext4 rw,relatime 0 0
tmpfs /tmp tmpfs rw,nosuid,nodev 0 0
tmpfs /run tmpfs rw,nosuid,nodev,mode=755 0 0
proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0
sysfs /sys sysfs rw,nosuid,nodev,noexec,relatime 0 0
devpts /dev/pts devpts rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000 0 0
'''
        self._create_file('/proc/mounts', mounts)
        self._create_file('/proc/self/mounts', mounts)
        
        self._create_file('/proc/cmdline', 'BOOT_IMAGE=/boot/vmlinuz-6.1.0-pylinux root=/dev/sda1 ro quiet\n')
        
        self._create_file('/proc/sys/kernel/hostname', 'localhost\n')
        self._create_file('/proc/sys/kernel/ostype', 'Linux\n')
        self._create_file('/proc/sys/kernel/osrelease', '6.1.0-pylinux\n')
        self._create_file('/proc/sys/kernel/version', '#1 SMP PREEMPT_DYNAMIC\n')

    def _create_dev_files(self):
        devices = [
            ('null', 0o666), ('zero', 0o666), ('full', 0o666),
            ('random', 0o666), ('urandom', 0o666),
            ('tty', 0o666), ('tty0', 0o620), ('tty1', 0o620),
            ('console', 0o600), ('ptmx', 0o666),
            ('sda', 0o660), ('sda1', 0o660), ('sda2', 0o660),
            ('stdin', 0o666), ('stdout', 0o666), ('stderr', 0o666),
            ('fd', 0o755), ('core', 0o666)
        ]
        
        for dev, perm in devices:
            self._create_file(f'/dev/{dev}', '', perm)

    def _create_sys_files(self):
        self._create_file('/sys/class/net/lo/address', '00:00:00:00:00:00\n')
        self._create_file('/sys/class/net/lo/operstate', 'unknown\n')
        self._create_file('/sys/class/net/eth0/address', '02:42:ac:11:00:02\n')
        self._create_file('/sys/class/net/eth0/operstate', 'up\n')
        
        self._create_file('/sys/kernel/mm/transparent_hugepage/enabled', '[always] madvise never\n')
        self._create_file('/sys/devices/system/cpu/online', f'0-{psutil.cpu_count()-1}\n')

    def _create_bin_files(self):
        import psutil
        
        bins = ['ls', 'cat', 'echo', 'pwd', 'cd', 'mkdir', 'rm', 'cp', 'mv', 'touch',
                'chmod', 'chown', 'grep', 'find', 'head', 'tail', 'wc', 'sort', 'uniq',
                'cut', 'tr', 'sed', 'awk', 'diff', 'tar', 'gzip', 'gunzip', 'zip', 'unzip',
                'ps', 'top', 'kill', 'killall', 'nice', 'renice', 'nohup', 'bg', 'fg', 'jobs',
                'df', 'du', 'free', 'mount', 'umount', 'fdisk', 'mkfs', 'fsck',
                'ifconfig', 'ip', 'ping', 'netstat', 'ss', 'route', 'traceroute', 'nslookup', 'dig', 'host', 'curl', 'wget',
                'ssh', 'scp', 'sftp', 'rsync', 'nc', 'telnet', 'ftp',
                'useradd', 'userdel', 'usermod', 'groupadd', 'groupdel', 'passwd', 'su', 'sudo', 'id', 'whoami', 'who', 'w', 'last', 'finger',
                'date', 'cal', 'uptime', 'hostname', 'uname', 'arch', 'dmesg', 'lsmod', 'modprobe', 'insmod', 'rmmod',
                'systemctl', 'service', 'journalctl', 'crontab', 'at', 'batch',
                'apt', 'apt-get', 'apt-cache', 'dpkg', 'yum', 'dnf', 'rpm', 'snap', 'flatpak',
                'man', 'info', 'help', 'whatis', 'whereis', 'which', 'type', 'file', 'stat', 'lsof',
                'env', 'export', 'set', 'unset', 'alias', 'unalias', 'source', 'exec', 'eval',
                'history', 'clear', 'reset', 'tput', 'stty', 'tee', 'xargs', 'time', 'watch',
                'ln', 'readlink', 'realpath', 'basename', 'dirname', 'mktemp', 'sync',
                'vi', 'vim', 'nano', 'ed', 'less', 'more', 'view',
                'iptables', 'ip6tables', 'ufw', 'firewall-cmd',
                'cron', 'anacron', 'logrotate',
                'bash', 'sh', 'dash', 'zsh', 'fish',
                'python', 'python3', 'perl', 'ruby', 'node', 'php',
                'gcc', 'g++', 'make', 'cmake', 'ld', 'as', 'ar', 'nm', 'objdump', 'strip',
                'git', 'svn', 'hg', 'cvs',
                'dd', 'od', 'hexdump', 'xxd', 'strings', 'base64', 'md5sum', 'sha256sum',
                'lscpu', 'lsmem', 'lspci', 'lsusb', 'lsblk', 'blkid', 'hwinfo', 'dmidecode',
                'htop', 'iotop', 'iftop', 'nethogs', 'vmstat', 'iostat', 'mpstat', 'sar', 'pidstat',
                'strace', 'ltrace', 'gdb', 'objcopy', 'size', 'readelf',
                'shutdown', 'reboot', 'poweroff', 'halt', 'init', 'telinit', 'runlevel',
                'chroot', 'pivot_root', 'switch_root',
                'true', 'false', 'yes', 'no', 'sleep', 'usleep', 'nproc', 'seq', 'shuf', 'factor', 'expr', 'bc', 'dc',
                'test', '[', '[[', 'printf', 'read', 'getopts'
        ]
        
        for b in bins:
            self._create_file(f'/bin/{b}', f'#!/bin/bash\n# {b} binary\n', 0o755)
            self._create_file(f'/usr/bin/{b}', f'#!/bin/bash\n# {b} binary\n', 0o755)

        sbins = ['fdisk', 'mkfs', 'fsck', 'mount', 'umount', 'ifconfig', 'route', 'iptables',
                 'useradd', 'userdel', 'groupadd', 'groupdel', 'init', 'shutdown', 'reboot',
                 'systemctl', 'service', 'modprobe', 'insmod', 'rmmod', 'dmesg', 'sysctl',
                 'grub-install', 'grub-mkconfig', 'update-grub', 'mkinitramfs', 'update-initramfs',
                 'lvs', 'vgs', 'pvs', 'lvcreate', 'vgcreate', 'pvcreate', 'mdadm',
                 'parted', 'gdisk', 'sgdisk', 'partprobe', 'blockdev', 'losetup',
                 'ip', 'ss', 'tc', 'bridge', 'netplan', 'networkctl',
                 'visudo', 'vipw', 'vigr', 'pwck', 'grpck',
                 'agetty', 'getty', 'login', 'nologin', 'sulogin',
                 'pivot_root', 'switch_root', 'chroot',
                 'mkswap', 'swapon', 'swapoff', 'zramctl',
                 'udevd', 'udevadm', 'systemd-udevd',
                 'chronyd', 'ntpd', 'timedatectl',
                 'auditd', 'auditctl', 'ausearch', 'aureport']
        
        for s in sbins:
            self._create_file(f'/sbin/{s}', f'#!/bin/bash\n# {s} binary\n', 0o755)
            self._create_file(f'/usr/sbin/{s}', f'#!/bin/bash\n# {s} binary\n', 0o755)

    def _create_root_files(self):
        self._create_file('/root/.bashrc',
            '# ~/.bashrc: executed by bash(1) for non-login shells.\n\n'
            'export PS1="\\[\\033[01;32m\\]\\u@\\h\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ "\n\n'
            'alias ls="ls --color=auto"\n'
            'alias ll="ls -la"\n'
            'alias la="ls -A"\n'
            'alias l="ls -CF"\n'
            'alias grep="grep --color=auto"\n'
            'alias df="df -h"\n'
            'alias du="du -h"\n'
            'alias free="free -h"\n\n'
            'export HISTSIZE=1000\n'
            'export HISTFILESIZE=2000\n'
            'export HISTCONTROL=ignoreboth\n'
            'shopt -s histappend\n'
            'shopt -s checkwinsize\n'
        )
        
        self._create_file('/root/.bash_profile',
            '# ~/.bash_profile\n\n'
            'if [ -f ~/.bashrc ]; then\n'
            '    . ~/.bashrc\n'
            'fi\n'
        )
        
        self._create_file('/root/.profile',
            '# ~/.profile: executed by Bourne-compatible login shells.\n\n'
            'if [ -n "$BASH_VERSION" ]; then\n'
            '    if [ -f "$HOME/.bashrc" ]; then\n'
            '        . "$HOME/.bashrc"\n'
            '    fi\n'
            'fi\n\n'
            'PATH="$HOME/bin:$HOME/.local/bin:$PATH"\n'
        )
        
        self._create_file('/root/.bash_history', '')
        self._create_file('/root/.vimrc', 'set nocompatible\nset number\nset syntax=on\n')
        self._create_file('/root/.nanorc', 'set autoindent\nset tabsize 4\nset linenumbers\n')
        
        self._mkdir_p('/home/user')
        self._create_file('/home/user/.bashrc', self._get_node('/root/.bashrc').content)
        self._create_file('/home/user/.profile', self._get_node('/root/.profile').content)

    def resolve_path(self, path):
        if not path:
            return self.cwd
        
        if path.startswith('~'):
            home = self.get_home_dir()
            path = home + path[1:]
        
        if not path.startswith('/'):
            if self.cwd == '/':
                path = '/' + path
            else:
                path = self.cwd + '/' + path
        
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

    def get_home_dir(self):
        user = self._get_current_user()
        if user == 'root':
            return '/root'
        return f'/home/{user}'

    def _get_current_user(self):
        return 'root'

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
                'accessed': node.accessed,
                'created': node.created,
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
        if not src_node:
            return False
        
        if src_node.is_dir:
            return self._copy_dir(src, dst)
        
        return self.write_file(dst, src_node.content)

    def _copy_dir(self, src, dst):
        self.mkdir(dst, parents=True)
        src_node = self._get_node(self.resolve_path(src))
        if src_node and src_node.is_dir:
            for name, child in src_node.children.items():
                child_src = f"{src}/{name}"
                child_dst = f"{dst}/{name}"
                if child.is_dir:
                    self._copy_dir(child_src, child_dst)
                else:
                    self.write_file(child_dst, child.content)
        return True

    def move(self, src, dst):
        if self.copy(src, dst):
            return self.delete(src, recursive=True)
        return False

    def to_dict(self):
        return {
            'root': self.root.to_dict(),
            'cwd': self.cwd,
            'mounts': self.mounts
        }

    def load_from_dict(self, data):
        if 'root' in data:
            self.root = FileNode.from_dict(data['root'])
        if 'cwd' in data:
            self.cwd = data['cwd']
        if 'mounts' in data:
            self.mounts = data['mounts']
