import time
import os
import re
import psutil
import socket
import hashlib
import base64
import json
import random
import struct
import datetime

class CommandExecutor:
    def __init__(self, system):
        self.system = system
        self.commands = self._register_commands()

    def _register_commands(self):
        return {
            'ls': self.cmd_ls,
            'dir': self.cmd_ls,
            'cat': self.cmd_cat,
            'tac': self.cmd_tac,
            'echo': self.cmd_echo,
            'printf': self.cmd_printf,
            'pwd': self.cmd_pwd,
            'cd': self.cmd_cd,
            'mkdir': self.cmd_mkdir,
            'rmdir': self.cmd_rmdir,
            'rm': self.cmd_rm,
            'cp': self.cmd_cp,
            'mv': self.cmd_mv,
            'touch': self.cmd_touch,
            'chmod': self.cmd_chmod,
            'chown': self.cmd_chown,
            'chgrp': self.cmd_chgrp,
            'ln': self.cmd_ln,
            'readlink': self.cmd_readlink,
            'realpath': self.cmd_realpath,
            'basename': self.cmd_basename,
            'dirname': self.cmd_dirname,
            'head': self.cmd_head,
            'tail': self.cmd_tail,
            'wc': self.cmd_wc,
            'sort': self.cmd_sort,
            'uniq': self.cmd_uniq,
            'cut': self.cmd_cut,
            'tr': self.cmd_tr,
            'grep': self.cmd_grep,
            'egrep': self.cmd_egrep,
            'fgrep': self.cmd_fgrep,
            'sed': self.cmd_sed,
            'awk': self.cmd_awk,
            'find': self.cmd_find,
            'locate': self.cmd_locate,
            'which': self.cmd_which,
            'whereis': self.cmd_whereis,
            'type': self.cmd_type,
            'file': self.cmd_file,
            'stat': self.cmd_stat,
            'diff': self.cmd_diff,
            'cmp': self.cmd_cmp,
            'comm': self.cmd_comm,
            'tar': self.cmd_tar,
            'gzip': self.cmd_gzip,
            'gunzip': self.cmd_gunzip,
            'zcat': self.cmd_zcat,
            'bzip2': self.cmd_bzip2,
            'xz': self.cmd_xz,
            'zip': self.cmd_zip,
            'unzip': self.cmd_unzip,
            'ps': self.cmd_ps,
            'top': self.cmd_top,
            'htop': self.cmd_top,
            'kill': self.cmd_kill,
            'killall': self.cmd_killall,
            'pkill': self.cmd_pkill,
            'pgrep': self.cmd_pgrep,
            'nice': self.cmd_nice,
            'renice': self.cmd_renice,
            'nohup': self.cmd_nohup,
            'jobs': self.cmd_jobs,
            'fg': self.cmd_fg,
            'bg': self.cmd_bg,
            'wait': self.cmd_wait,
            'df': self.cmd_df,
            'du': self.cmd_du,
            'free': self.cmd_free,
            'vmstat': self.cmd_vmstat,
            'iostat': self.cmd_iostat,
            'mpstat': self.cmd_mpstat,
            'uptime': self.cmd_uptime,
            'w': self.cmd_w,
            'who': self.cmd_who,
            'whoami': self.cmd_whoami,
            'id': self.cmd_id,
            'groups': self.cmd_groups,
            'users': self.cmd_users,
            'last': self.cmd_last,
            'lastlog': self.cmd_lastlog,
            'finger': self.cmd_finger,
            'hostname': self.cmd_hostname,
            'hostnamectl': self.cmd_hostnamectl,
            'uname': self.cmd_uname,
            'arch': self.cmd_arch,
            'nproc': self.cmd_nproc,
            'lscpu': self.cmd_lscpu,
            'lsmem': self.cmd_lsmem,
            'lspci': self.cmd_lspci,
            'lsusb': self.cmd_lsusb,
            'lsblk': self.cmd_lsblk,
            'blkid': self.cmd_blkid,
            'fdisk': self.cmd_fdisk,
            'mount': self.cmd_mount,
            'umount': self.cmd_umount,
            'dmesg': self.cmd_dmesg,
            'lsmod': self.cmd_lsmod,
            'modinfo': self.cmd_modinfo,
            'modprobe': self.cmd_modprobe,
            'insmod': self.cmd_insmod,
            'rmmod': self.cmd_rmmod,
            'date': self.cmd_date,
            'cal': self.cmd_cal,
            'timedatectl': self.cmd_timedatectl,
            'hwclock': self.cmd_hwclock,
            'sleep': self.cmd_sleep,
            'usleep': self.cmd_usleep,
            'time': self.cmd_time,
            'timeout': self.cmd_timeout,
            'watch': self.cmd_watch,
            'env': self.cmd_env,
            'printenv': self.cmd_printenv,
            'export': self.cmd_export,
            'set': self.cmd_set,
            'unset': self.cmd_unset,
            'alias': self.cmd_alias,
            'unalias': self.cmd_unalias,
            'source': self.cmd_source,
            '.': self.cmd_source,
            'exec': self.cmd_exec,
            'eval': self.cmd_eval,
            'history': self.cmd_history,
            'clear': self.cmd_clear,
            'reset': self.cmd_reset,
            'tput': self.cmd_tput,
            'stty': self.cmd_stty,
            'tee': self.cmd_tee,
            'xargs': self.cmd_xargs,
            'yes': self.cmd_yes,
            'true': self.cmd_true,
            'false': self.cmd_false,
            'test': self.cmd_test,
            '[': self.cmd_test,
            'expr': self.cmd_expr,
            'bc': self.cmd_bc,
            'dc': self.cmd_dc,
            'factor': self.cmd_factor,
            'seq': self.cmd_seq,
            'shuf': self.cmd_shuf,
            'rev': self.cmd_rev,
            'tac': self.cmd_tac,
            'nl': self.cmd_nl,
            'od': self.cmd_od,
            'xxd': self.cmd_xxd,
            'hexdump': self.cmd_hexdump,
            'strings': self.cmd_strings,
            'base64': self.cmd_base64,
            'md5sum': self.cmd_md5sum,
            'sha1sum': self.cmd_sha1sum,
            'sha256sum': self.cmd_sha256sum,
            'sha512sum': self.cmd_sha512sum,
            'sum': self.cmd_sum,
            'cksum': self.cmd_cksum,
            'ifconfig': self.cmd_ifconfig,
            'ip': self.cmd_ip,
            'ping': self.cmd_ping,
            'traceroute': self.cmd_traceroute,
            'tracepath': self.cmd_tracepath,
            'netstat': self.cmd_netstat,
            'ss': self.cmd_ss,
            'route': self.cmd_route,
            'arp': self.cmd_arp,
            'nslookup': self.cmd_nslookup,
            'dig': self.cmd_dig,
            'host': self.cmd_host,
            'hostname': self.cmd_hostname,
            'curl': self.cmd_curl,
            'wget': self.cmd_wget,
            'nc': self.cmd_nc,
            'netcat': self.cmd_nc,
            'telnet': self.cmd_telnet,
            'ftp': self.cmd_ftp,
            'ssh': self.cmd_ssh,
            'scp': self.cmd_scp,
            'sftp': self.cmd_sftp,
            'rsync': self.cmd_rsync,
            'useradd': self.cmd_useradd,
            'userdel': self.cmd_userdel,
            'usermod': self.cmd_usermod,
            'groupadd': self.cmd_groupadd,
            'groupdel': self.cmd_groupdel,
            'groupmod': self.cmd_groupmod,
            'passwd': self.cmd_passwd,
            'chpasswd': self.cmd_chpasswd,
            'su': self.cmd_su,
            'sudo': self.cmd_sudo,
            'visudo': self.cmd_visudo,
            'newgrp': self.cmd_newgrp,
            'login': self.cmd_login,
            'logout': self.cmd_logout,
            'exit': self.cmd_exit,
            'systemctl': self.cmd_systemctl,
            'service': self.cmd_service,
            'journalctl': self.cmd_journalctl,
            'init': self.cmd_init,
            'telinit': self.cmd_telinit,
            'runlevel': self.cmd_runlevel,
            'shutdown': self.cmd_shutdown,
            'reboot': self.cmd_reboot,
            'poweroff': self.cmd_poweroff,
            'halt': self.cmd_halt,
            'apt': self.cmd_apt,
            'apt-get': self.cmd_apt_get,
            'apt-cache': self.cmd_apt_cache,
            'dpkg': self.cmd_dpkg,
            'man': self.cmd_man,
            'info': self.cmd_info,
            'help': self.cmd_help,
            'whatis': self.cmd_whatis,
            'apropos': self.cmd_apropos,
            'less': self.cmd_less,
            'more': self.cmd_more,
            'nano': self.cmd_nano,
            'vi': self.cmd_vi,
            'vim': self.cmd_vim,
            'view': self.cmd_view,
            'ed': self.cmd_ed,
            'crontab': self.cmd_crontab,
            'at': self.cmd_at,
            'batch': self.cmd_batch,
            'iptables': self.cmd_iptables,
            'ip6tables': self.cmd_ip6tables,
            'ufw': self.cmd_ufw,
            'dd': self.cmd_dd,
            'sync': self.cmd_sync,
            'mktemp': self.cmd_mktemp,
            'mkfifo': self.cmd_mkfifo,
            'mknod': self.cmd_mknod,
            'split': self.cmd_split,
            'csplit': self.cmd_csplit,
            'join': self.cmd_join,
            'paste': self.cmd_paste,
            'expand': self.cmd_expand,
            'unexpand': self.cmd_unexpand,
            'fold': self.cmd_fold,
            'fmt': self.cmd_fmt,
            'pr': self.cmd_pr,
            'column': self.cmd_column,
            'colrm': self.cmd_colrm,
            'logger': self.cmd_logger,
            'lsof': self.cmd_lsof,
            'fuser': self.cmd_fuser,
            'pstree': self.cmd_pstree,
            'chroot': self.cmd_chroot,
            'nologin': self.cmd_nologin,
            'getent': self.cmd_getent,
            'locale': self.cmd_locale,
            'iconv': self.cmd_iconv,
            'uuid': self.cmd_uuid,
            'uuidgen': self.cmd_uuidgen,
        }

    def execute(self, cmd, args, stdin=None):
        if cmd in self.commands:
            try:
                return self.commands[cmd](args, stdin)
            except Exception as e:
                return f"-bash: {cmd}: {str(e)}\n"
        else:
            if self.system.filesystem.exists(f'/bin/{cmd}') or self.system.filesystem.exists(f'/usr/bin/{cmd}'):
                return f"{cmd}: command executed (simulated binary)\n"
            return f"-bash: {cmd}: command not found\n"

    def cmd_ls(self, args, stdin=None):
        show_all = False
        long_format = False
        human_readable = False
        show_inode = False
        recursive = False
        reverse = False
        sort_time = False
        sort_size = False
        one_per_line = False
        classify = False
        paths = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg.startswith('-') and len(arg) > 1 and not arg.startswith('--'):
                for c in arg[1:]:
                    if c == 'a':
                        show_all = True
                    elif c == 'l':
                        long_format = True
                    elif c == 'h':
                        human_readable = True
                    elif c == 'i':
                        show_inode = True
                    elif c == 'R':
                        recursive = True
                    elif c == 'r':
                        reverse = True
                    elif c == 't':
                        sort_time = True
                    elif c == 'S':
                        sort_size = True
                    elif c == '1':
                        one_per_line = True
                    elif c == 'F':
                        classify = True
                    elif c == 'A':
                        show_all = True
            elif arg == '--all':
                show_all = True
            elif arg == '--color=auto' or arg == '--color':
                pass
            else:
                paths.append(arg)
            i += 1
        
        if not paths:
            paths = ['.']
        
        output = []
        
        for path in paths:
            resolved = self.system.filesystem.resolve_path(path)
            
            if not self.system.filesystem.exists(resolved):
                output.append(f"ls: cannot access '{path}': No such file or directory")
                continue
            
            if self.system.filesystem.is_file(resolved):
                info = self.system.filesystem.get_file_info(resolved)
                if long_format:
                    output.append(self._format_ls_long(info, human_readable, show_inode))
                else:
                    output.append(info['name'])
                continue
            
            files = self.system.filesystem.list_dir(resolved)
            if files is None:
                output.append(f"ls: cannot open directory '{path}': Permission denied")
                continue
            
            if not show_all:
                files = [f for f in files if not f.startswith('.')]
            
            if len(paths) > 1:
                output.append(f"{path}:")
            
            entries = []
            for f in files:
                full_path = f"{resolved}/{f}" if resolved != '/' else f"/{f}"
                info = self.system.filesystem.get_file_info(full_path)
                if info:
                    entries.append(info)
            
            if sort_time:
                entries.sort(key=lambda x: x['modified'], reverse=not reverse)
            elif sort_size:
                entries.sort(key=lambda x: x['size'], reverse=not reverse)
            else:
                entries.sort(key=lambda x: x['name'].lower(), reverse=reverse)
            
            if long_format:
                total = sum(e['size'] for e in entries) // 1024
                output.append(f"total {total}")
                for entry in entries:
                    line = self._format_ls_long(entry, human_readable, show_inode)
                    if classify and entry['is_dir']:
                        line += '/'
                    output.append(line)
            elif one_per_line:
                for entry in entries:
                    name = entry['name']
                    if classify:
                        if entry['is_dir']:
                            name += '/'
                        elif entry['permissions'] & 0o111:
                            name += '*'
                    output.append(name)
            else:
                names = []
                for entry in entries:
                    name = entry['name']
                    if classify:
                        if entry['is_dir']:
                            name += '/'
                        elif entry['permissions'] & 0o111:
                            name += '*'
                    names.append(name)
                output.append('  '.join(names))
        
        return '\n'.join(output) + '\n' if output else ''

    def _format_ls_long(self, info, human_readable=False, show_inode=False):
        mode = self._format_mode(info['permissions'], info['is_dir'])
        size = info['size']
        
        if human_readable:
            if size >= 1024**3:
                size_str = f"{size/1024**3:.1f}G"
            elif size >= 1024**2:
                size_str = f"{size/1024**2:.1f}M"
            elif size >= 1024:
                size_str = f"{size/1024:.1f}K"
            else:
                size_str = str(size)
        else:
            size_str = str(size)
        
        mtime = time.strftime('%b %d %H:%M', time.localtime(info['modified']))
        
        inode_str = f"{info['inode']:>8} " if show_inode else ""
        
        return f"{inode_str}{mode} {info['links']:>3} {info['owner']:<8} {info['group']:<8} {size_str:>8} {mtime} {info['name']}"

    def _format_mode(self, permissions, is_dir):
        result = 'd' if is_dir else '-'
        
        for i in range(3):
            shift = 6 - i * 3
            result += 'r' if permissions & (4 << shift) else '-'
            result += 'w' if permissions & (2 << shift) else '-'
            result += 'x' if permissions & (1 << shift) else '-'
        
        return result

    def cmd_cat(self, args, stdin=None):
        if stdin and not args:
            return stdin
        
        show_line_numbers = False
        show_ends = False
        show_tabs = False
        squeeze_blank = False
        files = []
        
        for arg in args:
            if arg == '-n' or arg == '--number':
                show_line_numbers = True
            elif arg == '-E' or arg == '--show-ends':
                show_ends = True
            elif arg == '-T' or arg == '--show-tabs':
                show_tabs = True
            elif arg == '-s' or arg == '--squeeze-blank':
                squeeze_blank = True
            elif arg == '-A' or arg == '--show-all':
                show_ends = True
                show_tabs = True
            elif arg == '-':
                if stdin:
                    files.append(('stdin', stdin))
            elif not arg.startswith('-'):
                files.append(('file', arg))
        
        if not files:
            if stdin:
                files.append(('stdin', stdin))
            else:
                return ''
        
        output = []
        line_num = 1
        prev_blank = False
        
        for file_type, file_arg in files:
            if file_type == 'stdin':
                content = file_arg
            else:
                content = self.system.filesystem.read_file(file_arg)
                if content is None:
                    output.append(f"cat: {file_arg}: No such file or directory")
                    continue
            
            lines = content.split('\n')
            for line in lines:
                is_blank = not line.strip()
                
                if squeeze_blank and is_blank and prev_blank:
                    continue
                
                if show_tabs:
                    line = line.replace('\t', '^I')
                
                if show_ends:
                    line = line + '$'
                
                if show_line_numbers:
                    output.append(f"{line_num:>6}\t{line}")
                    line_num += 1
                else:
                    output.append(line)
                
                prev_blank = is_blank
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_tac(self, args, stdin=None):
        content = stdin if stdin else ''
        
        for arg in args:
            if not arg.startswith('-'):
                file_content = self.system.filesystem.read_file(arg)
                if file_content is None:
                    return f"tac: {arg}: No such file or directory\n"
                content += file_content
        
        lines = content.strip().split('\n')
        return '\n'.join(reversed(lines)) + '\n'

    def cmd_echo(self, args, stdin=None):
        newline = True
        interpret_escapes = False
        output_args = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-n':
                newline = False
            elif arg == '-e':
                interpret_escapes = True
            elif arg == '-E':
                interpret_escapes = False
            else:
                output_args.append(arg)
            i += 1
        
        result = ' '.join(output_args)
        
        if interpret_escapes:
            result = result.replace('\\n', '\n')
            result = result.replace('\\t', '\t')
            result = result.replace('\\r', '\r')
            result = result.replace('\\\\', '\\')
            result = result.replace('\\a', '\a')
            result = result.replace('\\b', '\b')
            result = result.replace('\\f', '\f')
            result = result.replace('\\v', '\v')
        
        if newline:
            result += '\n'
        
        return result

    def cmd_printf(self, args, stdin=None):
        if not args:
            return ''
        
        format_str = args[0]
        format_args = args[1:]
        
        result = format_str
        result = result.replace('\\n', '\n')
        result = result.replace('\\t', '\t')
        result = result.replace('\\r', '\r')
        result = result.replace('%%', '%')
        
        arg_idx = 0
        output = ''
        i = 0
        while i < len(result):
            if result[i] == '%' and i + 1 < len(result):
                spec = result[i + 1]
                if spec == 's' and arg_idx < len(format_args):
                    output += format_args[arg_idx]
                    arg_idx += 1
                    i += 2
                    continue
                elif spec == 'd' and arg_idx < len(format_args):
                    try:
                        output += str(int(format_args[arg_idx]))
                    except:
                        output += '0'
                    arg_idx += 1
                    i += 2
                    continue
                elif spec == 'f' and arg_idx < len(format_args):
                    try:
                        output += str(float(format_args[arg_idx]))
                    except:
                        output += '0.0'
                    arg_idx += 1
                    i += 2
                    continue
            output += result[i]
            i += 1
        
        return output

    def cmd_pwd(self, args, stdin=None):
        return self.system.filesystem.cwd + '\n'

    def cmd_cd(self, args, stdin=None):
        if not args:
            target = self.system.environment.get('HOME', '/root')
        elif args[0] == '-':
            target = self.system.environment.get('OLDPWD', self.system.filesystem.cwd)
        elif args[0] == '~':
            target = self.system.environment.get('HOME', '/root')
        else:
            target = args[0]
        
        resolved = self.system.filesystem.resolve_path(target)
        
        if not self.system.filesystem.exists(resolved):
            return f"-bash: cd: {target}: No such file or directory\n"
        
        if not self.system.filesystem.is_dir(resolved):
            return f"-bash: cd: {target}: Not a directory\n"
        
        self.system.environment['OLDPWD'] = self.system.filesystem.cwd
        self.system.filesystem.cwd = resolved
        self.system.environment['PWD'] = resolved
        
        return ''

    def cmd_mkdir(self, args, stdin=None):
        parents = False
        mode = 0o755
        verbose = False
        dirs = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-p' or arg == '--parents':
                parents = True
            elif arg == '-v' or arg == '--verbose':
                verbose = True
            elif arg == '-m' or arg == '--mode':
                if i + 1 < len(args):
                    try:
                        mode = int(args[i + 1], 8)
                    except:
                        pass
                    i += 1
            elif not arg.startswith('-'):
                dirs.append(arg)
            i += 1
        
        output = []
        for d in dirs:
            if self.system.filesystem.mkdir(d, parents=parents):
                if verbose:
                    output.append(f"mkdir: created directory '{d}'")
            else:
                if not parents:
                    output.append(f"mkdir: cannot create directory '{d}': File exists or parent missing")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_rmdir(self, args, stdin=None):
        output = []
        for arg in args:
            if arg.startswith('-'):
                continue
            resolved = self.system.filesystem.resolve_path(arg)
            node = self.system.filesystem._get_node(resolved)
            if node is None:
                output.append(f"rmdir: failed to remove '{arg}': No such file or directory")
            elif not node.is_dir:
                output.append(f"rmdir: failed to remove '{arg}': Not a directory")
            elif node.children:
                output.append(f"rmdir: failed to remove '{arg}': Directory not empty")
            else:
                self.system.filesystem.delete(arg)
        return '\n'.join(output) + '\n' if output else ''

    def cmd_rm(self, args, stdin=None):
        recursive = False
        force = False
        verbose = False
        files = []
        
        for arg in args:
            if arg == '-r' or arg == '-R' or arg == '--recursive':
                recursive = True
            elif arg == '-f' or arg == '--force':
                force = True
            elif arg == '-v' or arg == '--verbose':
                verbose = True
            elif arg == '-rf' or arg == '-fr':
                recursive = True
                force = True
            elif not arg.startswith('-'):
                files.append(arg)
        
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
            else:
                output.append(f"rm: cannot remove '{f}': Operation failed")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_cp(self, args, stdin=None):
        recursive = False
        verbose = False
        preserve = False
        force = False
        sources = []
        dest = None
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-r' or arg == '-R' or arg == '--recursive':
                recursive = True
            elif arg == '-v' or arg == '--verbose':
                verbose = True
            elif arg == '-p' or arg == '--preserve':
                preserve = True
            elif arg == '-f' or arg == '--force':
                force = True
            elif not arg.startswith('-'):
                sources.append(arg)
            i += 1
        
        if len(sources) < 2:
            return "cp: missing destination file operand\n"
        
        dest = sources.pop()
        output = []
        
        for src in sources:
            if not self.system.filesystem.exists(src):
                output.append(f"cp: cannot stat '{src}': No such file or directory")
                continue
            
            if self.system.filesystem.is_dir(src) and not recursive:
                output.append(f"cp: -r not specified; omitting directory '{src}'")
                continue
            
            if self.system.filesystem.copy(src, dest):
                if verbose:
                    output.append(f"'{src}' -> '{dest}'")
            else:
                output.append(f"cp: cannot copy '{src}' to '{dest}'")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_mv(self, args, stdin=None):
        verbose = False
        force = False
        sources = []
        
        for arg in args:
            if arg == '-v' or arg == '--verbose':
                verbose = True
            elif arg == '-f' or arg == '--force':
                force = True
            elif not arg.startswith('-'):
                sources.append(arg)
        
        if len(sources) < 2:
            return "mv: missing destination file operand\n"
        
        dest = sources.pop()
        output = []
        
        for src in sources:
            if not self.system.filesystem.exists(src):
                output.append(f"mv: cannot stat '{src}': No such file or directory")
                continue
            
            if self.system.filesystem.move(src, dest):
                if verbose:
                    output.append(f"renamed '{src}' -> '{dest}'")
            else:
                output.append(f"mv: cannot move '{src}' to '{dest}'")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_touch(self, args, stdin=None):
        for arg in args:
            if arg.startswith('-'):
                continue
            if not self.system.filesystem.exists(arg):
                self.system.filesystem.write_file(arg, '')
            else:
                node = self.system.filesystem._get_node(self.system.filesystem.resolve_path(arg))
                if node:
                    node.accessed = time.time()
                    node.modified = time.time()
        return ''

    def cmd_chmod(self, args, stdin=None):
        if len(args) < 2:
            return "chmod: missing operand\n"
        
        recursive = False
        verbose = False
        mode_str = None
        files = []
        
        for arg in args:
            if arg == '-R' or arg == '--recursive':
                recursive = True
            elif arg == '-v' or arg == '--verbose':
                verbose = True
            elif mode_str is None and (arg[0].isdigit() or arg[0] in 'ugoa+-'):
                mode_str = arg
            elif not arg.startswith('-'):
                files.append(arg)
        
        if not mode_str or not files:
            return "chmod: missing operand\n"
        
        try:
            mode = int(mode_str, 8)
        except:
            mode = 0o644
        
        output = []
        for f in files:
            if self.system.filesystem.chmod(f, mode):
                if verbose:
                    output.append(f"mode of '{f}' changed to {oct(mode)[2:]}")
            else:
                output.append(f"chmod: cannot access '{f}': No such file or directory")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_chown(self, args, stdin=None):
        if len(args) < 2:
            return "chown: missing operand\n"
        
        owner_group = args[0]
        files = [a for a in args[1:] if not a.startswith('-')]
        
        if ':' in owner_group:
            owner, group = owner_group.split(':', 1)
        else:
            owner = owner_group
            group = None
        
        output = []
        for f in files:
            if self.system.filesystem.chown(f, owner, group):
                pass
            else:
                output.append(f"chown: cannot access '{f}': No such file or directory")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_chgrp(self, args, stdin=None):
        if len(args) < 2:
            return "chgrp: missing operand\n"
        
        group = args[0]
        files = [a for a in args[1:] if not a.startswith('-')]
        
        output = []
        for f in files:
            if self.system.filesystem.chown(f, None, group):
                pass
            else:
                output.append(f"chgrp: cannot access '{f}': No such file or directory")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_ln(self, args, stdin=None):
        symbolic = False
        force = False
        verbose = False
        sources = []
        
        for arg in args:
            if arg == '-s' or arg == '--symbolic':
                symbolic = True
            elif arg == '-f' or arg == '--force':
                force = True
            elif arg == '-v' or arg == '--verbose':
                verbose = True
            elif not arg.startswith('-'):
                sources.append(arg)
        
        if len(sources) < 2:
            return "ln: missing destination file operand\n"
        
        return f"ln: created {'symbolic ' if symbolic else ''}link '{sources[-1]}' -> '{sources[0]}'\n" if verbose else ''

    def cmd_readlink(self, args, stdin=None):
        for arg in args:
            if not arg.startswith('-'):
                return f"{arg}\n"
        return ''

    def cmd_realpath(self, args, stdin=None):
        output = []
        for arg in args:
            if not arg.startswith('-'):
                output.append(self.system.filesystem.resolve_path(arg))
        return '\n'.join(output) + '\n' if output else ''

    def cmd_basename(self, args, stdin=None):
        if not args:
            return "basename: missing operand\n"
        path = args[0]
        suffix = args[1] if len(args) > 1 else ''
        name = path.rstrip('/').split('/')[-1]
        if suffix and name.endswith(suffix):
            name = name[:-len(suffix)]
        return name + '\n'

    def cmd_dirname(self, args, stdin=None):
        if not args:
            return "dirname: missing operand\n"
        path = args[0].rstrip('/')
        if '/' not in path:
            return '.\n'
        return '/'.join(path.split('/')[:-1]) or '/' + '\n'

    def cmd_head(self, args, stdin=None):
        lines = 10
        files = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-n' and i + 1 < len(args):
                try:
                    lines = int(args[i + 1])
                except:
                    pass
                i += 1
            elif arg.startswith('-n'):
                try:
                    lines = int(arg[2:])
                except:
                    pass
            elif arg.startswith('-') and arg[1:].isdigit():
                lines = int(arg[1:])
            elif not arg.startswith('-'):
                files.append(arg)
            i += 1
        
        output = []
        
        if stdin and not files:
            content_lines = stdin.split('\n')
            output.extend(content_lines[:lines])
        else:
            for f in files:
                content = self.system.filesystem.read_file(f)
                if content is None:
                    output.append(f"head: cannot open '{f}' for reading: No such file or directory")
                    continue
                
                if len(files) > 1:
                    output.append(f"==> {f} <==")
                
                content_lines = content.split('\n')
                output.extend(content_lines[:lines])
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_tail(self, args, stdin=None):
        lines = 10
        follow = False
        files = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-n' and i + 1 < len(args):
                try:
                    lines = int(args[i + 1])
                except:
                    pass
                i += 1
            elif arg.startswith('-n'):
                try:
                    lines = int(arg[2:])
                except:
                    pass
            elif arg == '-f' or arg == '--follow':
                follow = True
            elif arg.startswith('-') and arg[1:].isdigit():
                lines = int(arg[1:])
            elif not arg.startswith('-'):
                files.append(arg)
            i += 1
        
        output = []
        
        if stdin and not files:
            content_lines = stdin.strip().split('\n')
            output.extend(content_lines[-lines:])
        else:
            for f in files:
                content = self.system.filesystem.read_file(f)
                if content is None:
                    output.append(f"tail: cannot open '{f}' for reading: No such file or directory")
                    continue
                
                if len(files) > 1:
                    output.append(f"==> {f} <==")
                
                content_lines = content.strip().split('\n')
                output.extend(content_lines[-lines:])
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_wc(self, args, stdin=None):
        show_lines = False
        show_words = False
        show_chars = False
        show_bytes = False
        files = []
        
        for arg in args:
            if arg == '-l' or arg == '--lines':
                show_lines = True
            elif arg == '-w' or arg == '--words':
                show_words = True
            elif arg == '-c' or arg == '--bytes':
                show_bytes = True
            elif arg == '-m' or arg == '--chars':
                show_chars = True
            elif not arg.startswith('-'):
                files.append(arg)
        
        if not any([show_lines, show_words, show_chars, show_bytes]):
            show_lines = show_words = show_bytes = True
        
        output = []
        total_lines = total_words = total_chars = 0
        
        contents = []
        if stdin and not files:
            contents.append(('', stdin))
        else:
            for f in files:
                content = self.system.filesystem.read_file(f)
                if content is None:
                    output.append(f"wc: {f}: No such file or directory")
                    continue
                contents.append((f, content))
        
        for filename, content in contents:
            lines = content.count('\n')
            words = len(content.split())
            chars = len(content)
            
            total_lines += lines
            total_words += words
            total_chars += chars
            
            parts = []
            if show_lines:
                parts.append(f"{lines:>8}")
            if show_words:
                parts.append(f"{words:>8}")
            if show_bytes or show_chars:
                parts.append(f"{chars:>8}")
            
            if filename:
                parts.append(f" {filename}")
            
            output.append(''.join(parts))
        
        if len(contents) > 1:
            parts = []
            if show_lines:
                parts.append(f"{total_lines:>8}")
            if show_words:
                parts.append(f"{total_words:>8}")
            if show_bytes or show_chars:
                parts.append(f"{total_chars:>8}")
            parts.append(" total")
            output.append(''.join(parts))
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_sort(self, args, stdin=None):
        reverse = False
        numeric = False
        unique = False
        ignore_case = False
        files = []
        
        for arg in args:
            if arg == '-r' or arg == '--reverse':
                reverse = True
            elif arg == '-n' or arg == '--numeric-sort':
                numeric = True
            elif arg == '-u' or arg == '--unique':
                unique = True
            elif arg == '-f' or arg == '--ignore-case':
                ignore_case = True
            elif not arg.startswith('-'):
                files.append(arg)
        
        content = ''
        if stdin and not files:
            content = stdin
        else:
            for f in files:
                fc = self.system.filesystem.read_file(f)
                if fc:
                    content += fc
        
        lines = content.strip().split('\n') if content.strip() else []
        
        if numeric:
            def sort_key(x):
                try:
                    return float(x.split()[0]) if x.split() else 0
                except:
                    return 0
            lines.sort(key=sort_key, reverse=reverse)
        elif ignore_case:
            lines.sort(key=str.lower, reverse=reverse)
        else:
            lines.sort(reverse=reverse)
        
        if unique:
            lines = list(dict.fromkeys(lines))
        
        return '\n'.join(lines) + '\n' if lines else ''

    def cmd_uniq(self, args, stdin=None):
        count = False
        repeated = False
        ignore_case = False
        files = []
        
        for arg in args:
            if arg == '-c' or arg == '--count':
                count = True
            elif arg == '-d' or arg == '--repeated':
                repeated = True
            elif arg == '-i' or arg == '--ignore-case':
                ignore_case = True
            elif not arg.startswith('-'):
                files.append(arg)
        
        content = ''
        if stdin and not files:
            content = stdin
        elif files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        lines = content.strip().split('\n') if content.strip() else []
        
        result = []
        prev = None
        cnt = 0
        
        for line in lines:
            compare_line = line.lower() if ignore_case else line
            if compare_line != prev:
                if prev is not None:
                    if not repeated or cnt > 1:
                        if count:
                            result.append(f"{cnt:>7} {prev_orig}")
                        else:
                            result.append(prev_orig)
                prev = compare_line
                prev_orig = line
                cnt = 1
            else:
                cnt += 1
        
        if prev is not None:
            if not repeated or cnt > 1:
                if count:
                    result.append(f"{cnt:>7} {prev_orig}")
                else:
                    result.append(prev_orig)
        
        return '\n'.join(result) + '\n' if result else ''

    def cmd_cut(self, args, stdin=None):
        delimiter = '\t'
        fields = None
        chars = None
        files = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-d' and i + 1 < len(args):
                delimiter = args[i + 1]
                i += 1
            elif arg.startswith('-d'):
                delimiter = arg[2:]
            elif arg == '-f' and i + 1 < len(args):
                fields = args[i + 1]
                i += 1
            elif arg.startswith('-f'):
                fields = arg[2:]
            elif arg == '-c' and i + 1 < len(args):
                chars = args[i + 1]
                i += 1
            elif arg.startswith('-c'):
                chars = arg[2:]
            elif not arg.startswith('-'):
                files.append(arg)
            i += 1
        
        content = ''
        if stdin and not files:
            content = stdin
        elif files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        lines = content.strip().split('\n') if content.strip() else []
        output = []
        
        for line in lines:
            if fields:
                parts = line.split(delimiter)
                selected = []
                for f in fields.split(','):
                    if '-' in f:
                        start, end = f.split('-')
                        start = int(start) - 1 if start else 0
                        end = int(end) if end else len(parts)
                        selected.extend(parts[start:end])
                    else:
                        idx = int(f) - 1
                        if 0 <= idx < len(parts):
                            selected.append(parts[idx])
                output.append(delimiter.join(selected))
            elif chars:
                selected = []
                for c in chars.split(','):
                    if '-' in c:
                        start, end = c.split('-')
                        start = int(start) - 1 if start else 0
                        end = int(end) if end else len(line)
                        selected.append(line[start:end])
                    else:
                        idx = int(c) - 1
                        if 0 <= idx < len(line):
                            selected.append(line[idx])
                output.append(''.join(selected))
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_tr(self, args, stdin=None):
        if len(args) < 1:
            return "tr: missing operand\n"
        
        delete = False
        squeeze = False
        complement = False
        
        non_flag_args = []
        for arg in args:
            if arg == '-d' or arg == '--delete':
                delete = True
            elif arg == '-s' or arg == '--squeeze-repeats':
                squeeze = True
            elif arg == '-c' or arg == '--complement':
                complement = True
            else:
                non_flag_args.append(arg)
        
        if not non_flag_args:
            return "tr: missing operand\n"
        
        set1 = non_flag_args[0]
        set2 = non_flag_args[1] if len(non_flag_args) > 1 else ''
        
        content = stdin or ''
        
        if delete:
            for c in set1:
                content = content.replace(c, '')
        elif set2:
            trans = str.maketrans(set1, set2[:len(set1)])
            content = content.translate(trans)
        
        if squeeze and set2:
            result = []
            prev = None
            for c in content:
                if c in set2 and c == prev:
                    continue
                result.append(c)
                prev = c
            content = ''.join(result)
        
        return content

    def cmd_grep(self, args, stdin=None):
        ignore_case = False
        invert = False
        count_only = False
        line_numbers = False
        files_only = False
        recursive = False
        extended = False
        fixed = False
        only_matching = False
        quiet = False
        pattern = None
        files = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-i' or arg == '--ignore-case':
                ignore_case = True
            elif arg == '-v' or arg == '--invert-match':
                invert = True
            elif arg == '-c' or arg == '--count':
                count_only = True
            elif arg == '-n' or arg == '--line-number':
                line_numbers = True
            elif arg == '-l' or arg == '--files-with-matches':
                files_only = True
            elif arg == '-r' or arg == '-R' or arg == '--recursive':
                recursive = True
            elif arg == '-E' or arg == '--extended-regexp':
                extended = True
            elif arg == '-F' or arg == '--fixed-strings':
                fixed = True
            elif arg == '-o' or arg == '--only-matching':
                only_matching = True
            elif arg == '-q' or arg == '--quiet' or arg == '--silent':
                quiet = True
            elif arg == '-e' and i + 1 < len(args):
                pattern = args[i + 1]
                i += 1
            elif arg == '--color=auto' or arg == '--color':
                pass
            elif not arg.startswith('-'):
                if pattern is None:
                    pattern = arg
                else:
                    files.append(arg)
            i += 1
        
        if pattern is None:
            return "grep: missing pattern\n"
        
        flags = re.IGNORECASE if ignore_case else 0
        
        if fixed:
            regex_pattern = re.escape(pattern)
        else:
            regex_pattern = pattern
        
        try:
            regex = re.compile(regex_pattern, flags)
        except re.error as e:
            return f"grep: Invalid regular expression: {e}\n"
        
        contents = []
        if stdin and not files:
            contents.append(('', stdin))
        else:
            for f in files:
                content = self.system.filesystem.read_file(f)
                if content is None:
                    continue
                contents.append((f, content))
        
        output = []
        match_count = 0
        show_filename = len(contents) > 1
        
        for filename, content in contents:
            lines = content.split('\n')
            file_matches = 0
            
            for line_num, line in enumerate(lines, 1):
                match = regex.search(line)
                matched = bool(match) != invert
                
                if matched:
                    file_matches += 1
                    match_count += 1
                    
                    if quiet:
                        continue
                    
                    if files_only:
                        if filename:
                            output.append(filename)
                        break
                    
                    if count_only:
                        continue
                    
                    prefix = ''
                    if show_filename and filename:
                        prefix = f"{filename}:"
                    if line_numbers:
                        prefix += f"{line_num}:"
                    
                    if only_matching and match and not invert:
                        output.append(f"{prefix}{match.group()}")
                    else:
                        output.append(f"{prefix}{line}")
            
            if count_only and not quiet:
                if filename:
                    output.append(f"{filename}:{file_matches}")
                else:
                    output.append(str(file_matches))
        
        if quiet:
            return '' if match_count > 0 else ''
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_egrep(self, args, stdin=None):
        return self.cmd_grep(['-E'] + args, stdin)

    def cmd_fgrep(self, args, stdin=None):
        return self.cmd_grep(['-F'] + args, stdin)

    def cmd_sed(self, args, stdin=None):
        in_place = False
        script = None
        files = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-i' or arg == '--in-place':
                in_place = True
            elif arg == '-e' and i + 1 < len(args):
                script = args[i + 1]
                i += 1
            elif arg == '-n' or arg == '--quiet' or arg == '--silent':
                pass
            elif not arg.startswith('-'):
                if script is None:
                    script = arg
                else:
                    files.append(arg)
            i += 1
        
        if script is None:
            return "sed: no script specified\n"
        
        content = ''
        if stdin and not files:
            content = stdin
        elif files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        if script.startswith('s'):
            delim = script[1]
            parts = script.split(delim)
            if len(parts) >= 3:
                pattern = parts[1]
                replacement = parts[2]
                flags = parts[3] if len(parts) > 3 else ''
                
                count = 0 if 'g' in flags else 1
                re_flags = re.IGNORECASE if 'i' in flags else 0
                
                try:
                    if count == 0:
                        content = re.sub(pattern, replacement, content, flags=re_flags)
                    else:
                        content = re.sub(pattern, replacement, content, count=count, flags=re_flags)
                except re.error:
                    pass
        elif script == 'd':
            content = ''
        elif script.startswith('/') and script.endswith('/d'):
            pattern = script[1:-2]
            lines = content.split('\n')
            lines = [l for l in lines if not re.search(pattern, l)]
            content = '\n'.join(lines)
        
        if in_place and files:
            self.system.filesystem.write_file(files[0], content)
            return ''
        
        return content

    def cmd_awk(self, args, stdin=None):
        program = None
        field_sep = None
        files = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-F' and i + 1 < len(args):
                field_sep = args[i + 1]
                i += 1
            elif arg.startswith('-F'):
                field_sep = arg[2:]
            elif not arg.startswith('-'):
                if program is None:
                    program = arg
                else:
                    files.append(arg)
            i += 1
        
        if program is None:
            return "awk: no program specified\n"
        
        content = ''
        if stdin and not files:
            content = stdin
        elif files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        lines = content.strip().split('\n') if content.strip() else []
        output = []
        
        if field_sep is None:
            field_sep = r'\s+'
        
        print_match = re.match(r'\{print\s+(.+)\}', program)
        if print_match:
            fields_expr = print_match.group(1)
            
            for line in lines:
                fields = re.split(field_sep, line)
                fields = [''] + fields
                
                result_parts = []
                for part in fields_expr.split(','):
                    part = part.strip()
                    if part == '$0':
                        result_parts.append(line)
                    elif part.startswith('$'):
                        try:
                            idx = int(part[1:])
                            if 0 <= idx < len(fields):
                                result_parts.append(fields[idx])
                        except:
                            result_parts.append(part)
                    elif part.startswith('"') and part.endswith('"'):
                        result_parts.append(part[1:-1])
                    else:
                        result_parts.append(part)
                
                output.append(' '.join(result_parts))
        elif program == '{print}' or program == '{print $0}':
            output = lines
        elif '/' in program:
            pattern_match = re.match(r'/(.+)/\s*\{(.+)\}', program)
            if pattern_match:
                pattern = pattern_match.group(1)
                action = pattern_match.group(2)
                for line in lines:
                    if re.search(pattern, line):
                        if action == 'print' or action == 'print $0':
                            output.append(line)
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_find(self, args, stdin=None):
        paths = []
        name_pattern = None
        type_filter = None
        maxdepth = None
        mindepth = 0
        size_filter = None
        mtime_filter = None
        exec_cmd = None
        print_null = False
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-name' and i + 1 < len(args):
                name_pattern = args[i + 1]
                i += 1
            elif arg == '-iname' and i + 1 < len(args):
                name_pattern = args[i + 1].lower()
                i += 1
            elif arg == '-type' and i + 1 < len(args):
                type_filter = args[i + 1]
                i += 1
            elif arg == '-maxdepth' and i + 1 < len(args):
                maxdepth = int(args[i + 1])
                i += 1
            elif arg == '-mindepth' and i + 1 < len(args):
                mindepth = int(args[i + 1])
                i += 1
            elif arg == '-size' and i + 1 < len(args):
                size_filter = args[i + 1]
                i += 1
            elif arg == '-mtime' and i + 1 < len(args):
                mtime_filter = args[i + 1]
                i += 1
            elif arg == '-exec':
                exec_parts = []
                i += 1
                while i < len(args) and args[i] != ';':
                    exec_parts.append(args[i])
                    i += 1
                exec_cmd = exec_parts
            elif arg == '-print0':
                print_null = True
            elif not arg.startswith('-'):
                paths.append(arg)
            i += 1
        
        if not paths:
            paths = ['.']
        
        results = []
        
        def search_dir(path, depth):
            if maxdepth is not None and depth > maxdepth:
                return
            
            resolved = self.system.filesystem.resolve_path(path)
            
            if depth >= mindepth:
                info = self.system.filesystem.get_file_info(resolved)
                if info:
                    match = True
                    
                    if name_pattern:
                        import fnmatch
                        if not fnmatch.fnmatch(info['name'], name_pattern):
                            match = False
                    
                    if type_filter:
                        if type_filter == 'f' and info['is_dir']:
                            match = False
                        elif type_filter == 'd' and not info['is_dir']:
                            match = False
                    
                    if match:
                        results.append(resolved)
            
            if self.system.filesystem.is_dir(resolved):
                files = self.system.filesystem.list_dir(resolved)
                if files:
                    for f in files:
                        child_path = f"{resolved}/{f}" if resolved != '/' else f"/{f}"
                        search_dir(child_path, depth + 1)
        
        for path in paths:
            search_dir(path, 0)
        
        if print_null:
            return '\0'.join(results) + '\0' if results else ''
        return '\n'.join(results) + '\n' if results else ''

    def cmd_locate(self, args, stdin=None):
        if not args:
            return "locate: no pattern specified\n"
        
        pattern = args[0]
        results = []
        
        def search(path):
            node = self.system.filesystem._get_node(path)
            if node is None:
                return
            
            if pattern in node.name:
                results.append(path)
            
            if node.is_dir and node.children:
                for name, child in node.children.items():
                    child_path = f"{path}/{name}" if path != '/' else f"/{name}"
                    search(child_path)
        
        search('/')
        return '\n'.join(results) + '\n' if results else ''

    def cmd_which(self, args, stdin=None):
        output = []
        paths = self.system.environment.get('PATH', '').split(':')
        
        for cmd in args:
            if cmd.startswith('-'):
                continue
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

    def cmd_whereis(self, args, stdin=None):
        output = []
        for cmd in args:
            if cmd.startswith('-'):
                continue
            locations = []
            for prefix in ['/bin', '/sbin', '/usr/bin', '/usr/sbin', '/usr/local/bin']:
                path = f"{prefix}/{cmd}"
                if self.system.filesystem.exists(path):
                    locations.append(path)
            man_path = f"/usr/share/man/man1/{cmd}.1"
            if self.system.filesystem.exists(man_path):
                locations.append(man_path)
            output.append(f"{cmd}: {' '.join(locations)}")
        return '\n'.join(output) + '\n' if output else ''

    def cmd_type(self, args, stdin=None):
        output = []
        builtins = ['cd', 'pwd', 'echo', 'export', 'alias', 'unalias', 'history', 
                   'exit', 'source', 'set', 'unset', 'type', 'help', 'jobs',
                   'fg', 'bg', 'wait', 'kill', 'exec', 'eval', 'read', 'test']
        
        for cmd in args:
            if cmd.startswith('-'):
                continue
            if cmd in builtins:
                output.append(f"{cmd} is a shell builtin")
            elif cmd in self.system.aliases:
                output.append(f"{cmd} is aliased to '{self.system.aliases[cmd]}'")
            else:
                paths = self.system.environment.get('PATH', '').split(':')
                found = False
                for path in paths:
                    full_path = f"{path}/{cmd}"
                    if self.system.filesystem.exists(full_path):
                        output.append(f"{cmd} is {full_path}")
                        found = True
                        break
                if not found:
                    output.append(f"-bash: type: {cmd}: not found")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_file(self, args, stdin=None):
        output = []
        for arg in args:
            if arg.startswith('-'):
                continue
            if not self.system.filesystem.exists(arg):
                output.append(f"{arg}: cannot open (No such file or directory)")
                continue
            
            info = self.system.filesystem.get_file_info(self.system.filesystem.resolve_path(arg))
            if info['is_dir']:
                output.append(f"{arg}: directory")
            else:
                content = self.system.filesystem.read_file(arg) or ''
                if content.startswith('#!/'):
                    if 'python' in content.split('\n')[0]:
                        output.append(f"{arg}: Python script, ASCII text executable")
                    elif 'bash' in content.split('\n')[0] or 'sh' in content.split('\n')[0]:
                        output.append(f"{arg}: Bourne-Again shell script, ASCII text executable")
                    else:
                        output.append(f"{arg}: script, ASCII text executable")
                elif content.startswith('\x7fELF'):
                    output.append(f"{arg}: ELF 64-bit LSB executable")
                elif all(c in '\n\r\t' or 32 <= ord(c) < 127 for c in content[:1000]):
                    output.append(f"{arg}: ASCII text")
                else:
                    output.append(f"{arg}: data")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_stat(self, args, stdin=None):
        output = []
        for arg in args:
            if arg.startswith('-'):
                continue
            
            info = self.system.filesystem.get_file_info(self.system.filesystem.resolve_path(arg))
            if info is None:
                output.append(f"stat: cannot stat '{arg}': No such file or directory")
                continue
            
            file_type = 'directory' if info['is_dir'] else 'regular file'
            mode_str = self._format_mode(info['permissions'], info['is_dir'])
            access_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info['accessed']))
            modify_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info['modified']))
            change_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info['created']))
            
            output.append(f"  File: {arg}")
            output.append(f"  Size: {info['size']:<15} Blocks: {info['size'] // 512:<10} IO Block: 4096   {file_type}")
            output.append(f"Device: 801h/2049d\tInode: {info['inode']:<12} Links: {info['links']}")
            output.append(f"Access: ({oct(info['permissions'])[2:]}/{mode_str})  Uid: (    0/    {info['owner']})   Gid: (    0/    {info['group']})")
            output.append(f"Access: {access_time}.000000000 +0000")
            output.append(f"Modify: {modify_time}.000000000 +0000")
            output.append(f"Change: {change_time}.000000000 +0000")
            output.append(f" Birth: -")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_diff(self, args, stdin=None):
        unified = False
        files = []
        
        for arg in args:
            if arg == '-u' or arg == '--unified':
                unified = True
            elif not arg.startswith('-'):
                files.append(arg)
        
        if len(files) < 2:
            return "diff: missing operand\n"
        
        content1 = self.system.filesystem.read_file(files[0])
        content2 = self.system.filesystem.read_file(files[1])
        
        if content1 is None:
            return f"diff: {files[0]}: No such file or directory\n"
        if content2 is None:
            return f"diff: {files[1]}: No such file or directory\n"
        
        lines1 = content1.split('\n')
        lines2 = content2.split('\n')
        
        if content1 == content2:
            return ''
        
        output = []
        if unified:
            output.append(f"--- {files[0]}")
            output.append(f"+++ {files[1]}")
            output.append("@@ -1,{} +1,{} @@".format(len(lines1), len(lines2)))
        
        import difflib
        diff = difflib.unified_diff(lines1, lines2, fromfile=files[0], tofile=files[1], lineterm='')
        output.extend(list(diff))
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_cmp(self, args, stdin=None):
        files = [a for a in args if not a.startswith('-')]
        
        if len(files) < 2:
            return "cmp: missing operand\n"
        
        content1 = self.system.filesystem.read_file(files[0])
        content2 = self.system.filesystem.read_file(files[1])
        
        if content1 is None:
            return f"cmp: {files[0]}: No such file or directory\n"
        if content2 is None:
            return f"cmp: {files[1]}: No such file or directory\n"
        
        if content1 == content2:
            return ''
        
        for i, (c1, c2) in enumerate(zip(content1, content2)):
            if c1 != c2:
                line = content1[:i].count('\n') + 1
                return f"{files[0]} {files[1]} differ: byte {i+1}, line {line}\n"
        
        if len(content1) != len(content2):
            shorter = files[0] if len(content1) < len(content2) else files[1]
            return f"cmp: EOF on {shorter}\n"
        
        return ''

    def cmd_comm(self, args, stdin=None):
        files = [a for a in args if not a.startswith('-')]
        
        if len(files) < 2:
            return "comm: missing operand\n"
        
        content1 = self.system.filesystem.read_file(files[0]) or ''
        content2 = self.system.filesystem.read_file(files[1]) or ''
        
        lines1 = set(content1.strip().split('\n'))
        lines2 = set(content2.strip().split('\n'))
        
        only1 = lines1 - lines2
        only2 = lines2 - lines1
        both = lines1 & lines2
        
        output = []
        for line in sorted(only1):
            output.append(line)
        for line in sorted(only2):
            output.append(f"\t{line}")
        for line in sorted(both):
            output.append(f"\t\t{line}")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_tar(self, args, stdin=None):
        create = False
        extract = False
        list_only = False
        verbose = False
        gzip = False
        bzip2 = False
        xz = False
        filename = None
        files = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg.startswith('-'):
                for c in arg[1:] if arg.startswith('-') and not arg.startswith('--') else []:
                    if c == 'c':
                        create = True
                    elif c == 'x':
                        extract = True
                    elif c == 't':
                        list_only = True
                    elif c == 'v':
                        verbose = True
                    elif c == 'z':
                        gzip = True
                    elif c == 'j':
                        bzip2 = True
                    elif c == 'J':
                        xz = True
                    elif c == 'f':
                        if i + 1 < len(args):
                            i += 1
                            filename = args[i]
                if arg == '--create':
                    create = True
                elif arg == '--extract':
                    extract = True
                elif arg == '--list':
                    list_only = True
                elif arg == '--verbose':
                    verbose = True
                elif arg == '--gzip':
                    gzip = True
                elif arg == '--file' and i + 1 < len(args):
                    i += 1
                    filename = args[i]
            else:
                if filename is None and (create or extract or list_only):
                    filename = arg
                else:
                    files.append(arg)
            i += 1
        
        if create:
            if not filename:
                return "tar: Refusing to write archive to stdout\n"
            output = []
            for f in files:
                if verbose:
                    output.append(f)
            return '\n'.join(output) + f"\ntar: Created archive {filename}\n" if output else f"tar: Created archive {filename}\n"
        elif extract:
            if not filename:
                return "tar: No archive file specified\n"
            return f"tar: Extracted from {filename}\n"
        elif list_only:
            return f"tar: Contents of {filename or 'archive'}\n"
        
        return "tar: You must specify one of '-c', '-x', or '-t' options\n"

    def cmd_gzip(self, args, stdin=None):
        decompress = False
        keep = False
        verbose = False
        files = []
        
        for arg in args:
            if arg == '-d' or arg == '--decompress':
                decompress = True
            elif arg == '-k' or arg == '--keep':
                keep = True
            elif arg == '-v' or arg == '--verbose':
                verbose = True
            elif not arg.startswith('-'):
                files.append(arg)
        
        output = []
        for f in files:
            if decompress:
                if verbose:
                    output.append(f"{f}: decompressed")
            else:
                if verbose:
                    output.append(f"{f}: compressed")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_gunzip(self, args, stdin=None):
        return self.cmd_gzip(['-d'] + args, stdin)

    def cmd_zcat(self, args, stdin=None):
        files = [a for a in args if not a.startswith('-')]
        output = []
        for f in files:
            content = self.system.filesystem.read_file(f)
            if content:
                output.append(content)
        return '\n'.join(output) if output else ''

    def cmd_bzip2(self, args, stdin=None):
        return self.cmd_gzip(args, stdin)

    def cmd_xz(self, args, stdin=None):
        return self.cmd_gzip(args, stdin)

    def cmd_zip(self, args, stdin=None):
        files = [a for a in args if not a.startswith('-')]
        if files:
            return f"  adding: {', '.join(files[1:])} (stored 0%)\n" if len(files) > 1 else ''
        return ''

    def cmd_unzip(self, args, stdin=None):
        files = [a for a in args if not a.startswith('-')]
        if files:
            return f"Archive:  {files[0]}\n  extracting: ...\n"
        return "unzip: missing archive filename\n"

    def cmd_ps(self, args, stdin=None):
        aux = False
        full = False
        all_procs = False
        
        for arg in args:
            if 'a' in arg and 'u' in arg and 'x' in arg:
                aux = True
            elif arg == '-ef' or arg == '-e':
                full = True
                all_procs = True
            elif arg == '-f':
                full = True
            elif arg == '-a' or arg == '-A':
                all_procs = True
        
        return self.system.process_manager.format_ps_output(full=full, aux=aux) + '\n'

    def cmd_top(self, args, stdin=None):
        return self.system.process_manager.format_top_output() + '\n'

    def cmd_kill(self, args, stdin=None):
        signal = 15
        pids = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-l' or arg == '--list':
                signals = " 1) SIGHUP\t 2) SIGINT\t 3) SIGQUIT\t 4) SIGILL\t 5) SIGTRAP\n"
                signals += " 6) SIGABRT\t 7) SIGBUS\t 8) SIGFPE\t 9) SIGKILL\t10) SIGUSR1\n"
                signals += "11) SIGSEGV\t12) SIGUSR2\t13) SIGPIPE\t14) SIGALRM\t15) SIGTERM\n"
                signals += "16) SIGSTKFLT\t17) SIGCHLD\t18) SIGCONT\t19) SIGSTOP\t20) SIGTSTP\n"
                return signals
            elif arg.startswith('-'):
                try:
                    signal = int(arg[1:])
                except:
                    if arg[1:].upper() == 'KILL' or arg[1:] == '9':
                        signal = 9
                    elif arg[1:].upper() == 'TERM' or arg[1:] == '15':
                        signal = 15
                    elif arg[1:].upper() == 'HUP' or arg[1:] == '1':
                        signal = 1
                    elif arg[1:].upper() == 'INT' or arg[1:] == '2':
                        signal = 2
            else:
                try:
                    pids.append(int(arg))
                except:
                    pass
            i += 1
        
        output = []
        for pid in pids:
            success, msg = self.system.process_manager.kill_process(pid, signal)
            if not success:
                output.append(f"kill: ({pid}) - {msg}")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_killall(self, args, stdin=None):
        signal = 15
        names = []
        
        for arg in args:
            if arg.startswith('-'):
                try:
                    signal = int(arg[1:])
                except:
                    pass
            else:
                names.append(arg)
        
        output = []
        for name in names:
            procs = self.system.process_manager.get_processes_by_name(name)
            if not procs:
                output.append(f"{name}: no process found")
            for proc in procs:
                self.system.process_manager.kill_process(proc.pid, signal)
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_pkill(self, args, stdin=None):
        return self.cmd_killall(args, stdin)

    def cmd_pgrep(self, args, stdin=None):
        list_name = False
        names = []
        
        for arg in args:
            if arg == '-l' or arg == '--list-name':
                list_name = True
            elif not arg.startswith('-'):
                names.append(arg)
        
        output = []
        for name in names:
            procs = self.system.process_manager.get_processes_by_name(name)
            for proc in procs:
                if list_name:
                    output.append(f"{proc.pid} {proc.name}")
                else:
                    output.append(str(proc.pid))
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_nice(self, args, stdin=None):
        nice_value = 10
        command = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-n' and i + 1 < len(args):
                try:
                    nice_value = int(args[i + 1])
                except:
                    pass
                i += 1
            elif not arg.startswith('-'):
                command = args[i:]
                break
            i += 1
        
        if command:
            return f"Running '{' '.join(command)}' with nice value {nice_value}\n"
        return f"{nice_value}\n"

    def cmd_renice(self, args, stdin=None):
        if len(args) < 2:
            return "renice: missing operand\n"
        
        try:
            priority = int(args[0])
        except:
            return "renice: invalid priority\n"
        
        output = []
        for arg in args[1:]:
            if arg == '-p':
                continue
            try:
                pid = int(arg)
                if self.system.process_manager.set_nice(pid, priority):
                    output.append(f"{pid} (process ID) old priority 0, new priority {priority}")
                else:
                    output.append(f"renice: {pid}: No such process")
            except:
                pass
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_nohup(self, args, stdin=None):
        if not args:
            return "nohup: missing operand\n"
        return f"nohup: running '{' '.join(args)}'\n"

    def cmd_jobs(self, args, stdin=None):
        if not self.system.jobs:
            return ''
        output = []
        for i, job in enumerate(self.system.jobs):
            output.append(f"[{i+1}]+ {job['status']}\t{job['command']}")
        return '\n'.join(output) + '\n'

    def cmd_fg(self, args, stdin=None):
        return "fg: no current job\n"

    def cmd_bg(self, args, stdin=None):
        return "bg: no current job\n"

    def cmd_wait(self, args, stdin=None):
        return ''

    def cmd_df(self, args, stdin=None):
        human_readable = False
        
        for arg in args:
            if arg == '-h' or arg == '--human-readable':
                human_readable = True
        
        disk = psutil.disk_usage('/')
        
        if human_readable:
            def fmt(n):
                if n >= 1024**3:
                    return f"{n/1024**3:.1f}G"
                elif n >= 1024**2:
                    return f"{n/1024**2:.1f}M"
                elif n >= 1024:
                    return f"{n/1024:.1f}K"
                return str(n)
            
            output = "Filesystem      Size  Used Avail Use% Mounted on\n"
            output += f"/dev/sda1       {fmt(disk.total):>4}  {fmt(disk.used):>4}  {fmt(disk.free):>4}  {disk.percent:>2.0f}% /\n"
            output += f"tmpfs           {fmt(psutil.virtual_memory().total // 2):>4}     0  {fmt(psutil.virtual_memory().total // 2):>4}   0% /tmp\n"
            output += f"tmpfs           {fmt(psutil.virtual_memory().total // 10):>4}  {fmt(1024*1024):>4}  {fmt(psutil.virtual_memory().total // 10):>4}   1% /run\n"
        else:
            output = "Filesystem     1K-blocks    Used Available Use% Mounted on\n"
            output += f"/dev/sda1      {disk.total//1024:>10} {disk.used//1024:>7} {disk.free//1024:>9} {disk.percent:>2.0f}% /\n"
        
        return output

    def cmd_du(self, args, stdin=None):
        human_readable = False
        summary = False
        paths = []
        
        for arg in args:
            if arg == '-h' or arg == '--human-readable':
                human_readable = True
            elif arg == '-s' or arg == '--summarize':
                summary = True
            elif not arg.startswith('-'):
                paths.append(arg)
        
        if not paths:
            paths = ['.']
        
        output = []
        for path in paths:
            resolved = self.system.filesystem.resolve_path(path)
            size = self._calculate_size(resolved)
            
            if human_readable:
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

    def _calculate_size(self, path):
        node = self.system.filesystem._get_node(path)
        if node is None:
            return 0
        
        if not node.is_dir:
            return node.size
        
        total = 4096
        if node.children:
            for name, child in node.children.items():
                child_path = f"{path}/{name}" if path != '/' else f"/{name}"
                total += self._calculate_size(child_path)
        
        return total

    def cmd_free(self, args, stdin=None):
        human_readable = any(arg in ['-h', '--human'] for arg in args)
        return self.system.memory_manager.format_free_output(human_readable) + '\n'

    def cmd_vmstat(self, args, stdin=None):
        return self.system.memory_manager.get_vmstat() + '\n'

    def cmd_iostat(self, args, stdin=None):
        cpu = psutil.cpu_percent(interval=0.1)
        output = f"""Linux 6.1.0-pylinux ({self.system.hostname}) \t{time.strftime('%m/%d/%Y')}\t_x86_64_\t({psutil.cpu_count()} CPU)

avg-cpu:  %user   %nice %system %iowait  %steal   %idle
          {cpu/2:.2f}    0.00    {cpu/4:.2f}    0.00    0.00   {100-cpu:.2f}

Device             tps    kB_read/s    kB_wrtn/s    kB_read    kB_wrtn
sda              10.00        50.00        25.00     102400      51200
"""
        return output

    def cmd_mpstat(self, args, stdin=None):
        cpu_times = psutil.cpu_times_percent(interval=0.1)
        output = f"""Linux 6.1.0-pylinux ({self.system.hostname}) \t{time.strftime('%m/%d/%Y')}\t_x86_64_\t({psutil.cpu_count()} CPU)

{time.strftime('%H:%M:%S')}  CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
{time.strftime('%H:%M:%S')}  all   {cpu_times.user:>5.2f}   {cpu_times.nice:>5.2f}   {cpu_times.system:>5.2f}   {cpu_times.iowait:>5.2f}    0.00    0.00    0.00    0.00    0.00  {cpu_times.idle:>5.2f}
"""
        return output

    def cmd_uptime(self, args, stdin=None):
        uptime_secs = self.system.get_uptime()
        hours = int(uptime_secs // 3600)
        minutes = int((uptime_secs % 3600) // 60)
        
        try:
            load = psutil.getloadavg()
            load_str = f"{load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}"
        except:
            load_str = "0.00, 0.00, 0.00"
        
        return f" {time.strftime('%H:%M:%S')} up {hours}:{minutes:02d},  1 user,  load average: {load_str}\n"

    def cmd_w(self, args, stdin=None):
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

    def cmd_who(self, args, stdin=None):
        return f"root     tty1         {time.strftime('%Y-%m-%d %H:%M')}\n"

    def cmd_whoami(self, args, stdin=None):
        return f"{self.system.current_user or 'root'}\n"

    def cmd_id(self, args, stdin=None):
        user = args[0] if args and not args[0].startswith('-') else (self.system.current_user or 'root')
        
        if user == 'root':
            return "uid=0(root) gid=0(root) groups=0(root)\n"
        else:
            return f"uid=1000({user}) gid=1000({user}) groups=1000({user}),27(sudo),100(users)\n"

    def cmd_groups(self, args, stdin=None):
        user = args[0] if args else (self.system.current_user or 'root')
        if user == 'root':
            return "root\n"
        return f"{user} sudo users\n"

    def cmd_users(self, args, stdin=None):
        return f"{self.system.current_user or 'root'}\n"

    def cmd_last(self, args, stdin=None):
        output = f"""root     tty1                          {time.strftime('%a %b %d %H:%M')}   still logged in
reboot   system boot  6.1.0-pylinux     {time.strftime('%a %b %d %H:%M')}   still running
root     tty1                          {time.strftime('%a %b %d %H:%M', time.localtime(time.time() - 86400))} - {time.strftime('%H:%M', time.localtime(time.time() - 82800))}  (01:00)

wtmp begins {time.strftime('%a %b %d %H:%M:%S %Y', time.localtime(time.time() - 86400*30))}
"""
        return output

    def cmd_lastlog(self, args, stdin=None):
        output = "Username         Port     From             Latest\n"
        output += f"root             tty1                      {time.strftime('%a %b %d %H:%M:%S %z %Y')}\n"
        output += "daemon                                     **Never logged in**\n"
        output += "bin                                        **Never logged in**\n"
        return output

    def cmd_finger(self, args, stdin=None):
        user = args[0] if args else 'root'
        return f"""Login: {user}           \t\t\tName: {user.title()}
Directory: /{user if user != 'root' else 'root'}      \t\tShell: /bin/bash
On since {time.strftime('%a %b %d %H:%M')} on tty1
No mail.
No Plan.
"""

    def cmd_hostname(self, args, stdin=None):
        if args and not args[0].startswith('-'):
            self.system.hostname = args[0]
            self.system.environment['HOSTNAME'] = args[0]
            return ''
        
        for arg in args:
            if arg == '-f' or arg == '--fqdn':
                return f"{self.system.hostname}.localdomain\n"
            elif arg == '-i' or arg == '--ip-address':
                return "127.0.0.1\n"
            elif arg == '-I' or arg == '--all-ip-addresses':
                return "127.0.0.1 ::1\n"
            elif arg == '-s' or arg == '--short':
                return f"{self.system.hostname}\n"
        
        return f"{self.system.hostname}\n"

    def cmd_hostnamectl(self, args, stdin=None):
        return f"""   Static hostname: {self.system.hostname}
         Icon name: computer-vm
           Chassis: vm
        Machine ID: {'0' * 32}
           Boot ID: {'1' * 32}
    Virtualization: container
  Operating System: PyLinux 6.1.0
            Kernel: Linux 6.1.0-pylinux
      Architecture: x86-64
"""

    def cmd_uname(self, args, stdin=None):
        if not args:
            return "Linux\n"
        
        options = ''.join(args).replace('-', '')
        return self.system.kernel.get_uname(options) + '\n'

    def cmd_arch(self, args, stdin=None):
        return f"{self.system.kernel.machine}\n"

    def cmd_nproc(self, args, stdin=None):
        return f"{psutil.cpu_count()}\n"

    def cmd_lscpu(self, args, stdin=None):
        freq = psutil.cpu_freq()
        return f"""Architecture:            x86_64
CPU op-mode(s):          32-bit, 64-bit
Address sizes:           48 bits physical, 48 bits virtual
Byte Order:              Little Endian
CPU(s):                  {psutil.cpu_count()}
On-line CPU(s) list:     0-{psutil.cpu_count() - 1}
Vendor ID:               GenuineIntel
Model name:              Intel(R) Core(TM) Processor
CPU family:              6
Model:                   142
Thread(s) per core:      {psutil.cpu_count() // (psutil.cpu_count(logical=False) or 1)}
Core(s) per socket:      {psutil.cpu_count(logical=False) or psutil.cpu_count()}
Socket(s):               1
Stepping:                10
CPU max MHz:             {freq.max if freq else 3000:.4f}
CPU min MHz:             {freq.min if freq else 800:.4f}
BogoMIPS:                {freq.current * 2 if freq else 4800:.2f}
Flags:                   fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss ht syscall nx pdpe1gb rdtscp lm constant_tsc rep_good nopl xtopology cpuid pni pclmulqdq ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt aes xsave avx f16c rdrand hypervisor lahf_lm
Virtualization:          VT-x
L1d cache:               32K
L1i cache:               32K
L2 cache:                256K
L3 cache:                8192K
"""

    def cmd_lsmem(self, args, stdin=None):
        mem = psutil.virtual_memory()
        return f"""RANGE                                 SIZE  STATE REMOVABLE BLOCK
0x0000000000000000-0x{mem.total:016x} {mem.total // (1024**3)}G online       yes     0

Memory block size:       128M
Total online memory:     {mem.total // (1024**3)}G
Total offline memory:    0B
"""

    def cmd_lspci(self, args, stdin=None):
        return """00:00.0 Host bridge: Intel Corporation Device
00:01.0 PCI bridge: Intel Corporation Device
00:02.0 VGA compatible controller: Intel Corporation Device
00:14.0 USB controller: Intel Corporation Device
00:16.0 Communication controller: Intel Corporation Device
00:17.0 SATA controller: Intel Corporation Device
00:1f.0 ISA bridge: Intel Corporation Device
00:1f.2 Memory controller: Intel Corporation Device
00:1f.3 Audio device: Intel Corporation Device
00:1f.4 SMBus: Intel Corporation Device
"""

    def cmd_lsusb(self, args, stdin=None):
        return """Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 002: ID 0627:0001 Adomax Technology Co., Ltd QEMU USB Keyboard
Bus 001 Device 003: ID 0627:0001 Adomax Technology Co., Ltd QEMU USB Mouse
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
"""

    def cmd_lsblk(self, args, stdin=None):
        disk = psutil.disk_usage('/')
        size_gb = disk.total / (1024**3)
        return f"""NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
sda      8:0    0   {size_gb:.1f}G  0 disk 
├─sda1   8:1    0   {size_gb - 1:.1f}G  0 part /
└─sda2   8:2    0     1G  0 part [SWAP]
sr0     11:0    1  1024M  0 rom  
"""

    def cmd_blkid(self, args, stdin=None):
        return """/dev/sda1: UUID="12345678-1234-1234-1234-123456789abc" TYPE="ext4" PARTUUID="abcd1234-01"
/dev/sda2: UUID="87654321-4321-4321-4321-cba987654321" TYPE="swap" PARTUUID="abcd1234-02"
"""

    def cmd_fdisk(self, args, stdin=None):
        if '-l' in args:
            disk = psutil.disk_usage('/')
            size_gb = disk.total / (1024**3)
            return f"""Disk /dev/sda: {size_gb:.2f} GiB, {disk.total} bytes, {disk.total // 512} sectors
Disk model: Virtual Disk
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: gpt
Disk identifier: ABCD1234-5678-90AB-CDEF-123456789ABC

Device     Start       End   Sectors  Size Type
/dev/sda1   2048 {disk.total // 512 - 2097152}  {disk.total // 512 - 2099200}  {size_gb - 1:.1f}G Linux filesystem
/dev/sda2  {disk.total // 512 - 2097152} {disk.total // 512 - 1} 2097152    1G Linux swap
"""
        return "fdisk: interactive mode not supported\n"

    def cmd_mount(self, args, stdin=None):
        if not args:
            output = ""
            for mount_point, info in self.system.filesystem.mounts.items():
                output += f"{info['device']} on {mount_point} type {info['fstype']} ({info['options']})\n"
            return output
        return "mount: operation not supported in this environment\n"

    def cmd_umount(self, args, stdin=None):
        return "umount: operation not supported in this environment\n"

    def cmd_dmesg(self, args, stdin=None):
        return self.system.kernel.get_dmesg() + '\n'

    def cmd_lsmod(self, args, stdin=None):
        output = "Module                  Size  Used by\n"
        for mod in self.system.kernel.modules:
            size = random.randint(10000, 500000)
            output += f"{mod:<24}{size:>6}  0\n"
        return output

    def cmd_modinfo(self, args, stdin=None):
        if not args:
            return "modinfo: missing module name\n"
        
        mod = args[0]
        return f"""filename:       /lib/modules/6.1.0-pylinux/kernel/drivers/{mod}.ko
license:        GPL
description:    {mod} driver
author:         Linux Kernel
srcversion:     ABCDEF1234567890
depends:        
retpoline:      Y
intree:         Y
name:           {mod}
vermagic:       6.1.0-pylinux SMP preempt mod_unload modversions
"""

    def cmd_modprobe(self, args, stdin=None):
        if not args:
            return "modprobe: missing module name\n"
        
        remove = '-r' in args
        mod = [a for a in args if not a.startswith('-')]
        
        if mod:
            if remove:
                if mod[0] in self.system.kernel.modules:
                    self.system.kernel.modules.remove(mod[0])
            else:
                if mod[0] not in self.system.kernel.modules:
                    self.system.kernel.modules.append(mod[0])
        return ''

    def cmd_insmod(self, args, stdin=None):
        return self.cmd_modprobe(args, stdin)

    def cmd_rmmod(self, args, stdin=None):
        return self.cmd_modprobe(['-r'] + args, stdin)

    def cmd_date(self, args, stdin=None):
        if not args:
            return time.strftime('%a %b %d %H:%M:%S %Z %Y') + '\n'
        
        for i, arg in enumerate(args):
            if arg.startswith('+'):
                fmt = arg[1:]
                fmt = fmt.replace('%Y', time.strftime('%Y'))
                fmt = fmt.replace('%m', time.strftime('%m'))
                fmt = fmt.replace('%d', time.strftime('%d'))
                fmt = fmt.replace('%H', time.strftime('%H'))
                fmt = fmt.replace('%M', time.strftime('%M'))
                fmt = fmt.replace('%S', time.strftime('%S'))
                fmt = fmt.replace('%s', str(int(time.time())))
                fmt = fmt.replace('%Z', time.strftime('%Z'))
                fmt = fmt.replace('%z', time.strftime('%z'))
                fmt = fmt.replace('%A', time.strftime('%A'))
                fmt = fmt.replace('%a', time.strftime('%a'))
                fmt = fmt.replace('%B', time.strftime('%B'))
                fmt = fmt.replace('%b', time.strftime('%b'))
                fmt = fmt.replace('%c', time.strftime('%c'))
                fmt = fmt.replace('%x', time.strftime('%x'))
                fmt = fmt.replace('%X', time.strftime('%X'))
                fmt = fmt.replace('%j', time.strftime('%j'))
                fmt = fmt.replace('%U', time.strftime('%U'))
                fmt = fmt.replace('%W', time.strftime('%W'))
                fmt = fmt.replace('%w', time.strftime('%w'))
                fmt = fmt.replace('%n', '\n')
                fmt = fmt.replace('%t', '\t')
                return fmt + '\n'
            elif arg == '-u' or arg == '--utc':
                return time.strftime('%a %b %d %H:%M:%S UTC %Y', time.gmtime()) + '\n'
            elif arg == '-I' or arg == '--iso-8601':
                return time.strftime('%Y-%m-%d') + '\n'
            elif arg == '-R' or arg == '--rfc-email':
                return time.strftime('%a, %d %b %Y %H:%M:%S %z') + '\n'
        
        return time.strftime('%a %b %d %H:%M:%S %Z %Y') + '\n'

    def cmd_cal(self, args, stdin=None):
        import calendar
        
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        
        for i, arg in enumerate(args):
            if arg == '-y':
                return calendar.calendar(year)
            elif arg == '-m' and i + 1 < len(args):
                try:
                    month = int(args[i + 1])
                except:
                    pass
            elif arg.isdigit():
                if int(arg) > 12:
                    year = int(arg)
                else:
                    month = int(arg)
        
        return calendar.month(year, month)

    def cmd_timedatectl(self, args, stdin=None):
        return f"""               Local time: {time.strftime('%a %Y-%m-%d %H:%M:%S %Z')}
           Universal time: {time.strftime('%a %Y-%m-%d %H:%M:%S UTC', time.gmtime())}
                 RTC time: {time.strftime('%a %Y-%m-%d %H:%M:%S', time.gmtime())}
                Time zone: {time.strftime('%Z')} ({time.strftime('%z')})
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
"""

    def cmd_hwclock(self, args, stdin=None):
        return time.strftime('%Y-%m-%d %H:%M:%S.000000%z') + '\n'

    def cmd_sleep(self, args, stdin=None):
        if not args:
            return "sleep: missing operand\n"
        
        try:
            duration = float(args[0].rstrip('smhd'))
            suffix = args[0][-1] if args[0][-1] in 'smhd' else 's'
            
            if suffix == 'm':
                duration *= 60
            elif suffix == 'h':
                duration *= 3600
            elif suffix == 'd':
                duration *= 86400
            
            time.sleep(min(duration, 5))
        except:
            return f"sleep: invalid time interval '{args[0]}'\n"
        
        return ''

    def cmd_usleep(self, args, stdin=None):
        if args:
            try:
                time.sleep(int(args[0]) / 1000000)
            except:
                pass
        return ''

    def cmd_time(self, args, stdin=None):
        if not args:
            return ''
        
        start = time.time()
        output = self.execute(' '.join(args), None)
        elapsed = time.time() - start
        
        return output + f"\nreal\t0m{elapsed:.3f}s\nuser\t0m0.000s\nsys\t0m0.000s\n"

    def cmd_timeout(self, args, stdin=None):
        if len(args) < 2:
            return "timeout: missing operand\n"
        return ''

    def cmd_watch(self, args, stdin=None):
        return "watch: interactive mode not supported\n"

    def cmd_env(self, args, stdin=None):
        if not args:
            output = []
            for key, value in sorted(self.system.environment.items()):
                output.append(f"{key}={value}")
            return '\n'.join(output) + '\n'
        return ''

    def cmd_printenv(self, args, stdin=None):
        if args:
            values = []
            for arg in args:
                if arg in self.system.environment:
                    values.append(self.system.environment[arg])
            return '\n'.join(values) + '\n' if values else ''
        return self.cmd_env(args, stdin)

    def cmd_export(self, args, stdin=None):
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

    def cmd_set(self, args, stdin=None):
        if not args:
            output = []
            for key, value in sorted(self.system.environment.items()):
                output.append(f"{key}='{value}'")
            return '\n'.join(output) + '\n'
        return ''

    def cmd_unset(self, args, stdin=None):
        for arg in args:
            if arg in self.system.environment:
                del self.system.environment[arg]
        return ''

    def cmd_alias(self, args, stdin=None):
        if not args:
            output = []
            for name, value in sorted(self.system.aliases.items()):
                output.append(f"alias {name}='{value}'")
            return '\n'.join(output) + '\n'
        
        for arg in args:
            if '=' in arg:
                name, value = arg.split('=', 1)
                value = value.strip("'\"")
                self.system.aliases[name] = value
            else:
                if arg in self.system.aliases:
                    return f"alias {arg}='{self.system.aliases[arg]}'\n"
        return ''

    def cmd_unalias(self, args, stdin=None):
        for arg in args:
            if arg == '-a':
                self.system.aliases.clear()
            elif arg in self.system.aliases:
                del self.system.aliases[arg]
        return ''

    def cmd_source(self, args, stdin=None):
        if not args:
            return "source: missing file argument\n"
        
        content = self.system.filesystem.read_file(args[0])
        if content is None:
            return f"-bash: {args[0]}: No such file or directory\n"
        
        output = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                result = self.system.shell.execute(line)
                if result:
                    output.append(result.rstrip())
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_exec(self, args, stdin=None):
        if not args:
            return ''
        return f"exec: would replace shell with '{args[0]}'\n"

    def cmd_eval(self, args, stdin=None):
        if not args:
            return ''
        return self.system.shell.execute(' '.join(args))

    def cmd_history(self, args, stdin=None):
        output = []
        for i, cmd in enumerate(self.system.history, 1):
            output.append(f"  {i:>4}  {cmd}")
        return '\n'.join(output) + '\n' if output else ''

    def cmd_clear(self, args, stdin=None):
        return '\033[2J\033[H'

    def cmd_reset(self, args, stdin=None):
        return '\033c'

    def cmd_tput(self, args, stdin=None):
        if not args:
            return ''
        
        if args[0] == 'clear':
            return '\033[2J\033[H'
        elif args[0] == 'reset':
            return '\033c'
        elif args[0] == 'cols':
            return '80\n'
        elif args[0] == 'lines':
            return '24\n'
        elif args[0] == 'bold':
            return '\033[1m'
        elif args[0] == 'sgr0':
            return '\033[0m'
        
        return ''

    def cmd_stty(self, args, stdin=None):
        if not args or args[0] == '-a':
            return """speed 38400 baud; rows 24; columns 80; line = 0;
intr = ^C; quit = ^\\; erase = ^?; kill = ^U; eof = ^D; eol = <undef>;
eol2 = <undef>; swtch = <undef>; start = ^Q; stop = ^S; susp = ^Z;
-parenb -parodd -cmspar cs8 -hupcl -cstopb cread -clocal -crtscts
-ignbrk -brkint -ignpar -parmrk -inpck -istrip -inlcr -igncr icrnl ixon -ixoff
-iuclc -ixany -imaxbel -iutf8
opost -olcuc -ocrnl onlcr -onocr -onlret -ofill -ofdel nl0 cr0 tab0 bs0 vt0 ff0
isig icanon iexten echo echoe echok -echonl -noflsh -xcase -tostop -echoprt
"""
        return ''

    def cmd_tee(self, args, stdin=None):
        append = '-a' in args or '--append' in args
        files = [a for a in args if not a.startswith('-')]
        
        content = stdin or ''
        
        for f in files:
            self.system.filesystem.write_file(f, content, append=append)
        
        return content

    def cmd_xargs(self, args, stdin=None):
        if not stdin:
            return ''
        
        cmd = args if args else ['echo']
        items = stdin.split()
        
        full_cmd = ' '.join(cmd + items)
        return self.system.shell.execute(full_cmd)

    def cmd_yes(self, args, stdin=None):
        text = args[0] if args else 'y'
        return '\n'.join([text] * 10) + '\n'

    def cmd_true(self, args, stdin=None):
        self.system.last_exit_code = 0
        return ''

    def cmd_false(self, args, stdin=None):
        self.system.last_exit_code = 1
        return ''

    def cmd_test(self, args, stdin=None):
        if not args:
            self.system.last_exit_code = 1
            return ''
        
        if args[-1] == ']':
            args = args[:-1]
        
        if len(args) == 1:
            self.system.last_exit_code = 0 if args[0] else 1
        elif len(args) == 2:
            op = args[0]
            arg = args[1]
            
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
            elif op == '-r' or op == '-w' or op == '-x':
                self.system.last_exit_code = 0 if self.system.filesystem.exists(arg) else 1
            elif op == '-s':
                info = self.system.filesystem.get_file_info(self.system.filesystem.resolve_path(arg))
                self.system.last_exit_code = 0 if info and info['size'] > 0 else 1
            elif op == '!':
                self.cmd_test([arg], stdin)
                self.system.last_exit_code = 1 - self.system.last_exit_code
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
            elif op == '-le':
                try:
                    self.system.last_exit_code = 0 if int(left) <= int(right) else 1
                except:
                    self.system.last_exit_code = 1
            elif op == '-gt':
                try:
                    self.system.last_exit_code = 0 if int(left) > int(right) else 1
                except:
                    self.system.last_exit_code = 1
            elif op == '-ge':
                try:
                    self.system.last_exit_code = 0 if int(left) >= int(right) else 1
                except:
                    self.system.last_exit_code = 1
        
        return ''

    def cmd_expr(self, args, stdin=None):
        if not args:
            return ''
        
        expr_str = ' '.join(args)
        
        try:
            if '+' in args:
                idx = args.index('+')
                result = int(args[idx-1]) + int(args[idx+1])
            elif '-' in args:
                idx = args.index('-')
                result = int(args[idx-1]) - int(args[idx+1])
            elif '*' in args or 'x' in args:
                idx = args.index('*') if '*' in args else args.index('x')
                result = int(args[idx-1]) * int(args[idx+1])
            elif '/' in args:
                idx = args.index('/')
                result = int(args[idx-1]) // int(args[idx+1])
            elif '%' in args:
                idx = args.index('%')
                result = int(args[idx-1]) % int(args[idx+1])
            else:
                result = eval(expr_str)
            return str(result) + '\n'
        except:
            return '0\n'

    def cmd_bc(self, args, stdin=None):
        if stdin:
            try:
                lines = stdin.strip().split('\n')
                results = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        line = line.replace('^', '**')
                        result = eval(line)
                        results.append(str(result))
                return '\n'.join(results) + '\n'
            except:
                return '0\n'
        return ''

    def cmd_dc(self, args, stdin=None):
        return self.cmd_bc(args, stdin)

    def cmd_factor(self, args, stdin=None):
        output = []
        for arg in args:
            try:
                n = int(arg)
                factors = []
                d = 2
                while d * d <= n:
                    while n % d == 0:
                        factors.append(d)
                        n //= d
                    d += 1
                if n > 1:
                    factors.append(n)
                output.append(f"{arg}: {' '.join(map(str, factors))}")
            except:
                output.append(f"factor: '{arg}' is not a valid positive integer")
        return '\n'.join(output) + '\n' if output else ''

    def cmd_seq(self, args, stdin=None):
        if not args:
            return ''
        
        try:
            if len(args) == 1:
                end = int(args[0])
                return '\n'.join(map(str, range(1, end + 1))) + '\n'
            elif len(args) == 2:
                start = int(args[0])
                end = int(args[1])
                return '\n'.join(map(str, range(start, end + 1))) + '\n'
            elif len(args) >= 3:
                start = int(args[0])
                step = int(args[1])
                end = int(args[2])
                return '\n'.join(map(str, range(start, end + 1, step))) + '\n'
        except:
            pass
        return ''

    def cmd_shuf(self, args, stdin=None):
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        lines = content.strip().split('\n') if content.strip() else []
        random.shuffle(lines)
        return '\n'.join(lines) + '\n' if lines else ''

    def cmd_rev(self, args, stdin=None):
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        lines = content.split('\n')
        reversed_lines = [line[::-1] for line in lines]
        return '\n'.join(reversed_lines)

    def cmd_nl(self, args, stdin=None):
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        lines = content.split('\n')
        output = []
        for i, line in enumerate(lines, 1):
            if line.strip():
                output.append(f"{i:>6}\t{line}")
            else:
                output.append(line)
        
        return '\n'.join(output)

    def cmd_od(self, args, stdin=None):
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        output = []
        for i in range(0, len(content), 16):
            chunk = content[i:i+16]
            hex_vals = ' '.join(f'{ord(c):03o}' for c in chunk)
            output.append(f'{i:07o} {hex_vals}')
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_xxd(self, args, stdin=None):
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        output = []
        for i in range(0, len(content), 16):
            chunk = content[i:i+16]
            hex_vals = ' '.join(f'{ord(c):02x}' for c in chunk)
            ascii_vals = ''.join(c if 32 <= ord(c) < 127 else '.' for c in chunk)
            output.append(f'{i:08x}: {hex_vals:<48} {ascii_vals}')
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_hexdump(self, args, stdin=None):
        return self.cmd_xxd(args, stdin)

    def cmd_strings(self, args, stdin=None):
        min_len = 4
        files = []
        
        for arg in args:
            if arg.startswith('-n'):
                try:
                    min_len = int(arg[2:])
                except:
                    pass
            elif not arg.startswith('-'):
                files.append(arg)
        
        content = stdin or ''
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        output = []
        current = []
        for c in content:
            if 32 <= ord(c) < 127:
                current.append(c)
            else:
                if len(current) >= min_len:
                    output.append(''.join(current))
                current = []
        
        if len(current) >= min_len:
            output.append(''.join(current))
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_base64(self, args, stdin=None):
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

    def cmd_md5sum(self, args, stdin=None):
        output = []
        
        if stdin and not args:
            h = hashlib.md5(stdin.encode()).hexdigest()
            output.append(f"{h}  -")
        else:
            for f in args:
                if f.startswith('-'):
                    continue
                content = self.system.filesystem.read_file(f)
                if content is None:
                    output.append(f"md5sum: {f}: No such file or directory")
                else:
                    h = hashlib.md5(content.encode()).hexdigest()
                    output.append(f"{h}  {f}")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_sha1sum(self, args, stdin=None):
        output = []
        
        if stdin and not args:
            h = hashlib.sha1(stdin.encode()).hexdigest()
            output.append(f"{h}  -")
        else:
            for f in args:
                if f.startswith('-'):
                    continue
                content = self.system.filesystem.read_file(f)
                if content is None:
                    output.append(f"sha1sum: {f}: No such file or directory")
                else:
                    h = hashlib.sha1(content.encode()).hexdigest()
                    output.append(f"{h}  {f}")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_sha256sum(self, args, stdin=None):
        output = []
        
        if stdin and not args:
            h = hashlib.sha256(stdin.encode()).hexdigest()
            output.append(f"{h}  -")
        else:
            for f in args:
                if f.startswith('-'):
                    continue
                content = self.system.filesystem.read_file(f)
                if content is None:
                    output.append(f"sha256sum: {f}: No such file or directory")
                else:
                    h = hashlib.sha256(content.encode()).hexdigest()
                    output.append(f"{h}  {f}")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_sha512sum(self, args, stdin=None):
        output = []
        
        if stdin and not args:
            h = hashlib.sha512(stdin.encode()).hexdigest()
            output.append(f"{h}  -")
        else:
            for f in args:
                if f.startswith('-'):
                    continue
                content = self.system.filesystem.read_file(f)
                if content is None:
                    output.append(f"sha512sum: {f}: No such file or directory")
                else:
                    h = hashlib.sha512(content.encode()).hexdigest()
                    output.append(f"{h}  {f}")
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_sum(self, args, stdin=None):
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''

              checksum = sum(ord(c) for c in content) % 65536
        blocks = (len(content) + 511) // 512
        
        return f"{checksum:>5} {blocks:>5}\n"

    def cmd_cksum(self, args, stdin=None):
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        import binascii
        crc = binascii.crc32(content.encode()) & 0xffffffff
        
        return f"{crc} {len(content)}\n"

    def cmd_ifconfig(self, args, stdin=None):
        return self.system.network_manager.ifconfig(args)

    def cmd_ip(self, args, stdin=None):
        return self.system.network_manager.ip_command(args)

    def cmd_ping(self, args, stdin=None):
        count = 4
        host = None
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-c' and i + 1 < len(args):
                try:
                    count = int(args[i + 1])
                except:
                    pass
                i += 1
            elif not arg.startswith('-'):
                host = arg
            i += 1
        
        if not host:
            return "ping: missing host operand\n"
        
        return self.system.network_manager.ping(host, count)

    def cmd_traceroute(self, args, stdin=None):
        host = None
        for arg in args:
            if not arg.startswith('-'):
                host = arg
                break
        
        if not host:
            return "traceroute: missing host operand\n"
        
        return self.system.network_manager.traceroute(host)

    def cmd_tracepath(self, args, stdin=None):
        return self.cmd_traceroute(args, stdin)

    def cmd_netstat(self, args, stdin=None):
        return self.system.network_manager.netstat(args)

    def cmd_ss(self, args, stdin=None):
        return self.system.network_manager.ss(args)

    def cmd_route(self, args, stdin=None):
        return self.system.network_manager.route(args)

    def cmd_arp(self, args, stdin=None):
        return self.system.network_manager.arp(args)

    def cmd_nslookup(self, args, stdin=None):
        if not args:
            return "nslookup: missing host operand\n"
        
        return self.system.network_manager.nslookup(args[0])

    def cmd_dig(self, args, stdin=None):
        if not args:
            return "dig: missing host operand\n"
        
        return self.system.network_manager.dig(args[0])

    def cmd_host(self, args, stdin=None):
        if not args:
            return "host: missing host operand\n"
        
        return self.system.network_manager.host(args[0])

    def cmd_curl(self, args, stdin=None):
        url = None
        output_file = None
        silent = False
        headers_only = False
        include_headers = False
        method = 'GET'
        data = None
        headers = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-o' and i + 1 < len(args):
                output_file = args[i + 1]
                i += 1
            elif arg == '-s' or arg == '--silent':
                silent = True
            elif arg == '-I' or arg == '--head':
                headers_only = True
            elif arg == '-i' or arg == '--include':
                include_headers = True
            elif arg == '-X' and i + 1 < len(args):
                method = args[i + 1]
                i += 1
            elif arg == '-d' and i + 1 < len(args):
                data = args[i + 1]
                method = 'POST'
                i += 1
            elif arg == '-H' and i + 1 < len(args):
                headers.append(args[i + 1])
                i += 1
            elif not arg.startswith('-'):
                url = arg
            i += 1
        
        if not url:
            return "curl: missing URL\n"
        
        return self.system.network_manager.curl(url, method, data, headers, include_headers, headers_only)

    def cmd_wget(self, args, stdin=None):
        url = None
        output_file = None
        quiet = False
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-O' and i + 1 < len(args):
                output_file = args[i + 1]
                i += 1
            elif arg == '-q' or arg == '--quiet':
                quiet = True
            elif not arg.startswith('-'):
                url = arg
            i += 1
        
        if not url:
            return "wget: missing URL\n"
        
        return self.system.network_manager.wget(url, output_file, quiet)

    def cmd_nc(self, args, stdin=None):
        return "nc: connection handling not supported in this environment\n"

    def cmd_telnet(self, args, stdin=None):
        if not args:
            return "telnet: missing host operand\n"
        return f"Trying {args[0]}...\ntelnet: connection not supported in this environment\n"

    def cmd_ftp(self, args, stdin=None):
        return "ftp: connection not supported in this environment\n"

    def cmd_ssh(self, args, stdin=None):
        if not args:
            return "usage: ssh [-l login_name] hostname\n"
        return f"ssh: connect to host {args[-1]}: Connection not supported in this environment\n"

    def cmd_scp(self, args, stdin=None):
        return "scp: connection not supported in this environment\n"

    def cmd_sftp(self, args, stdin=None):
        return "sftp: connection not supported in this environment\n"

    def cmd_rsync(self, args, stdin=None):
        return "rsync: connection not supported in this environment\n"

    def cmd_useradd(self, args, stdin=None):
        if not args:
            return "useradd: missing username\n"
        
        username = None
        home = None
        shell = '/bin/bash'
        groups = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-m' or arg == '--create-home':
                pass
            elif arg == '-d' and i + 1 < len(args):
                home = args[i + 1]
                i += 1
            elif arg == '-s' and i + 1 < len(args):
                shell = args[i + 1]
                i += 1
            elif arg == '-G' and i + 1 < len(args):
                groups = args[i + 1].split(',')
                i += 1
            elif not arg.startswith('-'):
                username = arg
            i += 1
        
        if not username:
            return "useradd: missing username\n"
        
        return self.system.user_manager.add_user(username, home, shell, groups)

    def cmd_userdel(self, args, stdin=None):
        if not args:
            return "userdel: missing username\n"
        
        remove_home = '-r' in args
        username = [a for a in args if not a.startswith('-')]
        
        if username:
            return self.system.user_manager.del_user(username[0], remove_home)
        return "userdel: missing username\n"

    def cmd_usermod(self, args, stdin=None):
        if len(args) < 2:
            return "usermod: missing arguments\n"
        
        return f"usermod: user modified\n"

    def cmd_groupadd(self, args, stdin=None):
        if not args:
            return "groupadd: missing group name\n"
        
        groupname = [a for a in args if not a.startswith('-')]
        if groupname:
            return self.system.user_manager.add_group(groupname[0])
        return "groupadd: missing group name\n"

    def cmd_groupdel(self, args, stdin=None):
        if not args:
            return "groupdel: missing group name\n"
        
        return self.system.user_manager.del_group(args[0])

    def cmd_groupmod(self, args, stdin=None):
        return "groupmod: group modified\n"

    def cmd_passwd(self, args, stdin=None):
        username = args[0] if args else (self.system.current_user or 'root')
        return f"passwd: password for {username} updated successfully\n"

    def cmd_chpasswd(self, args, stdin=None):
        return "chpasswd: passwords updated\n"

    def cmd_su(self, args, stdin=None):
        user = 'root'
        login_shell = False
        
        for arg in args:
            if arg == '-' or arg == '-l' or arg == '--login':
                login_shell = True
            elif not arg.startswith('-'):
                user = arg
        
        self.system.current_user = user
        self.system.environment['USER'] = user
        self.system.environment['LOGNAME'] = user
        
        if user == 'root':
            self.system.environment['HOME'] = '/root'
        else:
            self.system.environment['HOME'] = f'/home/{user}'
        
        if login_shell:
            self.system.filesystem.cwd = self.system.environment['HOME']
        
        return ''

    def cmd_sudo(self, args, stdin=None):
        if not args:
            return "usage: sudo command\n"
        
        if args[0] == '-i':
            self.system.current_user = 'root'
            self.system.environment['USER'] = 'root'
            self.system.environment['HOME'] = '/root'
            self.system.filesystem.cwd = '/root'
            return ''
        elif args[0] == '-u' and len(args) > 2:
            user = args[1]
            command = ' '.join(args[2:])
            return self.system.shell.execute(command)
        
        command = ' '.join(args)
        return self.system.shell.execute(command)

    def cmd_visudo(self, args, stdin=None):
        return "visudo: editor not available in this environment\n"

    def cmd_newgrp(self, args, stdin=None):
        if args:
            return f"newgrp: group changed to {args[0]}\n"
        return ''

    def cmd_login(self, args, stdin=None):
        return "login: interactive login not supported\n"

    def cmd_logout(self, args, stdin=None):
        return "logout: not login shell: use `exit'\n"

    def cmd_exit(self, args, stdin=None):
        code = 0
        if args:
            try:
                code = int(args[0])
            except:
                pass
        return f"exit {code}\n"

    def cmd_systemctl(self, args, stdin=None):
        return self.system.systemd.systemctl(args)

    def cmd_service(self, args, stdin=None):
        if len(args) < 2:
            return "Usage: service <service> <action>\n"
        
        service = args[0]
        action = args[1]
        
        return self.system.systemd.systemctl([action, service])

    def cmd_journalctl(self, args, stdin=None):
        return self.system.systemd.journalctl(args)

    def cmd_init(self, args, stdin=None):
        if args:
            try:
                level = int(args[0])
                return f"Switching to runlevel {level}\n"
            except:
                pass
        return "init: invalid runlevel\n"

    def cmd_telinit(self, args, stdin=None):
        return self.cmd_init(args, stdin)

    def cmd_runlevel(self, args, stdin=None):
        return f"N {self.system.runlevel}\n"

    def cmd_shutdown(self, args, stdin=None):
        return "shutdown\n"

    def cmd_reboot(self, args, stdin=None):
        return "reboot\n"

    def cmd_poweroff(self, args, stdin=None):
        return "poweroff\n"

    def cmd_halt(self, args, stdin=None):
        return "halt\n"

    def cmd_apt(self, args, stdin=None):
        return self.system.package_manager.apt(args)

    def cmd_apt_get(self, args, stdin=None):
        return self.system.package_manager.apt_get(args)

    def cmd_apt_cache(self, args, stdin=None):
        return self.system.package_manager.apt_cache(args)

    def cmd_dpkg(self, args, stdin=None):
        return self.system.package_manager.dpkg(args)

    def cmd_man(self, args, stdin=None):
        if not args:
            return "What manual page do you want?\n"
        
        cmd = args[0]
        
        man_pages = {
            'ls': '''LS(1)                            User Commands                           LS(1)

NAME
       ls - list directory contents

SYNOPSIS
       ls [OPTION]... [FILE]...

DESCRIPTION
       List information about the FILEs (the current directory by default).

       -a, --all
              do not ignore entries starting with .

       -l     use a long listing format

       -h, --human-readable
              with -l, print sizes like 1K 234M 2G etc.

       -R, --recursive
              list subdirectories recursively

       -r, --reverse
              reverse order while sorting

       -S     sort by file size, largest first

       -t     sort by time, newest first

SEE ALSO
       dir(1), find(1)
''',
            'cat': '''CAT(1)                           User Commands                          CAT(1)

NAME
       cat - concatenate files and print on the standard output

SYNOPSIS
       cat [OPTION]... [FILE]...

DESCRIPTION
       Concatenate FILE(s) to standard output.

       -n, --number
              number all output lines

       -E, --show-ends
              display $ at end of each line

       -T, --show-tabs
              display TAB characters as ^I

SEE ALSO
       tac(1), head(1), tail(1)
''',
            'grep': '''GREP(1)                          User Commands                         GREP(1)

NAME
       grep - print lines that match patterns

SYNOPSIS
       grep [OPTION...] PATTERNS [FILE...]

DESCRIPTION
       grep searches for PATTERNS in each FILE.

       -i, --ignore-case
              ignore case distinctions

       -v, --invert-match
              select non-matching lines

       -c, --count
              print only a count of selected lines per FILE

       -n, --line-number
              prefix each line of output with the 1-based line number

       -r, -R, --recursive
              read all files under each directory, recursively

       -E, --extended-regexp
              PATTERNS are extended regular expressions

SEE ALSO
       egrep(1), fgrep(1), sed(1), awk(1)
'''
        }
        
        if cmd in man_pages:
            return man_pages[cmd]
        
        return f"""
{cmd.upper()}(1)                          User Commands                         {cmd.upper()}(1)

NAME
       {cmd} - {cmd} command

SYNOPSIS
       {cmd} [OPTION]... [ARG]...

DESCRIPTION
       This is the manual page for the {cmd} command.
       
       For more information, consult the system documentation.

SEE ALSO
       info {cmd}

"""

    def cmd_info(self, args, stdin=None):
        if not args:
            return "info: missing argument\n"
        return f"info: no info entry for {args[0]}\n"

    def cmd_help(self, args, stdin=None):
        if not args:
            return """GNU bash, version 5.1.0

These shell commands are defined internally.  Type 'help' to see this list.
Type 'help name' to find out more about the function 'name'.

 alias      bg         cd         echo       eval       exec       exit
 export     fg         hash       help       history    jobs       kill
 pwd        read       return     set        shift      source     test
 times      trap       type       ulimit     umask      unalias    unset
 wait

"""
        
        cmd = args[0]
        help_texts = {
            'cd': 'cd: cd [-L|[-P [-e]] [-@]] [dir]\n    Change the shell working directory.',
            'pwd': 'pwd: pwd [-LP]\n    Print the name of the current working directory.',
            'echo': 'echo: echo [-neE] [arg ...]\n    Write arguments to the standard output.',
            'export': 'export: export [-fn] [name[=value] ...]\n    Set export attribute for shell variables.',
            'alias': 'alias: alias [-p] [name[=value] ... ]\n    Define or display aliases.',
            'history': 'history: history [-c] [-d offset] [n]\n    Display or manipulate the history list.',
            'exit': 'exit: exit [n]\n    Exit the shell.',
            'type': 'type: type [-afptP] name [name ...]\n    Display information about command type.',
            'source': 'source: source filename [arguments]\n    Execute commands from a file in the current shell.',
            'test': 'test: test [expr]\n    Evaluate conditional expression.',
            'kill': 'kill: kill [-s sigspec | -n signum | -sigspec] pid | jobspec ...\n    Send a signal to a job.'
        }
        
        return help_texts.get(cmd, f"-bash: help: no help topics match '{cmd}'\n") + '\n'

    def cmd_whatis(self, args, stdin=None):
        if not args:
            return "whatis: missing argument\n"
        
        descriptions = {
            'ls': 'ls (1)               - list directory contents',
            'cat': 'cat (1)              - concatenate files and print on the standard output',
            'grep': 'grep (1)             - print lines that match patterns',
            'find': 'find (1)             - search for files in a directory hierarchy',
            'ps': 'ps (1)               - report a snapshot of the current processes',
            'kill': 'kill (1)             - send a signal to a process',
            'man': 'man (1)              - an interface to the system reference manuals'
        }
        
        output = []
        for arg in args:
            if arg in descriptions:
                output.append(descriptions[arg])
            else:
                output.append(f"{arg}: nothing appropriate.")
        
        return '\n'.join(output) + '\n'

    def cmd_apropos(self, args, stdin=None):
        if not args:
            return "apropos: missing argument\n"
        
        keyword = args[0].lower()
        
        results = {
            'file': ['cat (1) - concatenate files', 'cp (1) - copy files', 'mv (1) - move files', 'rm (1) - remove files', 'find (1) - search for files'],
            'directory': ['ls (1) - list directory contents', 'mkdir (1) - make directories', 'rmdir (1) - remove directories', 'cd (1) - change directory'],
            'process': ['ps (1) - report process status', 'kill (1) - terminate processes', 'top (1) - display processes'],
            'network': ['ping (1) - send ICMP ECHO_REQUEST', 'netstat (1) - network statistics', 'ifconfig (1) - configure network']
        }
        
        output = []
        for key, entries in results.items():
            if keyword in key:
                output.extend(entries)
        
        if output:
            return '\n'.join(output) + '\n'
        return f"{keyword}: nothing appropriate.\n"

    def cmd_less(self, args, stdin=None):
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        return content

    def cmd_more(self, args, stdin=None):
        return self.cmd_less(args, stdin)

    def cmd_nano(self, args, stdin=None):
        return "nano: terminal-based editor not available in this environment\nUse 'echo \"content\" > file' or 'cat > file' to create files.\n"

    def cmd_vi(self, args, stdin=None):
        return "vi: terminal-based editor not available in this environment\nUse 'echo \"content\" > file' or 'cat > file' to create files.\n"

    def cmd_vim(self, args, stdin=None):
        return self.cmd_vi(args, stdin)

    def cmd_view(self, args, stdin=None):
        return self.cmd_less(args, stdin)

    def cmd_ed(self, args, stdin=None):
        return "ed: line editor not available in this environment\n"

    def cmd_crontab(self, args, stdin=None):
        if '-l' in args:
            return "no crontab for root\n"
        elif '-e' in args:
            return "crontab: editor not available\n"
        elif '-r' in args:
            return "crontab: crontab removed\n"
        return "crontab: usage error\n"

    def cmd_at(self, args, stdin=None):
        return "at: scheduling not available in this environment\n"

    def cmd_batch(self, args, stdin=None):
        return "batch: scheduling not available in this environment\n"

    def cmd_iptables(self, args, stdin=None):
        if '-L' in args or '--list' in args:
            return """Chain INPUT (policy ACCEPT)
target     prot opt source               destination         

Chain FORWARD (policy ACCEPT)
target     prot opt source               destination         

Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination         
"""
        return "iptables: firewall management simulated\n"

    def cmd_ip6tables(self, args, stdin=None):
        return self.cmd_iptables(args, stdin)

    def cmd_ufw(self, args, stdin=None):
        if not args:
            return "ufw: missing command\n"
        
        if args[0] == 'status':
            return "Status: inactive\n"
        elif args[0] == 'enable':
            return "Firewall is active and enabled on system startup\n"
        elif args[0] == 'disable':
            return "Firewall stopped and disabled on system startup\n"
        
        return "ufw: command executed\n"

    def cmd_dd(self, args, stdin=None):
        count = 1
        bs = 512
        input_file = '/dev/zero'
        output_file = None
        
        for arg in args:
            if arg.startswith('if='):
                input_file = arg[3:]
            elif arg.startswith('of='):
                output_file = arg[3:]
            elif arg.startswith('bs='):
                try:
                    bs_str = arg[3:]
                    if bs_str.endswith('K'):
                        bs = int(bs_str[:-1]) * 1024
                    elif bs_str.endswith('M'):
                        bs = int(bs_str[:-1]) * 1024 * 1024
                    else:
                        bs = int(bs_str)
                except:
                    pass
            elif arg.startswith('count='):
                try:
                    count = int(arg[6:])
                except:
                    pass
        
        total_bytes = bs * count
        
        return f"""{count}+0 records in
{count}+0 records out
{total_bytes} bytes ({total_bytes / 1024:.1f} KB) copied, 0.001 s, {total_bytes / 1000:.1f} kB/s
"""

    def cmd_sync(self, args, stdin=None):
        return ''

    def cmd_mktemp(self, args, stdin=None):
        import random
        import string
        
        directory = '-d' in args
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        if directory:
            path = f"/tmp/tmp.{suffix}"
            self.system.filesystem.mkdir(path)
        else:
            path = f"/tmp/tmp.{suffix}"
            self.system.filesystem.write_file(path, '')
        
        return path + '\n'

    def cmd_mkfifo(self, args, stdin=None):
        files = [a for a in args if not a.startswith('-')]
        for f in files:
            self.system.filesystem.write_file(f, '')
        return ''

    def cmd_mknod(self, args, stdin=None):
        return "mknod: device creation not supported\n"

    def cmd_split(self, args, stdin=None):
        return "split: file splitting simulated\n"

    def cmd_csplit(self, args, stdin=None):
        return "csplit: context splitting simulated\n"

    def cmd_join(self, args, stdin=None):
        files = [a for a in args if not a.startswith('-')]
        if len(files) < 2:
            return "join: missing file operand\n"
        
        content1 = self.system.filesystem.read_file(files[0]) or ''
        content2 = self.system.filesystem.read_file(files[1]) or ''
        
        return content1 + content2

    def cmd_paste(self, args, stdin=None):
        delimiter = '\t'
        files = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-d' and i + 1 < len(args):
                delimiter = args[i + 1]
                i += 1
            elif not arg.startswith('-'):
                files.append(arg)
            i += 1
        
        if not files:
            return stdin or ''
        
        contents = []
        for f in files:
            content = self.system.filesystem.read_file(f) or ''
            contents.append(content.strip().split('\n'))
        
        max_lines = max(len(c) for c in contents) if contents else 0
        output = []
        
        for i in range(max_lines):
            parts = []
            for c in contents:
                parts.append(c[i] if i < len(c) else '')
            output.append(delimiter.join(parts))
        
        return '\n'.join(output) + '\n' if output else ''

    def cmd_expand(self, args, stdin=None):
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        return content.replace('\t', '        ')

    def cmd_unexpand(self, args, stdin=None):
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        return content.replace('        ', '\t')

    def cmd_fold(self, args, stdin=None):
        width = 80
        content = stdin or ''
        
        for i, arg in enumerate(args):
            if arg == '-w' and i + 1 < len(args):
                try:
                    width = int(args[i + 1])
                except:
                    pass
            elif not arg.startswith('-'):
                content = self.system.filesystem.read_file(arg) or content
        
        output = []
        for line in content.split('\n'):
            while len(line) > width:
                output.append(line[:width])
                line = line[width:]
            output.append(line)
        
        return '\n'.join(output)

    def cmd_fmt(self, args, stdin=None):
        return self.cmd_fold(args, stdin)

    def cmd_pr(self, args, stdin=None):
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        header = f"\n\n{time.strftime('%Y-%m-%d %H:%M')}  Page 1\n\n\n"
        return header + content

    def cmd_column(self, args, stdin=None):
        content = stdin or ''
        files = [a for a in args if not a.startswith('-')]
        
        if files:
            content = self.system.filesystem.read_file(files[0]) or ''
        
        table = '-t' in args
        
        if table:
            lines = content.strip().split('\n')
            if lines:
                cols = [line.split() for line in lines]
                widths = []
                for col_idx in range(max(len(row) for row in cols)):
                    width = max(len(row[col_idx]) if col_idx < len(row) else 0 for row in cols)
                    widths.append(width)
                
                output = []
                for row in cols:
                    formatted = []
                    for i, cell in enumerate(row):
                        if i < len(widths):
                            formatted.append(cell.ljust(widths[i]))
                        else:
                            formatted.append(cell)
                    output.append('  '.join(formatted))
                
                return '\n'.join(output) + '\n'
        
        return content

    def cmd_colrm(self, args, stdin=None):
        start = int(args[0]) if args else 1
        end = int(args[1]) if len(args) > 1 else None
        
        content = stdin or ''
        output = []
        
        for line in content.split('\n'):
            if end:
                output.append(line[:start-1] + line[end:])
            else:
                output.append(line[:start-1])
        
        return '\n'.join(output)

    def cmd_logger(self, args, stdin=None):
        message = ' '.join(args)
        return f"Logged: {message}\n" if '-s' in args else ''

    def cmd_lsof(self, args, stdin=None):
        output = """COMMAND     PID   USER   FD      TYPE    DEVICE SIZE/OFF       NODE NAME
systemd       1   root  cwd       DIR       8,1     4096          2 /
systemd       1   root  rtd       DIR       8,1     4096          2 /
systemd       1   root  txt       REG       8,1   1620224     131073 /lib/systemd/systemd
systemd       1   root  mem       REG       8,1   1369352     131332 /lib/x86_64-linux-gnu/libm-2.31.so
bash        109   root  cwd       DIR       8,1     4096     262145 /root
bash        109   root  rtd       DIR       8,1     4096          2 /
bash        109   root    0u      CHR     136,1      0t0          4 /dev/pts/1
bash        109   root    1u      CHR     136,1      0t0          4 /dev/pts/1
bash        109   root    2u      CHR     136,1      0t0          4 /dev/pts/1
"""
        return output

    def cmd_fuser(self, args, stdin=None):
        if not args:
            return "fuser: missing file argument\n"
        return f"{args[0]}:               109\n"

    def cmd_pstree(self, args, stdin=None):
        return """systemd─┬─agetty
        ├─cron
        ├─dbus-daemon
        ├─login───bash───pstree
        ├─rsyslogd
        ├─sshd
        ├─systemd-journal
        ├─systemd-logind
        └─systemd-udevd
"""

    def cmd_chroot(self, args, stdin=None):
        if not args:
            return "chroot: missing operand\n"
        return f"chroot: cannot change root directory to '{args[0]}': Operation not permitted\n"

    def cmd_nologin(self, args, stdin=None):
        return "This account is currently not available.\n"

    def cmd_getent(self, args, stdin=None):
        if len(args) < 1:
            return "getent: missing database argument\n"
        
        database = args[0]
        key = args[1] if len(args) > 1 else None
        
        if database == 'passwd':
            content = self.system.filesystem.read_file('/etc/passwd') or ''
            if key:
                for line in content.split('\n'):
                    if line.startswith(f"{key}:"):
                        return line + '\n'
                return ''
            return content
        elif database == 'group':
            content = self.system.filesystem.read_file('/etc/group') or ''
            if key:
                for line in content.split('\n'):
                    if line.startswith(f"{key}:"):
                        return line + '\n'
                return ''
            return content
        elif database == 'hosts':
            if key:
                if key == 'localhost':
                    return "127.0.0.1       localhost\n"
            return self.system.filesystem.read_file('/etc/hosts') or ''
        
        return f"getent: unknown database: {database}\n"

    def cmd_locale(self, args, stdin=None):
        if '-a' in args:
            return """C
C.UTF-8
POSIX
en_US.utf8
"""
        return """LANG=en_US.UTF-8
LANGUAGE=
LC_CTYPE="en_US.UTF-8"
LC_NUMERIC="en_US.UTF-8"
LC_TIME="en_US.UTF-8"
LC_COLLATE="en_US.UTF-8"
LC_MONETARY="en_US.UTF-8"
LC_MESSAGES="en_US.UTF-8"
LC_PAPER="en_US.UTF-8"
LC_NAME="en_US.UTF-8"
LC_ADDRESS="en_US.UTF-8"
LC_TELEPHONE="en_US.UTF-8"
LC_MEASUREMENT="en_US.UTF-8"
LC_IDENTIFICATION="en_US.UTF-8"
LC_ALL=
"""

    def cmd_iconv(self, args, stdin=None):
        return stdin or ''

    def cmd_uuid(self, args, stdin=None):
        return self.cmd_uuidgen(args, stdin)

    def cmd_uuidgen(self, args, stdin=None):
        import uuid
        return str(uuid.uuid4()) + '\n'

    def execute(self, cmd, args, stdin=None):
        if cmd in self.commands:
            try:
                return self.commands[cmd](args, stdin)
            except Exception as e:
                return f"-bash: {cmd}: {str(e)}\n"
        else:
            if self.system.filesystem.exists(f'/bin/{cmd}') or self.system.filesystem.exists(f'/usr/bin/{cmd}'):
                return f"{cmd}: command executed (simulated binary)\n"
            return f"-bash: {cmd}: command not found\n"
