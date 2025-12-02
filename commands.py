import time
import os
import re
import psutil
import socket
import hashlib
import base64
import random
import datetime
import calendar


class CommandExecutor:
    def __init__(self, system):
        self.system = system

    def execute(self, cmd, args, stdin=None):
        commands = {
            'ls': self.cmd_ls, 'cat': self.cmd_cat, 'echo': self.cmd_echo,
            'pwd': self.cmd_pwd, 'cd': self.cmd_cd, 'mkdir': self.cmd_mkdir,
            'rmdir': self.cmd_rmdir, 'rm': self.cmd_rm, 'cp': self.cmd_cp,
            'mv': self.cmd_mv, 'touch': self.cmd_touch, 'chmod': self.cmd_chmod,
            'chown': self.cmd_chown, 'head': self.cmd_head, 'tail': self.cmd_tail,
            'wc': self.cmd_wc, 'grep': self.cmd_grep, 'find': self.cmd_find,
            'sort': self.cmd_sort, 'uniq': self.cmd_uniq, 'cut': self.cmd_cut,
            'tr': self.cmd_tr, 'sed': self.cmd_sed, 'ps': self.cmd_ps,
            'top': self.cmd_top, 'kill': self.cmd_kill, 'killall': self.cmd_killall,
            'df': self.cmd_df, 'du': self.cmd_du, 'free': self.cmd_free,
            'uptime': self.cmd_uptime, 'uname': self.cmd_uname,
            'hostname': self.cmd_hostname, 'date': self.cmd_date, 'cal': self.cmd_cal,
            'whoami': self.cmd_whoami, 'id': self.cmd_id, 'who': self.cmd_who,
            'w': self.cmd_w, 'ifconfig': self.cmd_ifconfig, 'ip': self.cmd_ip,
            'ping': self.cmd_ping, 'netstat': self.cmd_netstat,
            'env': self.cmd_env, 'export': self.cmd_export, 'printenv': self.cmd_env,
            'alias': self.cmd_alias, 'unalias': self.cmd_unalias,
            'history': self.cmd_history, 'clear': self.cmd_clear,
            'dmesg': self.cmd_dmesg, 'lsmod': self.cmd_lsmod,
            'systemctl': self.cmd_systemctl, 'service': self.cmd_service,
            'apt': self.cmd_apt, 'apt-get': self.cmd_apt, 'dpkg': self.cmd_dpkg,
            'man': self.cmd_man, 'help': self.cmd_help, 'which': self.cmd_which,
            'whereis': self.cmd_whereis, 'type': self.cmd_type,
            'file': self.cmd_file, 'stat': self.cmd_stat,
            'su': self.cmd_su, 'sudo': self.cmd_sudo, 'passwd': self.cmd_passwd,
            'useradd': self.cmd_useradd, 'userdel': self.cmd_userdel,
            'groupadd': self.cmd_groupadd, 'mount': self.cmd_mount,
            'umount': self.cmd_umount, 'ln': self.cmd_ln,
            'basename': self.cmd_basename, 'dirname': self.cmd_dirname,
            'md5sum': self.cmd_md5sum, 'sha256sum': self.cmd_sha256sum,
            'base64': self.cmd_base64, 'tee': self.cmd_tee,
            'xargs': self.cmd_xargs, 'yes': self.cmd_yes,
            'true': self.cmd_true, 'false': self.cmd_false,
            'test': self.cmd_test, '[': self.cmd_test,
            'expr': self.cmd_expr, 'seq': self.cmd_seq,
            'sleep': self.cmd_sleep, 'exit': self.cmd_exit,
            'logout': self.cmd_exit, 'source': self.cmd_source,
            'set': self.cmd_set, 'unset': self.cmd_unset,
            'lscpu': self.cmd_lscpu, 'lsblk': self.cmd_lsblk,
            'blkid': self.cmd_blkid, 'curl': self.cmd_curl, 'wget': self.cmd_wget,
            'nslookup': self.cmd_nslookup, 'dig': self.cmd_dig,
            'tac': self.cmd_tac, 'rev': self.cmd_rev, 'nl': self.cmd_nl,
            'reboot': lambda a, s: 'reboot\n',
            'shutdown': lambda a, s: 'shutdown\n',
            'poweroff': lambda a, s: 'poweroff\n',
            'halt': lambda a, s: 'halt\n',
        }
        
        if cmd in commands:
            try:
                return commands[cmd](args, stdin)
            except Exception as e:
                return f"-bash: {cmd}: {str(e)}\n"
        
        if self.system.filesystem.exists(f'/bin/{cmd}') or self.system.filesystem.exists(f'/usr/bin/{cmd}'):
            return f"{cmd}: command executed\n"
        return f"-bash: {cmd}: command not found\n"

    def cmd_ls(self, args, stdin):
        show_all = '-a' in args or '-la' in args or '-al' in args
        long_fmt = '-l' in args or '-la' in args or '-al' in args
        human = '-h' in args
        paths = [a for a in args if not a.startswith('-')] or ['.']
        output = []
        
        for path in paths:
            resolved = self.system.filesystem.resolve_path(path)
            if not self.system.filesystem.exists(resolved):
                output.append(f"ls: cannot access '{path}': No such file or directory")
                continue
            
            if self.system.filesystem.is_file(resolved):
                info = self.system.filesystem.get_file_info(resolved)
                if long_fmt:
                    output.append(self._format_ls_long(info, human))
                else:
                    output.append(info['name'])
                continue
            
            files = self.system.filesystem.list_dir(resolved) or []
            if not show_all:
                files = [f for f in files if not f.startswith('.')]
            
            if len(paths) > 1:
                output.append(f"{path}:")
            
            if long_fmt:
                output.append(f"total {len(files) * 4}")
                for f in sorted(files):
                    fp = f"{resolved}/{f}" if resolved != '/' else f"/{f}"
                    info = self.system.filesystem.get_file_info(fp)
                    if info:
                        output.append(self._format_ls_long(info, human))
            else:
                output.append('  '.join(sorted(files)))
        
        return '\n'.join(output) + '\n' if output else ''

    def _format_ls_long(self, info, human=False):
        mode = 'd' if info['is_dir'] else '-'
        for i in range(3):
            shift = 6 - i * 3
            mode += 'r' if info['permissions'] & (4 << shift) else '-'
            mode += 'w' if info['permissions'] & (2 << shift) else '-'
            mode += 'x' if info['permissions'] & (1 << shift) else '-'
        
        size = info['size']
        if human:
            if size >= 1024**2:
                size_str = f"{size/1024**2:.1f}M"
            elif size >= 1024:
                size_str = f"{size/1024:.1f}K"
            else:
                size_str = str(size)
        else:
            size_str = str(size)
        
        mtime = time.strftime('%b %d %H:%M', time.localtime(info['modified']))
        return f"{mode} {info['links']:>3} {info['owner']:<8} {info['group']:<8} {size_str:>8} {mtime} {info['name']}"

    def cmd_cat(self, args, stdin):
        if stdin and not args:
            return stdin
        show_line_numbers = '-n' in args
        output = []
        line_num = 1
        
        for f in [a for a in args if not a.startswith('-')]:
            content = self.system.filesystem.read_file(f)
            if content is None:
                output.append(f"cat: {f}: No such file or directory")
            else:
                if show_line_numbers:
                    for line in content.split('\n'):
                        output.append(f"{line_num:>6}\t{line}")
                        line_num += 1
                else:
                    output.append(content)
        
        return '\n'.join(output) if output else ''

    def cmd_tac(self, args, stdin):
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        lines = content.strip().split('\n')
        return '\n'.join(reversed(lines)) + '\n'

    def cmd_echo(self, args, stdin):
        newline = True
        interpret = False
        out_args = []
        for a in args:
            if a == '-n':
                newline = False
            elif a == '-e':
                interpret = True
            else:
                out_args.append(a)
        result = ' '.join(out_args)
        if interpret:
            result = result.replace('\\n', '\n').replace('\\t', '\t').replace('\\\\', '\\')
        return result + ('\n' if newline else '')

    def cmd_pwd(self, args, stdin):
        return self.system.filesystem.cwd + '\n'

    def cmd_cd(self, args, stdin):
        target = args[0] if args else self.system.environment.get('HOME', '/root')
        if target == '-':
            target = self.system.environment.get('OLDPWD', self.system.filesystem.cwd)
        resolved = self.system.filesystem.resolve_path(target)
        if not self.system.filesystem.exists(resolved):
            return f"-bash: cd: {target}: No such file or directory\n"
        if not self.system.filesystem.is_dir(resolved):
            return f"-bash: cd: {target}: Not a directory\n"
        self.system.environment['OLDPWD'] = self.system.filesystem.cwd
        self.system.filesystem.cwd = resolved
        self.system.environment['PWD'] = resolved
        return ''

    def cmd_mkdir(self, args, stdin):
        parents = '-p' in args
        verbose = '-v' in args
        dirs = [a for a in args if not a.startswith('-')]
        output = []
        for d in dirs:
            if self.system.filesystem.mkdir(d, parents=parents):
                if verbose:
                    output.append(f"mkdir: created directory '{d}'")
            else:
                if not parents:
                    output.append(f"mkdir: cannot create directory '{d}'")
        return '\n'.join(output) + '\n' if output else ''

    def cmd_rmdir(self, args, stdin):
        output = []
        for d in [a for a in args if not a.startswith('-')]:
            resolved = self.system.filesystem.resolve_path(d)
            node = self.system.filesystem._get_node(resolved)
            if not node:
                output.append(f"rmdir: failed to remove '{d}': No such file or directory")
            elif not node.is_dir:
                output.append(f"rmdir: failed to remove '{d}': Not a directory")
            elif node.children:
                output.append(f"rmdir: failed to remove '{d}': Directory not empty")
            else:
                self.system.filesystem.delete(d)
        return '\n'.join(output) + '\n' if output else ''

    def cmd_rm(self, args, stdin):
        recursive = '-r' in args or '-R' in args or '-rf' in args or '-fr' in args
        force = '-f' in args or '-rf' in args or '-fr' in args
        verbose = '-v' in args
        files = [a for a in args if not a.startswith('-')]
        output = []
        
        for f in files:
            if not self.system.filesystem.exists(f):
                if not force:
                    output.append(f"rm: cannot remove '{f}': No such file or directory")
                continue
            if self.system.filesystem.is_dir(f) and not recursive:
                output.append(f"rm: cannot remove '{f}': Is a directory")
                continue
            if self.system.filesystem.delete(f, recursive=recursive):
                if verbose:
                    output.append(f"removed '{f}'")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_touch(self, args, stdin):
        for f in [a for a in args if not a.startswith('-')]:
            if not self.system.filesystem.exists(f):
                self.system.filesystem.write_file(f, '')
            else:
                node = self.system.filesystem._get_node(self.system.filesystem.resolve_path(f))
                if node:
                    node.modified = time.time()
        return ''

    def cmd_cp(self, args, stdin):
        recursive = '-r' in args or '-R' in args
        verbose = '-v' in args
        files = [a for a in args if not a.startswith('-')]
        if len(files) < 2:
            return "cp: missing destination\n"
        dst = files.pop()
        output = []
        for src in files:
            if not self.system.filesystem.exists(src):
                output.append(f"cp: cannot stat '{src}': No such file or directory")
                continue
            if self.system.filesystem.is_dir(src) and not recursive:
                output.append(f"cp: -r not specified; omitting directory '{src}'")
                continue
            if self.system.filesystem.copy(src, dst):
                if verbose:
                    output.append(f"'{src}' -> '{dst}'")
        return '\n'.join(output) + '\n' if output else ''

    def cmd_mv(self, args, stdin):
        verbose = '-v' in args
        files = [a for a in args if not a.startswith('-')]
        if len(files) < 2:
            return "mv: missing destination\n"
        dst = files.pop()
        output = []
        for src in files:
            if not self.system.filesystem.exists(src):
                output.append(f"mv: cannot stat '{src}': No such file or directory")
                continue
            if self.system.filesystem.move(src, dst):
                if verbose:
                    output.append(f"renamed '{src}' -> '{dst}'")
        return '\n'.join(output) + '\n' if output else ''

    def cmd_chmod(self, args, stdin):
        if len(args) < 2:
            return "chmod: missing operand\n"
        mode_str = None
        files = []
        for a in args:
            if a.startswith('-'):
                continue
            if mode_str is None and (a[0].isdigit() or a[0] in 'ugoa'):
                mode_str = a
            else:
                files.append(a)
        if not mode_str or not files:
            return "chmod: missing operand\n"
        try:
            mode = int(mode_str, 8)
        except:
            mode = 0o644
        for f in files:
            self.system.filesystem.chmod(f, mode)
        return ''

    def cmd_chown(self, args, stdin):
        if len(args) < 2:
            return "chown: missing operand\n"
        owner_group = args[0]
        files = [a for a in args[1:] if not a.startswith('-')]
        owner, group = (owner_group.split(':') + [None])[:2] if ':' in owner_group else (owner_group, None)
        for f in files:
            self.system.filesystem.chown(f, owner, group)
        return ''

    def cmd_head(self, args, stdin):
        lines = 10
        files = []
        i = 0
        while i < len(args):
            if args[i] == '-n' and i + 1 < len(args):
                lines = int(args[i + 1])
                i += 2
            elif args[i].startswith('-') and args[i][1:].isdigit():
                lines = int(args[i][1:])
                i += 1
            elif not args[i].startswith('-'):
                files.append(args[i])
                i += 1
            else:
                i += 1
        
        content = stdin if stdin and not files else ''
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        return '\n'.join(content.split('\n')[:lines]) + '\n'

    def cmd_tail(self, args, stdin):
        lines = 10
        files = []
        i = 0
        while i < len(args):
            if args[i] == '-n' and i + 1 < len(args):
                lines = int(args[i + 1])
                i += 2
            elif args[i].startswith('-') and args[i][1:].isdigit():
                lines = int(args[i][1:])
                i += 1
            elif not args[i].startswith('-'):
                files.append(args[i])
                i += 1
            else:
                i += 1
        
        content = stdin if stdin and not files else ''
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        return '\n'.join(content.strip().split('\n')[-lines:]) + '\n'

    def cmd_wc(self, args, stdin):
        show_lines = '-l' in args
        show_words = '-w' in args
        show_chars = '-c' in args or '-m' in args
        if not any([show_lines, show_words, show_chars]):
            show_lines = show_words = show_chars = True
        
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        lines = content.count('\n')
        words = len(content.split())
        chars = len(content)
        fname = files[0] if files else ''
        
        parts = []
        if show_lines:
            parts.append(f"{lines:>8}")
        if show_words:
            parts.append(f"{words:>8}")
        if show_chars:
            parts.append(f"{chars:>8}")
        return ''.join(parts) + f" {fname}\n"

    def cmd_grep(self, args, stdin):
        ignore_case = '-i' in args
        invert = '-v' in args
        count_only = '-c' in args
        line_nums = '-n' in args
        pattern = None
        files = []
        
        for a in args:
            if a.startswith('-') or a == '--color=auto':
                continue
            if pattern is None:
                pattern = a
            else:
                files.append(a)
        
        if not pattern:
            return "grep: missing pattern\n"
        
        content = stdin if stdin and not files else ''
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        flags = re.IGNORECASE if ignore_case else 0
        try:
            regex = re.compile(pattern, flags)
        except:
            return f"grep: Invalid regex\n"
        
        output = []
        count = 0
        for i, line in enumerate(content.split('\n'), 1):
            match = bool(regex.search(line)) != invert
            if match:
                count += 1
                if not count_only:
                    prefix = f"{i}:" if line_nums else ""
                    output.append(f"{prefix}{line}")
        
        if count_only:
            return f"{count}\n"
        return '\n'.join(output) + '\n' if output else ''

    def cmd_find(self, args, stdin):
        paths = []
        name_pattern = None
        type_filter = None
        i = 0
        while i < len(args):
            if args[i] == '-name' and i + 1 < len(args):
                name_pattern = args[i + 1]
                i += 2
            elif args[i] == '-type' and i + 1 < len(args):
                type_filter = args[i + 1]
                i += 2
            elif not args[i].startswith('-'):
                paths.append(args[i])
                i += 1
            else:
                i += 1
        
        if not paths:
            paths = ['.']
        
        results = []
        import fnmatch
        
        def search(path, depth=0):
            resolved = self.system.filesystem.resolve_path(path)
            info = self.system.filesystem.get_file_info(resolved)
            if not info:
                return
            
            match = True
            if name_pattern:
                if not fnmatch.fnmatch(info['name'], name_pattern):
                    match = False
            if type_filter:
                if type_filter == 'f' and info['is_dir']:
                    match = False
                if type_filter == 'd' and not info['is_dir']:
                    match = False
            
            if match:
                results.append(resolved)
            
            if info['is_dir']:
                files = self.system.filesystem.list_dir(resolved) or []
                for f in files:
                    child = f"{resolved}/{f}" if resolved != '/' else f"/{f}"
                    search(child, depth + 1)
        
        for p in paths:
            search(p)
        return '\n'.join(results) + '\n' if results else ''

    def cmd_sort(self, args, stdin):
        reverse = '-r' in args
        numeric = '-n' in args
        unique = '-u' in args
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        lines = content.strip().split('\n') if content.strip() else []
        if numeric:
            def key(x):
                try:
                    return float(x.split()[0])
                except:
                    return 0
            lines.sort(key=key, reverse=reverse)
        else:
            lines.sort(reverse=reverse)
        
        if unique:
            lines = list(dict.fromkeys(lines))
        return '\n'.join(lines) + '\n' if lines else ''

    def cmd_uniq(self, args, stdin):
        count = '-c' in args
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        lines = content.strip().split('\n') if content.strip() else []
        result = []
        prev = None
        cnt = 0
        
        for line in lines:
            if line != prev:
                if prev is not None:
                    if count:
                        result.append(f"{cnt:>7} {prev}")
                    else:
                        result.append(prev)
                prev = line
                cnt = 1
            else:
                cnt += 1
        
        if prev is not None:
            if count:
                result.append(f"{cnt:>7} {prev}")
            else:
                result.append(prev)
        
        return '\n'.join(result) + '\n' if result else ''

    def cmd_cut(self, args, stdin):
        delimiter = '\t'
        fields = None
        i = 0
        while i < len(args):
            if args[i] == '-d' and i + 1 < len(args):
                delimiter = args[i + 1]
                i += 2
            elif args[i].startswith('-d'):
                delimiter = args[i][2:]
                i += 1
            elif args[i] == '-f' and i + 1 < len(args):
                fields = args[i + 1]
                i += 2
            elif args[i].startswith('-f'):
                fields = args[i][2:]
                i += 1
            else:
                i += 1
        
        content = stdin or ''
        output = []
        for line in content.split('\n'):
            if fields:
                parts = line.split(delimiter)
                selected = []
                for f in fields.split(','):
                    try:
                        idx = int(f) - 1
                        if 0 <= idx < len(parts):
                            selected.append(parts[idx])
                    except:
                        pass
                output.append(delimiter.join(selected))
            else:
                output.append(line)
        return '\n'.join(output)

    def cmd_tr(self, args, stdin):
        if len(args) < 1:
            return "tr: missing operand\n"
        delete = '-d' in args
        non_flag = [a for a in args if not a.startswith('-')]
        if not non_flag:
            return "tr: missing operand\n"
        
        set1 = non_flag[0]
        set2 = non_flag[1] if len(non_flag) > 1 else ''
        content = stdin or ''
        
        if delete:
            for c in set1:
                content = content.replace(c, '')
        elif set2:
            trans = str.maketrans(set1, set2[:len(set1)])
            content = content.translate(trans)
        return content

    def cmd_sed(self, args, stdin):
        script = None
        files = []
        for a in args:
            if a.startswith('-'):
                continue
            if script is None:
                script = a
            else:
                files.append(a)
        
        if not script:
            return "sed: no script\n"
        
        content = stdin or ''
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        if script.startswith('s'):
            delim = script[1]
            parts = script.split(delim)
            if len(parts) >= 3:
                pattern = parts[1]
                replacement = parts[2]
                flags = parts[3] if len(parts) > 3 else ''
                count = 0 if 'g' in flags else 1
                try:
                    content = re.sub(pattern, replacement, content, count=count)
                except:
                    pass
        return content

    def cmd_ps(self, args, stdin):
        aux = 'aux' in ''.join(args) or '-ef' in args
        return self.system.process_manager.format_ps_output(aux=aux) + '\n'

    def cmd_top(self, args, stdin):
        return self.system.process_manager.format_top_output() + '\n'

    def cmd_kill(self, args, stdin):
        signal = 15
        pids = []
        for a in args:
            if a == '-l':
                return "1) SIGHUP  2) SIGINT  9) SIGKILL  15) SIGTERM  19) SIGSTOP\n"
            elif a.startswith('-'):
                try:
                    signal = int(a[1:])
                except:
                    if a[1:].upper() == 'KILL':
                        signal = 9
                    elif a[1:].upper() == 'TERM':
                        signal = 15
            else:
                try:
                    pids.append(int(a))
                except:
                    pass
        
        output = []
        for pid in pids:
            success, msg = self.system.process_manager.kill_process(pid, signal)
            if not success:
                output.append(f"kill: ({pid}) - {msg}")
        return '\n'.join(output) + '\n' if output else ''

    def cmd_killall(self, args, stdin):
        signal = 15
        names = []
        for a in args:
            if a.startswith('-'):
                try:
                    signal = int(a[1:])
                except:
                    pass
            else:
                names.append(a)
        
        output = []
        for name in names:
            procs = self.system.process_manager.get_processes_by_name(name)
            if not procs:
                output.append(f"{name}: no process found")
            for proc in procs:
                self.system.process_manager.kill_process(proc.pid, signal)
        return '\n'.join(output) + '\n' if output else ''

    def cmd_df(self, args, stdin):
        human = '-h' in args
        disk = psutil.disk_usage('/')
        
        if human:
            def fmt(n):
                if n >= 1024**3:
                    return f"{n/1024**3:.1f}G"
                elif n >= 1024**2:
                    return f"{n/1024**2:.1f}M"
                return f"{n/1024:.1f}K"
            output = "Filesystem      Size  Used Avail Use% Mounted on\n"
            output += f"/dev/sda1       {fmt(disk.total):>4}  {fmt(disk.used):>4}  {fmt(disk.free):>4}  {disk.percent:>2.0f}% /\n"
        else:
            output = "Filesystem     1K-blocks    Used Available Use% Mounted on\n"
            output += f"/dev/sda1      {disk.total//1024:>10} {disk.used//1024:>7} {disk.free//1024:>9} {disk.percent:>2.0f}% /\n"
        return output

    def cmd_du(self, args, stdin):
        human = '-h' in args
        summary = '-s' in args
        paths = [a for a in args if not a.startswith('-')] or ['.']
        
        output = []
        for path in paths:
            resolved = self.system.filesystem.resolve_path(path)
            size = self._calc_size(resolved)
            if human:
                if size >= 1024**2:
                    size_str = f"{size/1024**2:.1f}M"
                elif size >= 1024:
                    size_str = f"{size/1024:.1f}K"
                else:
                    size_str = str(size)
            else:
                size_str = str(size // 1024)
            output.append(f"{size_str}\t{path}")
        return '\n'.join(output) + '\n' if output else ''

    def _calc_size(self, path):
        node = self.system.filesystem._get_node(path)
        if not node:
            return 0
        if not node.is_dir:
            return node.size
        total = 4096
        if node.children:
            for name in node.children:
                child_path = f"{path}/{name}" if path != '/' else f"/{name}"
                total += self._calc_size(child_path)
        return total

    def cmd_free(self, args, stdin):
        human = '-h' in args
        return self.system.memory_manager.format_free_output(human) + '\n'

    def cmd_uptime(self, args, stdin):
        uptime_secs = self.system.get_uptime()
        hours = int(uptime_secs // 3600)
        minutes = int((uptime_secs % 3600) // 60)
        try:
            load = psutil.getloadavg()
            load_str = f"{load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}"
        except:
            load_str = "0.00, 0.00, 0.00"
        return f" {time.strftime('%H:%M:%S')} up {hours}:{minutes:02d},  1 user,  load average: {load_str}\n"

    def cmd_uname(self, args, stdin):
        if not args:
            return "Linux\n"
        options = ''.join(args).replace('-', '')
        return self.system.kernel.get_uname(options) + '\n'

    def cmd_hostname(self, args, stdin):
        if args and not args[0].startswith('-'):
            self.system.hostname = args[0]
            self.system.environment['HOSTNAME'] = args[0]
            return ''
        return f"{self.system.hostname}\n"

    def cmd_date(self, args, stdin):
        if not args:
            return time.strftime('%a %b %d %H:%M:%S %Z %Y') + '\n'
        for arg in args:
            if arg.startswith('+'):
                fmt = arg[1:]
                return time.strftime(fmt.replace('%', '%%').replace('%%Y', '%Y').replace('%%m', '%m').replace('%%d', '%d').replace('%%H', '%H').replace('%%M', '%M').replace('%%S', '%S')) + '\n'
        return time.strftime('%a %b %d %H:%M:%S %Z %Y') + '\n'

    def cmd_cal(self, args, stdin):
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        for arg in args:
            if arg == '-y':
                return calendar.calendar(year)
            elif arg.isdigit():
                if int(arg) > 12:
                    year = int(arg)
                else:
                    month = int(arg)
        return calendar.month(year, month)

    def cmd_whoami(self, args, stdin):
        return f"{self.system.current_user or 'root'}\n"

    def cmd_id(self, args, stdin):
        user = args[0] if args and not args[0].startswith('-') else (self.system.current_user or 'root')
        if user == 'root':
            return "uid=0(root) gid=0(root) groups=0(root)\n"
        return f"uid=1000({user}) gid=1000({user}) groups=1000({user}),27(sudo)\n"

    def cmd_who(self, args, stdin):
        return f"root     tty1         {time.strftime('%Y-%m-%d %H:%M')}\n"

    def cmd_w(self, args, stdin):
        uptime_secs = self.system.get_uptime()
        hours = int(uptime_secs // 3600)
        minutes = int((uptime_secs % 3600) // 60)
        try:
            load = psutil.getloadavg()
            load_str = f"{load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}"
        except:
            load_str = "0.00, 0.00, 0.00"
        output = f" {time.strftime('%H:%M:%S')} up {hours}:{minutes:02d},  1 user,  load average: {load_str}\n"
        output += "USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT\n"
        output += f"root     tty1     -                {time.strftime('%H:%M')}    0.00s  0.01s  0.00s -bash\n"
        return output

    def cmd_ifconfig(self, args, stdin):
        return self.system.network_manager.ifconfig(args)

    def cmd_ip(self, args, stdin):
        return self.system.network_manager.ip_command(args)

    def cmd_ping(self, args, stdin):
        count = 4
        host = None
        i = 0
        while i < len(args):
            if args[i] == '-c' and i + 1 < len(args):
                count = int(args[i + 1])
                i += 2
            elif not args[i].startswith('-'):
                host = args[i]
                i += 1
            else:
                i += 1
        if not host:
            return "ping: missing host\n"
        return self.system.network_manager.ping(host, count)

    def cmd_netstat(self, args, stdin):
        return self.system.network_manager.netstat(args)

    def cmd_env(self, args, stdin):
        output = []
        for key, value in sorted(self.system.environment.items()):
            output.append(f"{key}={value}")
        return '\n'.join(output) + '\n'

    def cmd_export(self, args, stdin):
        if not args:
            output = []
            for key, value in sorted(self.system.environment.items()):
                output.append(f"declare -x {key}=\"{value}\"")
            return '\n'.join(output) + '\n'
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                self.system.environment[key] = value
            else:
                if arg not in self.system.environment:
                    self.system.environment[arg] = ''
        return ''

    def cmd_set(self, args, stdin):
        if not args:
            return self.cmd_env(args, stdin)
        return ''

    def cmd_unset(self, args, stdin):
        for arg in args:
            if arg in self.system.environment:
                del self.system.environment[arg]
        return ''

    def cmd_alias(self, args, stdin):
        if not args:
            output = []
            for name, value in sorted(self.system.aliases.items()):
                output.append(f"alias {name}='{value}'")
            return '\n'.join(output) + '\n'
        for arg in args:
            if '=' in arg:
                name, value = arg.split('=', 1)
                self.system.aliases[name] = value.strip("'\"")
            else:
                if arg in self.system.aliases:
                    return f"alias {arg}='{self.system.aliases[arg]}'\n"
        return ''

    def cmd_unalias(self, args, stdin):
        for arg in args:
            if arg == '-a':
                self.system.aliases.clear()
            elif arg in self.system.aliases:
                del self.system.aliases[arg]
        return ''

    def cmd_history(self, args, stdin):
        output = []
        for i, cmd in enumerate(self.system.history, 1):
            output.append(f"  {i:>4}  {cmd}")
        return '\n'.join(output) + '\n' if output else ''

    def cmd_clear(self, args, stdin):
        return '\033[2J\033[H'

    def cmd_dmesg(self, args, stdin):
        return self.system.kernel.get_dmesg() + '\n'

    def cmd_lsmod(self, args, stdin):
        output = "Module                  Size  Used by\n"
        for mod in self.system.kernel.modules:
            size = random.randint(10000, 500000)
            output += f"{mod:<24}{size:>6}  0\n"
        return output

    def cmd_systemctl(self, args, stdin):
        return self.system.systemd.systemctl(args)

    def cmd_service(self, args, stdin):
        if len(args) < 2:
            return "Usage: service <service> <action>\n"
        return self.system.systemd.systemctl([args[1], args[0]])

    def cmd_apt(self, args, stdin):
        return self.system.package_manager.apt(args)

    def cmd_dpkg(self, args, stdin):
        return self.system.package_manager.dpkg(args)

    def cmd_man(self, args, stdin):
        if not args:
            return "What manual page do you want?\n"
        cmd = args[0]
        return f"{cmd.upper()}(1)\n\nNAME\n       {cmd} - {cmd} command\n\nSYNOPSIS\n       {cmd} [OPTIONS]...\n\nDESCRIPTION\n       Manual page for {cmd}.\n"

    def cmd_help(self, args, stdin):
        if not args:
            return "GNU bash, version 5.1.0\n\nShell commands: alias, bg, cd, echo, exit, export, fg, help, history, jobs, kill, pwd, set, type, unalias, unset\n"
        return f"-bash: help: no help topics match '{args[0]}'\n"

    def cmd_which(self, args, stdin):
        output = []
        paths = self.system.environment.get('PATH', '').split(':')
        for cmd in [a for a in args if not a.startswith('-')]:
            found = False
            for path in paths:
                full_path = f"{path}/{cmd}"
                if self.system.filesystem.exists(full_path):
                    output.append(full_path)
                    found = True
                    break
            if not found:
                output.append(f"{cmd} not found")
        return '\n'.join(output) + '\n' if output else ''

    def cmd_whereis(self, args, stdin):
        output = []
        for cmd in [a for a in args if not a.startswith('-')]:
            locs = []
            for prefix in ['/bin', '/sbin', '/usr/bin', '/usr/sbin']:
                path = f"{prefix}/{cmd}"
                if self.system.filesystem.exists(path):
                    locs.append(path)
            output.append(f"{cmd}: {' '.join(locs)}")
        return '\n'.join(output) + '\n' if output else ''

    def cmd_type(self, args, stdin):
        builtins = ['cd', 'pwd', 'echo', 'export', 'alias', 'history', 'exit', 'source', 'set', 'unset', 'type']
        output = []
        for cmd in [a for a in args if not a.startswith('-')]:
            if cmd in builtins:
                output.append(f"{cmd} is a shell builtin")
            elif cmd in self.system.aliases:
                output.append(f"{cmd} is aliased to '{self.system.aliases[cmd]}'")
            else:
                for path in self.system.environment.get('PATH', '').split(':'):
                    full_path = f"{path}/{cmd}"
                    if self.system.filesystem.exists(full_path):
                        output.append(f"{cmd} is {full_path}")
                        break
                else:
                    output.append(f"-bash: type: {cmd}: not found")
        return '\n'.join(output) + '\n' if output else ''

    def cmd_file(self, args, stdin):
        output = []
        for f in [a for a in args if not a.startswith('-')]:
            if not self.system.filesystem.exists(f):
                output.append(f"{f}: cannot open (No such file)")
                continue
            info = self.system.filesystem.get_file_info(self.system.filesystem.resolve_path(f))
            if info['is_dir']:
                output.append(f"{f}: directory")
            else:
                content = self.system.filesystem.read_file(f) or ''
                if content.startswith('#!/'):
                    output.append(f"{f}: script, ASCII text executable")
                else:
                    output.append(f"{f}: ASCII text")
        return '\n'.join(output) + '\n' if output else ''

    def cmd_stat(self, args, stdin):
        output = []
        for f in [a for a in args if not a.startswith('-')]:
            info = self.system.filesystem.get_file_info(self.system.filesystem.resolve_path(f))
            if not info:
                output.append(f"stat: cannot stat '{f}': No such file")
                continue
            ftype = 'directory' if info['is_dir'] else 'regular file'
            mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info['modified']))
            output.append(f"  File: {f}")
            output.append(f"  Size: {info['size']}\tBlocks: {info['size']//512}\tIO Block: 4096\t{ftype}")
            output.append(f"Inode: {info['inode']}\tLinks: {info['links']}")
            output.append(f"Access: ({oct(info['permissions'])[2:]})  Uid: (0/{info['owner']})  Gid: (0/{info['group']})")
            output.append(f"Modify: {mtime}")
        return '\n'.join(output) + '\n' if output else ''

    def cmd_su(self, args, stdin):
        user = 'root'
        for arg in args:
            if not arg.startswith('-'):
                user = arg
                break
        self.system.current_user = user
        self.system.environment['USER'] = user
        self.system.environment['HOME'] = '/root' if user == 'root' else f'/home/{user}'
        return ''

    def cmd_sudo(self, args, stdin):
        if not args:
            return "usage: sudo command\n"
        if args[0] == '-i':
            self.system.current_user = 'root'
            self.system.environment['USER'] = 'root'
            self.system.environment['HOME'] = '/root'
            self.system.filesystem.cwd = '/root'
            return ''
        return self.system.shell.execute(' '.join(args))

    def cmd_passwd(self, args, stdin):
        user = args[0] if args else (self.system.current_user or 'root')
        return f"passwd: password for {user} updated successfully\n"

    def cmd_useradd(self, args, stdin):
        username = None
        for a in args:
            if not a.startswith('-'):
                username = a
                break
        if not username:
            return "useradd: missing username\n"
        return self.system.user_manager.add_user(username)

    def cmd_userdel(self, args, stdin):
        username = None
        remove_home = '-r' in args
        for a in args:
            if not a.startswith('-'):
                username = a
                break
        if not username:
            return "userdel: missing username\n"
        return self.system.user_manager.del_user(username, remove_home)

    def cmd_groupadd(self, args, stdin):
        groupname = None
        for a in args:
            if not a.startswith('-'):
                groupname = a
                break
        if not groupname:
            return "groupadd: missing group name\n"
        return self.system.user_manager.add_group(groupname)

    def cmd_mount(self, args, stdin):
        if not args:
            output = ""
            for mp, info in self.system.filesystem.mounts.items():
                output += f"{info['device']} on {mp} type {info['fstype']} ({info['options']})\n"
            return output
        return "mount: operation not supported\n"

    def cmd_umount(self, args, stdin):
        return "umount: operation not supported\n"

    def cmd_ln(self, args, stdin):
        symbolic = '-s' in args
        files = [a for a in args if not a.startswith('-')]
        if len(files) < 2:
            return "ln: missing destination\n"
        return f"ln: created {'symbolic ' if symbolic else ''}link '{files[-1]}' -> '{files[0]}'\n"

    def cmd_basename(self, args, stdin):
        if not args:
            return "basename: missing operand\n"
        path = args[0]
        suffix = args[1] if len(args) > 1 else ''
        name = path.rstrip('/').split('/')[-1]
        if suffix and name.endswith(suffix):
            name = name[:-len(suffix)]
        return name + '\n'

    def cmd_dirname(self, args, stdin):
        if not args:
            return "dirname: missing operand\n"
        path = args[0].rstrip('/')
        if '/' not in path:
            return '.\n'
        return '/'.join(path.split('/')[:-1]) or '/' + '\n'

    def cmd_md5sum(self, args, stdin):
        output = []
        if stdin and not args:
            h = hashlib.md5(stdin.encode()).hexdigest()
            output.append(f"{h}  -")
        else:
            for f in [a for a in args if not a.startswith('-')]:
                content = self.system.filesystem.read_file(f)
                if content is None:
                    output.append(f"md5sum: {f}: No such file")
                else:
                    h = hashlib.md5(content.encode()).hexdigest()
                    output.append(f"{h}  {f}")
        return '\n'.join(output) + '\n' if output else ''

    def cmd_sha256sum(self, args, stdin):
        output = []
        if stdin and not args:
            h = hashlib.sha256(stdin.encode()).hexdigest()
            output.append(f"{h}  -")
        else:
            for f in [a for a in args if not a.startswith('-')]:
                content = self.system.filesystem.read_file(f)
                if content is None:
                    output.append(f"sha256sum: {f}: No such file")
                else:
                    h = hashlib.sha256(content.encode()).hexdigest()
                    output.append(f"{h}  {f}")
        return '\n'.join(output) + '\n' if output else ''

    def cmd_base64(self, args, stdin):
        decode = '-d' in args or '--decode' in args
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        try:
            if decode:
                return base64.b64decode(content.strip()).decode('utf-8') + '\n'
            else:
                return base64.b64encode(content.encode()).decode('utf-8') + '\n'
        except:
            return "base64: invalid input\n"

    def cmd_tee(self, args, stdin):
        append = '-a' in args
        files = [a for a in args if not a.startswith('-')]
        content = stdin or ''
        for f in files:
            self.system.filesystem.write_file(f, content, append=append)
        return content

    def cmd_xargs(self, args, stdin):
        if not stdin:
            return ''
        cmd = args if args else ['echo']
        items = stdin.split()
        return self.system.shell.execute(' '.join(cmd + items))

    def cmd_yes(self, args, stdin):
        text = args[0] if args else 'y'
        return '\n'.join([text] * 10) + '\n'

    def cmd_true(self, args, stdin):
        self.system.last_exit_code = 0
        return ''

    def cmd_false(self, args, stdin):
        self.system.last_exit_code = 1
        return ''

    def cmd_test(self, args, stdin):
        if not args:
            self.system.last_exit_code = 1
            return ''
        if args[-1] == ']':
            args = args[:-1]
        
        if len(args) == 1:
            self.system.last_exit_code = 0 if args[0] else 1
        elif len(args) == 2:
            op, arg = args[0], args[1]
            if op == '-z':
                self.system.last_exit_code = 0 if not arg else 1
            elif op == '-n':
                self.system.last_exit_code = 0 if arg else 1
            elif op == '-e' or op == '-a':
                self.system.last_exit_code = 0 if self.system.filesystem.exists(arg) else 1
            elif op == '-f':
                self.system.last_exit_code = 0 if self.system.filesystem.is_file(arg) else 1
            elif op == '-d':
                self.system.last_exit_code = 0 if self.system.filesystem.is_dir(arg) else 1
        elif len(args) == 3:
            left, op, right = args
            if op == '=' or op == '==':
                self.system.last_exit_code = 0 if left == right else 1
            elif op == '!=':
                self.system.last_exit_code = 0 if left != right else 1
            elif op == '-eq':
                try:
                    self.system.last_exit_code = 0 if int(left) == int(right) else 1
                except:
                    self.system.last_exit_code = 1
            elif op == '-ne':
                try:
                    self.system.last_exit_code = 0 if int(left) != int(right) else 1
                except:
                    self.system.last_exit_code = 1
            elif op == '-lt':
                try:
                    self.system.last_exit_code = 0 if int(left) < int(right) else 1
                except:
                    self.system.last_exit_code = 1
            elif op == '-gt':
                try:
                    self.system.last_exit_code = 0 if int(left) > int(right) else 1
                except:
                    self.system.last_exit_code = 1
        return ''

    def cmd_expr(self, args, stdin):
        if not args:
            return ''
        try:
            if '+' in args:
                idx = args.index('+')
                return str(int(args[idx-1]) + int(args[idx+1])) + '\n'
            elif '-' in args:
                idx = args.index('-')
                return str(int(args[idx-1]) - int(args[idx+1])) + '\n'
            elif '*' in args:
                idx = args.index('*')
                return str(int(args[idx-1]) * int(args[idx+1])) + '\n'
            elif '/' in args:
                idx = args.index('/')
                return str(int(args[idx-1]) // int(args[idx+1])) + '\n'
        except:
            pass
        return '0\n'

    def cmd_seq(self, args, stdin):
        if not args:
            return ''
        try:
            if len(args) == 1:
                return '\n'.join(map(str, range(1, int(args[0]) + 1))) + '\n'
            elif len(args) == 2:
                return '\n'.join(map(str, range(int(args[0]), int(args[1]) + 1))) + '\n'
            elif len(args) >= 3:
                return '\n'.join(map(str, range(int(args[0]), int(args[2]) + 1, int(args[1])))) + '\n'
        except:
            pass
        return ''

    def cmd_sleep(self, args, stdin):
        if not args:
            return "sleep: missing operand\n"
        try:
            duration = float(args[0].rstrip('smhd'))
            time.sleep(min(duration, 5))
        except:
            return f"sleep: invalid time '{args[0]}'\n"
        return ''

    def cmd_exit(self, args, stdin):
        code = 0
        if args:
            try:
                code = int(args[0])
            except:
                pass
        return f"exit {code}\n"

    def cmd_source(self, args, stdin):
        if not args:
            return "source: missing file\n"
        content = self.system.filesystem.read_file(args[0])
        if content is None:
            return f"-bash: {args[0]}: No such file\n"
        output = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                result = self.system.shell.execute(line)
                if result:
                    output.append(result.rstrip())
        return '\n'.join(output) + '\n' if output else ''

    def cmd_lscpu(self, args, stdin):
        freq = psutil.cpu_freq()
        return f"""Architecture:            x86_64
CPU(s):                  {psutil.cpu_count()}
Model name:              Virtual CPU
CPU MHz:                 {freq.current if freq else 2400:.3f}
"""

    def cmd_lsblk(self, args, stdin):
        disk = psutil.disk_usage('/')
        return f"""NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
sda      8:0    0   {disk.total / (1024**3):.1f}G  0 disk 
├─sda1   8:1    0   {(disk.total - 1024**3) / (1024**3):.1f}G  0 part /
└─sda2   8:2    0     1G  0 part [SWAP]
"""

    def cmd_blkid(self, args, stdin):
        return '/dev/sda1: UUID="12345678-1234-1234-1234-123456789abc" TYPE="ext4"\n'

    def cmd_curl(self, args, stdin):
        url = None
        for a in args:
            if not a.startswith('-'):
                url = a
                break
        if not url:
            return "curl: missing URL\n"
        return self.system.network_manager.curl(url)

    def cmd_wget(self, args, stdin):
        url = None
        for a in args:
            if not a.startswith('-'):
                url = a
                break
        if not url:
            return "wget: missing URL\n"
        return self.system.network_manager.wget(url)

    def cmd_nslookup(self, args, stdin):
        if not args:
            return "nslookup: missing host\n"
        return self.system.network_manager.nslookup(args[0])

    def cmd_dig(self, args, stdin):
        if not args:
            return "dig: missing host\n"
        return self.system.network_manager.dig(args[0])

    def cmd_rev(self, args, stdin):
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        lines = content.split('\n')
        return '\n'.join(line[::-1] for line in lines)

    def cmd_nl(self, args, stdin):
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        output = []
        for i, line in enumerate(content.split('\n'), 1):
            if line.strip():
                output.append(f"{i:>6}\t{line}")
            else:
                output.append(line)
        return '\n'.join(output)
