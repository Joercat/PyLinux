import time
import random
from datetime import datetime
from editor import Editor

class CommandHandler:
    def __init__(self, filesystem, process_manager, memory_manager, user_manager, 
                 network_manager, device_manager, package_manager, session):
        self.fs = filesystem
        self.pm = process_manager
        self.mm = memory_manager
        self.um = user_manager
        self.nm = network_manager
        self.dm = device_manager
        self.pkg = package_manager
        self.session = session
        self.editor = Editor(filesystem)
        self.history = []
        self.aliases = {
            'll': 'ls -la',
            'la': 'ls -a',
        }

    def get_prompt(self):
        user = self.session.current_user
        host = self.session.hostname
        cwd = self.fs.current_dir
        if cwd == f'/home/{user}' or cwd == '/root':
            cwd = '~'
        symbol = '#' if user == 'root' else '$'
        return f'{user}@{host}:{cwd}{symbol} '

    def execute(self, command_line):
        if not command_line:
            return ''
        
        self.history.append(command_line)
        
        parts = command_line.split()
        if not parts:
            return ''
        
        cmd = parts[0]
        args = parts[1:]
        
        if cmd in self.aliases:
            return self.execute(self.aliases[cmd] + ' ' + ' '.join(args))
        
        commands = {
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'pwd': self.cmd_pwd,
            'cat': self.cmd_cat,
            'echo': self.cmd_echo,
            'mkdir': self.cmd_mkdir,
            'rmdir': self.cmd_rmdir,
            'rm': self.cmd_rm,
            'touch': self.cmd_touch,
            'cp': self.cmd_cp,
            'mv': self.cmd_mv,
            'find': self.cmd_find,
            'grep': self.cmd_grep,
            'ps': self.cmd_ps,
            'kill': self.cmd_kill,
            'top': self.cmd_top,
            'free': self.cmd_free,
            'df': self.cmd_df,
            'du': self.cmd_du,
            'mount': self.cmd_mount,
            'umount': self.cmd_umount,
            'ifconfig': self.cmd_ifconfig,
            'ip': self.cmd_ip,
            'ping': self.cmd_ping,
            'netstat': self.cmd_netstat,
            'route': self.cmd_route,
            'whoami': self.cmd_whoami,
            'who': self.cmd_who,
            'w': self.cmd_w,
            'id': self.cmd_id,
            'uname': self.cmd_uname,
            'hostname': self.cmd_hostname,
            'uptime': self.cmd_uptime,
            'date': self.cmd_date,
            'clear': self.cmd_clear,
            'history': self.cmd_history,
            'alias': self.cmd_alias,
            'export': self.cmd_export,
            'env': self.cmd_env,
            'which': self.cmd_which,
            'whereis': self.cmd_whereis,
            'man': self.cmd_man,
            'info': self.cmd_info,
            'help': self.cmd_help,
            'apt': self.cmd_apt,
            'apt-get': self.cmd_apt,
            'dpkg': self.cmd_dpkg,
            'lsblk': self.cmd_lsblk,
            'lspci': self.cmd_lspci,
            'lsusb': self.cmd_lsusb,
            'dmesg': self.cmd_dmesg,
            'systemctl': self.cmd_systemctl,
            'service': self.cmd_service,
            'journalctl': self.cmd_journalctl,
            'tar': self.cmd_tar,
            'gzip': self.cmd_gzip,
            'gunzip': self.cmd_gunzip,
            'zip': self.cmd_zip,
            'unzip': self.cmd_unzip,
            'wget': self.cmd_wget,
            'curl': self.cmd_curl,
            'ssh': self.cmd_ssh,
            'scp': self.cmd_scp,
            'chmod': self.cmd_chmod,
            'chown': self.cmd_chown,
            'chgrp': self.cmd_chgrp,
            'stat': self.cmd_stat,
            'file': self.cmd_file,
            'head': self.cmd_head,
            'tail': self.cmd_tail,
            'less': self.cmd_less,
            'more': self.cmd_more,
            'wc': self.cmd_wc,
            'sort': self.cmd_sort,
            'uniq': self.cmd_uniq,
            'diff': self.cmd_diff,
            'ln': self.cmd_ln,
            'readlink': self.cmd_readlink,
        }
        
        if cmd in commands:
            try:
                return commands[cmd](args)
            except Exception as e:
                return f'{cmd}: error: {str(e)}'
        else:
            return f'{cmd}: command not found'

    def cmd_ls(self, args):
        show_all = '-a' in args or '-la' in args or '-al' in args
        long_format = '-l' in args or '-la' in args or '-al' in args
        
        path = '.'
        for arg in args:
            if not arg.startswith('-'):
                path = arg
                break
        
        items = self.fs.list_directory(path)
        if items is None:
            return f'ls: cannot access \'{path}\': No such file or directory'
        
        if not show_all:
            items = [i for i in items if not i.startswith('.')]
        
        if not long_format:
            return '  '.join(sorted(items))
        
        result = []
        for item in sorted(items):
            item_path = f"{path}/{item}" if path != '.' else item
            info = self.fs.get_node_info(item_path)
            if info:
                perms = 'd' if info['is_dir'] else '-'
                perms += info['permissions']
                mtime = datetime.fromtimestamp(info['modified']).strftime('%b %d %H:%M')
                result.append(f"{perms} {info['links']:2d} {info['owner']:8s} {info['group']:8s} {info['size']:8d} {mtime} {item}")
        
        return '\n'.join(result) if result else ''

    def cmd_cd(self, args):
        if not args:
            target = self.session.env_vars.get('HOME', '/root')
        elif args[0] == '-':
            return 'cd: OLDPWD not set'
        elif args[0] == '~':
            target = self.session.env_vars.get('HOME', '/root')
        else:
            target = args[0]
        
        resolved = self.fs.resolve_path(target)
        
        if not self.fs.exists(resolved):
            return f'cd: {target}: No such file or directory'
        
        if not self.fs.is_directory(resolved):
            return f'cd: {target}: Not a directory'
        
        self.fs.current_dir = resolved
        return ''

    def cmd_pwd(self, args):
        return self.fs.current_dir

    def cmd_cat(self, args):
        if not args:
            return 'cat: missing file operand'
        
        results = []
        for filepath in args:
            content = self.fs.read_file(filepath)
            if content is None:
                results.append(f'cat: {filepath}: No such file or directory')
            else:
                results.append(content.decode('utf-8', errors='ignore'))
        
        return '\n'.join(results)

    def cmd_echo(self, args):
        return ' '.join(args)

    def cmd_mkdir(self, args):
        if not args:
            return 'mkdir: missing operand'
        
        recursive = '-p' in args
        dirs = [a for a in args if not a.startswith('-')]
        
        for dirname in dirs:
            success = self.fs.mkdir(dirname, recursive=recursive)
            if not success:
                return f'mkdir: cannot create directory \'{dirname}\': File exists'
        
        return ''

    def cmd_rmdir(self, args):
        if not args:
            return 'rmdir: missing operand'
        
        for dirname in args:
            if not self.fs.is_directory(dirname):
                return f'rmdir: failed to remove \'{dirname}\': Not a directory'
            
            success = self.fs.remove(dirname)
            if not success:
                return f'rmdir: failed to remove \'{dirname}\': Directory not empty'
        
        return ''

    def cmd_rm(self, args):
        if not args:
            return 'rm: missing operand'
        
        recursive = '-r' in args or '-rf' in args
        force = '-f' in args or '-rf' in args
        files = [a for a in args if not a.startswith('-')]
        
        for filepath in files:
            if not self.fs.exists(filepath) and not force:
                return f'rm: cannot remove \'{filepath}\': No such file or directory'
            
            success = self.fs.remove(filepath, recursive=recursive)
            if not success and not force:
                return f'rm: cannot remove \'{filepath}\': Is a directory'
        
        return ''

    def cmd_touch(self, args):
        if not args:
            return 'touch: missing file operand'
        
        for filepath in args:
            if not self.fs.exists(filepath):
                self.fs.write_file(filepath, b'')
        
        return ''

    def cmd_cp(self, args):
        if len(args) < 2:
            return 'cp: missing file operand'
        
        src = args[0]
        dst = args[1]
        
        if not self.fs.exists(src):
            return f'cp: cannot stat \'{src}\': No such file or directory'
        
        success = self.fs.copy(src, dst)
        if not success:
            return f'cp: cannot copy \'{src}\' to \'{dst}\''
        
        return ''

    def cmd_mv(self, args):
        if len(args) < 2:
            return 'mv: missing file operand'
        
        src = args[0]
        dst = args[1]
        
        if not self.fs.exists(src):
            return f'mv: cannot stat \'{src}\': No such file or directory'
        
        success = self.fs.move(src, dst)
        if not success:
            return f'mv: cannot move \'{src}\' to \'{dst}\''
        
        return ''

    def cmd_find(self, args):
        path = '.' if not args else args[0]
        return 'find: limited implementation'

    def cmd_grep(self, args):
        return 'grep: limited implementation'

    def cmd_ps(self, args):
        processes = self.pm.list_processes()
        
        show_all = 'aux' in args or '-e' in args or '-A' in args
        
        result = ['  PID TTY          TIME CMD']
        for proc in processes:
            runtime = proc.get_runtime()
            minutes = int(runtime // 60)
            seconds = int(runtime % 60)
            time_str = f'{minutes:02d}:{seconds:02d}'
            result.append(f'{proc.pid:5d} pts/0    {time_str} {proc.command if proc.command else proc.name}')
        
        return '\n'.join(result)

    def cmd_kill(self, args):
        if not args:
            return 'kill: missing operand'
        
        try:
            pid = int(args[0])
            success = self.pm.kill_process(pid)
            if success:
                return ''
            else:
                return f'kill: ({pid}) - No such process'
        except ValueError:
            return f'kill: invalid PID'

    def cmd_top(self, args):
        processes = self.pm.list_processes()
        mem_stats = self.mm.get_stats()
        
        uptime_seconds = time.time() - self.session.uptime_start if self.session.uptime_start else 0
        uptime_minutes = int(uptime_seconds // 60)
        
        load_avg = f'{random.uniform(0.0, 2.0):.2f}, {random.uniform(0.0, 2.0):.2f}, {random.uniform(0.0, 2.0):.2f}'
        
        result = [
            f'top - {datetime.now().strftime("%H:%M:%S")} up {uptime_minutes} min,  1 user,  load average: {load_avg}',
            f'Tasks: {len(processes)} total,   1 running, {len(processes)-1} sleeping,   0 stopped,   0 zombie',
            f'%Cpu(s):  {random.uniform(0.0, 10.0):.1f} us,  {random.uniform(0.0, 5.0):.1f} sy,  0.0 ni, {random.uniform(85.0, 99.0):.1f} id',
            f'MiB Mem :   {mem_stats["total"]//1024//1024:.1f} total,   {mem_stats["free"]//1024//1024:.1f} free,   {mem_stats["used"]//1024//1024:.1f} used',
            f'MiB Swap:   {mem_stats["swap_total"]//1024//1024:.1f} total,   {mem_stats["swap_free"]//1024//1024:.1f} free,   {mem_stats["swap_used"]//1024//1024:.1f} used',
            '',
            '  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND'
        ]
        
        for proc in sorted(processes, key=lambda p: p.cpu_percent, reverse=True)[:15]:
            result.append(
                f'{proc.pid:5d} {proc.user:8s} {proc.priority:3d} {proc.nice:3d} '
                f'{proc.memory_kb*4:7d} {proc.memory_kb:6d} {proc.memory_kb//2:6d} {proc.state} '
                f'{proc.cpu_percent:5.1f} {(proc.memory_kb/mem_stats["total"]*100*1024):.1f} '
                f'  0:00.{random.randint(10,99)} {proc.name}'
            )
        
        return '\n'.join(result)

    def cmd_free(self, args):
        stats = self.mm.get_stats()
        human = '-h' in args
        
        def format_size(size):
            if human:
                return self.mm.format_bytes(size)
            return str(size // 1024)
        
        unit = '' if human else 'total        used        free      shared  buff/cache   available'
        
        result = [
            f'              {unit}',
            f'Mem:     {format_size(stats["total"]):>10s} {format_size(stats["used"]):>10s} '
            f'{format_size(stats["free"]):>10s} {format_size(stats["shared"]):>10s} '
            f'{format_size(stats["cached"]):>10s} {format_size(stats["available"]):>10s}',
            f'Swap:    {format_size(stats["swap_total"]):>10s} {format_size(stats["swap_used"]):>10s} '
            f'{format_size(stats["swap_free"]):>10s}'
        ]
        
        return '\n'.join(result)

    def cmd_df(self, args):
        usage = self.fs.get_disk_usage()
        human = '-h' in args
        
        def format_size(kb):
            if human:
                return self.mm.format_bytes(kb * 1024)
            return str(kb)
        
        header = 'Filesystem      Size  Used Avail Use% Mounted on'
        data = f'/dev/sda1      {format_size(usage["total"]):>5s} {format_size(usage["used"]):>5s} ' \
               f'{format_size(usage["available"]):>5s} {usage["percent"]:>3d}% /'
        
        return f'{header}\n{data}'

    def cmd_du(self, args):
        return 'du: limited implementation'

    def cmd_mount(self, args):
        return '/dev/sda1 on / type ext4 (rw,relatime)\nproc on /proc type proc (rw,nosuid,nodev,noexec,relatime)\nsysfs on /sys type sysfs (rw,nosuid,nodev,noexec,relatime)'

    def cmd_umount(self, args):
        return 'umount: limited implementation'

    def cmd_ifconfig(self, args):
        result = []
        for name in self.nm.list_interfaces():
            stats = self.nm.get_interface_stats(name)
            result.append(f'{name}: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu {stats["mtu"]}')
            if stats['ipv4']:
                result.append(f'        inet {stats["ipv4"]}  netmask 255.255.255.0  broadcast 192.168.1.255')
            if stats['ipv6']:
                result.append(f'        inet6 {stats["ipv6"]}  prefixlen 64  scopeid 0x20<link>')
            result.append(f'        ether {stats["mac"]}  txqueuelen 1000  (Ethernet)')
            result.append(f'        RX packets {stats["rx_packets"]}  bytes {stats["rx_bytes"]} ({self.mm.format_bytes(stats["rx_bytes"])})')
            result.append(f'        TX packets {stats["tx_packets"]}  bytes {stats["tx_bytes"]} ({self.mm.format_bytes(stats["tx_bytes"])})')
            result.append('')
        
        return '\n'.join(result)

    def cmd_ip(self, args):
        if not args or args[0] == 'addr':
            result = []
            idx = 1
            for name in self.nm.list_interfaces():
                stats = self.nm.get_interface_stats(name)
                result.append(f'{idx}: {name}: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu {stats["mtu"]} state {stats["state"]}')
                result.append(f'    link/ether {stats["mac"]} brd ff:ff:ff:ff:ff:ff')
                if stats['ipv4']:
                    result.append(f'    inet {stats["ipv4"]}/24 brd 192.168.1.255 scope global {name}')
                if stats['ipv6']:
                    result.append(f'    inet6 {stats["ipv6"]}/64 scope link')
                idx += 1
            return '\n'.join(result)
        
        return 'ip: limited implementation'

    def cmd_ping(self, args):
        if not args:
            return 'ping: usage error: Destination address required'
        
        host = args[0]
        count = 4
        
        result = [f'PING {host} (93.184.216.34) 56(84) bytes of data.']
        
        for i in range(count):
            latency = random.uniform(10.0, 100.0)
            result.append(f'64 bytes from {host}: icmp_seq={i+1} ttl=64 time={latency:.1f} ms')
        
        result.append('')
        result.append(f'--- {host} ping statistics ---')
        result.append(f'{count} packets transmitted, {count} received, 0% packet loss')
        
        return '\n'.join(result)

    def cmd_netstat(self, args):
        return 'Active Internet connections (w/o servers)\nProto Recv-Q Send-Q Local Address           Foreign Address         State'

    def cmd_route(self, args):
        result = ['Kernel IP routing table']
        result.append('Destination     Gateway         Genmask         Flags Metric Ref    Use Iface')
        
        for route in self.nm.get_routes():
            result.append(f'{route["destination"]:15s} {route["gateway"]:15s} {route["netmask"]:15s} UG    0      0        0 {route["interface"]}')
        
        return '\n'.join(result)

    def cmd_whoami(self, args):
        return self.session.current_user

    def cmd_who(self, args):
        return f'{self.session.current_user} pts/0        {datetime.now().strftime("%Y-%m-%d %H:%M")}'

    def cmd_w(self, args):
        uptime_seconds = time.time() - self.session.uptime_start if self.session.uptime_start else 0
        uptime_minutes = int(uptime_seconds // 60)
        
        result = [
            f' {datetime.now().strftime("%H:%M:%S")} up {uptime_minutes} min,  1 user,  load average: 0.00, 0.01, 0.05',
            'USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT',
            f'{self.session.current_user:8s} pts/0    -                {datetime.now().strftime("%H:%M")}    0.00s  0.01s  0.00s w'
        ]
        
        return '\n'.join(result)

    def cmd_id(self, args):
        user = self.um.get_user(self.session.current_user)
        if user:
            return f'uid={user.uid}({user.username}) gid={user.gid}({user.username}) groups={user.gid}({user.username})'
        return 'id: cannot find name for user ID'

    def cmd_uname(self, args):
        if '-a' in args:
            return 'Linux localhost 5.15.0-terminal #1 SMP x86_64 GNU/Linux'
        elif '-r' in args:
            return '5.15.0-terminal'
        elif '-s' in args or not args:
            return 'Linux'
        elif '-n' in args:
            return 'localhost'
        elif '-m' in args:
            return 'x86_64'
        return 'Linux'

    def cmd_hostname(self, args):
        return self.session.hostname

    def cmd_uptime(self, args):
        uptime_seconds = time.time() - self.session.uptime_start if self.session.uptime_start else 0
        uptime_minutes = int(uptime_seconds // 60)
        
        return f' {datetime.now().strftime("%H:%M:%S")} up {uptime_minutes} min,  1 user,  load average: 0.00, 0.01, 0.05'

    def cmd_date(self, args):
        return datetime.now().strftime('%a %b %d %H:%M:%S %Z %Y')

    def cmd_clear(self, args):
        return '\033[2J\033[H'

    def cmd_history(self, args):
        return '\n'.join([f'{i+1:5d}  {cmd}' for i, cmd in enumerate(self.history)])

    def cmd_alias(self, args):
        if not args:
            return '\n'.join([f'{k}=\'{v}\'' for k, v in self.aliases.items()])
        return ''

    def cmd_export(self, args):
        if not args:
            return '\n'.join([f'{k}={v}' for k, v in self.session.env_vars.items()])
        
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                self.session.env_vars[key] = value
        
        return ''

    def cmd_env(self, args):
        return '\n'.join([f'{k}={v}' for k, v in self.session.env_vars.items()])

    def cmd_which(self, args):
        if not args:
            return 'which: missing operand'
        return f'/usr/bin/{args[0]}'

    def cmd_whereis(self, args):
        if not args:
            return 'whereis: missing operand'
        return f'{args[0]}: /usr/bin/{args[0]} /usr/share/man/man1/{args[0]}.1.gz'

    def cmd_man(self, args):
        if not args:
            return 'What manual page do you want?'
        return f'Manual page for {args[0]} - use --help for command information'

    def cmd_info(self, args):
        return 'info: limited implementation'

    def cmd_help(self, args):
        return '''Available commands:
File operations: ls, cd, pwd, cat, echo, mkdir, rmdir, rm, touch, cp, mv, find, grep
Process management: ps, kill, top
Memory: free
Disk: df, du, mount, umount
Network: ifconfig, ip, ping, netstat, route
System info: whoami, who, w, id, uname, hostname, uptime, date
Utilities: clear, history, alias, export, env, which, whereis, man
Package management: apt, apt-get, dpkg
Hardware: lsblk, lspci, lsusb
System: dmesg, systemctl, service, journalctl
File utilities: chmod, chown, stat, file, head, tail, wc, sort
Special: shutdown, reboot'''

    def cmd_apt(self, args):
        if not args:
            return 'apt: command requires an operation'
        
        if args[0] == 'update':
            return 'Reading package lists... Done\nBuilding dependency tree... Done\nAll packages are up to date.'
        
        elif args[0] == 'install' and len(args) > 1:
            package = args[1]
            success, msg = self.pkg.install(package)
            return msg
        
        elif args[0] == 'remove' and len(args) > 1:
            package = args[1]
            success, msg = self.pkg.remove(package)
            return msg
        
        elif args[0] == 'search' and len(args) > 1:
            results = self.pkg.search(args[1])
            return '\n'.join([f'{p.name}/{p.version} - {p.description}' for p in results])
        
        elif args[0] == 'list':
            if '--installed' in args:
                packages = self.pkg.list_installed()
                return '\n'.join([f'{p.name}/{p.version}' for p in packages])
        
        return 'apt: invalid operation'

    def cmd_dpkg(self, args):
        if '-l' in args:
            packages = self.pkg.list_installed()
            result = ['Desired=Unknown/Install/Remove/Purge/Hold',
                     '| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend',
                     '|/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)',
                     '||/ Name           Version      Architecture Description']
            for p in packages:
                result.append(f'ii  {p.name:14s} {p.version:12s} amd64        {p.description}')
            return '\n'.join(result)
        return 'dpkg: limited implementation'

    def cmd_lsblk(self, args):
        result = ['NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT']
        result.append('sda      8:0    0   20G  0 disk')
        result.append('├─sda1   8:1    0   19G  0 part /')
        result.append('└─sda2   8:2    0    1G  0 part [SWAP]')
        return '\n'.join(result)

    def cmd_lspci(self, args):
        return '''00:00.0 Host bridge: Intel Corporation Virtual Host Bridge
00:01.0 VGA compatible controller: VMware SVGA II Adapter
00:02.0 Ethernet controller: Intel Corporation Virtual Ethernet Controller'''

    def cmd_lsusb(self, args):
        return '''Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 001 Device 002: ID 80ee:0021 VirtualBox USB Tablet'''

    def cmd_dmesg(self, args):
        content = self.fs.read_file('/var/log/dmesg')
        if content:
            return content.decode('utf-8', errors='ignore')
        return '[    0.000000] Linux version 5.15.0-terminal'

    def cmd_systemctl(self, args):
        if not args:
            return 'systemctl: missing operation'
        
        if args[0] == 'status':
            return '● localhost\n    State: running\n     Jobs: 0 queued\n   Failed: 0 units'
        
        return 'systemctl: limited implementation'

    def cmd_service(self, args):
        return 'service: limited implementation'

    def cmd_journalctl(self, args):
        return '-- Logs begin at ' + datetime.now().strftime('%a %Y-%m-%d %H:%M:%S') + ' --'

    def cmd_tar(self, args):
        return 'tar: limited implementation'

    def cmd_gzip(self, args):
        return 'gzip: limited implementation'

    def cmd_gunzip(self, args):
        return 'gunzip: limited implementation'

    def cmd_zip(self, args):
        return 'zip: limited implementation'

    def cmd_unzip(self, args):
        return 'unzip: limited implementation'

    def cmd_wget(self, args):
        if not args:
            return 'wget: missing URL'
        return f'--{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--  {args[0]}\nResolving host... connected.\nHTTP request sent, awaiting response... 200 OK\nLength: unspecified [text/html]\nSaving to: 'index.html'\nindex.html saved'

    def cmd_curl(self, args):
        if not args:
            return 'curl: missing URL'
        return 'curl: limited implementation'

    def cmd_ssh(self, args):
        return 'ssh: limited implementation'

    def cmd_scp(self, args):
        return 'scp: limited implementation'

    def cmd_chmod(self, args):
        if len(args) < 2:
            return 'chmod: missing operand'
        
        mode = args[0]
        filepath = args[1]
        
        info = self.fs.get_node_info(filepath)
        if not info:
            return f'chmod: cannot access \'{filepath}\': No such file or directory'
        
        return ''

    def cmd_chown(self, args):
        if len(args) < 2:
            return 'chown: missing operand'
        return ''

    def cmd_chgrp(self, args):
        if len(args) < 2:
            return 'chgrp: missing operand'
        return ''

    def cmd_stat(self, args):
        if not args:
            return 'stat: missing operand'
        
        info = self.fs.get_node_info(args[0])
        if not info:
            return f'stat: cannot stat \'{args[0]}\': No such file or directory'
        
        file_type = 'directory' if info['is_dir'] else 'regular file'
        
        result = [
            f'  File: {info["name"]}',
            f'  Size: {info["size"]}\t\tBlocks: {info["size"]//512 + 1}\tIO Block: 4096   {file_type}',
            f'Device: 8,1\tInode: {info["inode"]}\tLinks: {info["links"]}',
            f'Access: ({info["permissions"]})  Uid: (    0/{info["owner"]})\tGid: (    0/{info["group"]})',
            f'Access: {datetime.fromtimestamp(info["accessed"]).strftime("%Y-%m-%d %H:%M:%S")}',
            f'Modify: {datetime.fromtimestamp(info["modified"]).strftime("%Y-%m-%d %H:%M:%S")}',
            f'Change: {datetime.fromtimestamp(info["modified"]).strftime("%Y-%m-%d %H:%M:%S")}',
        ]
        
        return '\n'.join(result)

    def cmd_file(self, args):
        if not args:
            return 'file: missing operand'
        
        info = self.fs.get_node_info(args[0])
        if not info:
            return f'{args[0]}: cannot open (No such file or directory)'
        
        if info['is_dir']:
            return f'{args[0]}: directory'
        
        return f'{args[0]}: ASCII text'

    def cmd_head(self, args):
        if not args:
            return 'head: missing operand'
        
        content = self.fs.read_file(args[0])
        if content is None:
            return f'head: cannot open \'{args[0]}\': No such file or directory'
        
        lines = content.decode('utf-8', errors='ignore').split('\n')
        return '\n'.join(lines[:10])

    def cmd_tail(self, args):
        if not args:
            return 'tail: missing operand'
        
        content = self.fs.read_file(args[0])
        if content is None:
            return f'tail: cannot open \'{args[0]}\': No such file or directory'
        
        lines = content.decode('utf-8', errors='ignore').split('\n')
        return '\n'.join(lines[-10:])

    def cmd_less(self, args):
        if not args:
            return 'less: missing operand'
        return self.cmd_cat(args)

    def cmd_more(self, args):
        if not args:
            return 'more: missing operand'
        return self.cmd_cat(args)

    def cmd_wc(self, args):
        if not args:
            return 'wc: missing operand'
        
        content = self.fs.read_file(args[0])
        if content is None:
            return f'wc: {args[0]}: No such file or directory'
        
        text = content.decode('utf-8', errors='ignore')
        lines = len(text.split('\n'))
        words = len(text.split())
        chars = len(text)
        
        return f'{lines:7d} {words:7d} {chars:7d} {args[0]}'

    def cmd_sort(self, args):
        return 'sort: limited implementation'

    def cmd_uniq(self, args):
        return 'uniq: limited implementation'

    def cmd_diff(self, args):
        return 'diff: limited implementation'

    def cmd_ln(self, args):
        return 'ln: limited implementation'

    def cmd_readlink(self, args):
        return 'readlink: limited implementation'
