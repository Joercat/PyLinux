import shlex
import re
import os
import glob as glob_module
from commands import CommandExecutor

class Shell:
    def __init__(self, system):
        self.system = system
        self.executor = CommandExecutor(system)
        self.interrupted = False
        self.last_command = ''
        self.pipe_buffer = None

    def execute(self, command_line):
        if not command_line.strip():
            return ''
        
        self.interrupted = False
        command_line = command_line.strip()
        
        for alias, expansion in self.system.aliases.items():
            if command_line == alias or command_line.startswith(alias + ' '):
                command_line = expansion + command_line[len(alias):]
                break
        
        command_line = self.expand_variables(command_line)
        command_line = self.expand_history(command_line)
        
        if '|' in command_line:
            return self.execute_pipeline(command_line)
        
        redirect_out = None
        redirect_in = None
        append_mode = False
        
        if '>>' in command_line:
            parts = command_line.split('>>')
            command_line = parts[0].strip()
            redirect_out = parts[1].strip()
            append_mode = True
        elif '>' in command_line:
            parts = command_line.split('>')
            command_line = parts[0].strip()
            redirect_out = parts[1].strip()
        
        if '<' in command_line:
            parts = command_line.split('<')
            command_line = parts[0].strip()
            redirect_in = parts[1].strip()
        
        background = False
        if command_line.endswith('&'):
            background = True
            command_line = command_line[:-1].strip()
        
        try:
            parts = shlex.split(command_line)
        except ValueError:
            parts = command_line.split()
        
        if not parts:
            return ''
        
        parts = self.expand_globs(parts)
        
        cmd = parts[0]
        args = parts[1:]
        
        stdin_content = None
        if redirect_in:
            content = self.system.filesystem.read_file(redirect_in)
            if content is None:
                return f"-bash: {redirect_in}: No such file or directory\n"
            stdin_content = content
        
        if self.pipe_buffer is not None:
            stdin_content = self.pipe_buffer
            self.pipe_buffer = None
        
        output = self.executor.execute(cmd, args, stdin=stdin_content)
        
        self.system.last_exit_code = 0 if not output.startswith('-bash:') else 1
        
        if redirect_out:
            self.system.filesystem.write_file(redirect_out, output, append=append_mode)
            return ''
        
        return output

    def execute_pipeline(self, command_line):
        commands = [cmd.strip() for cmd in command_line.split('|')]
        
        output = ''
        for i, cmd in enumerate(commands):
            if i > 0:
                self.pipe_buffer = output
            output = self.execute(cmd)
            if self.interrupted:
                break
        
        self.pipe_buffer = None
        return output

    def expand_variables(self, command_line):
        def replace_var(match):
            var_name = match.group(1) or match.group(2)
            
            if var_name == '?':
                return str(self.system.last_exit_code)
            elif var_name == '$':
                return str(os.getpid())
            elif var_name == '!':
                return str(os.getpid())
            elif var_name == '0':
                return 'bash'
            elif var_name == '#':
                return '0'
            elif var_name == '*' or var_name == '@':
                return ''
            elif var_name == 'HOME':
                return self.system.environment.get('HOME', '/root')
            elif var_name == 'PWD':
                return self.system.filesystem.cwd
            elif var_name == 'OLDPWD':
                return self.system.environment.get('OLDPWD', '')
            elif var_name == 'USER':
                return self.system.current_user or 'root'
            elif var_name == 'HOSTNAME':
                return self.system.hostname
            elif var_name == 'RANDOM':
                import random
                return str(random.randint(0, 32767))
            elif var_name == 'SECONDS':
                return str(int(self.system.get_uptime()))
            elif var_name == 'LINENO':
                return '1'
            
            return self.system.environment.get(var_name, '')
        
        result = re.sub(r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*|\?|\$|!|#|\*|@|[0-9])', replace_var, command_line)
        
        result = result.replace('~', self.system.environment.get('HOME', '/root'))
        
        return result

    def expand_history(self, command_line):
        if command_line == '!!':
            if self.system.history:
                return self.system.history[-1]
            return ''
        
        if command_line.startswith('!'):
            rest = command_line[1:]
            if rest.isdigit():
                idx = int(rest) - 1
                if 0 <= idx < len(self.system.history):
                    return self.system.history[idx]
            elif rest.startswith('-') and rest[1:].isdigit():
                idx = -int(rest[1:])
                if abs(idx) <= len(self.system.history):
                    return self.system.history[idx]
            else:
                for cmd in reversed(self.system.history):
                    if cmd.startswith(rest):
                        return cmd
        
        return command_line

    def expand_globs(self, parts):
        result = []
        for part in parts:
            if any(c in part for c in ['*', '?', '[']):
                base_path = self.system.filesystem.cwd
                matches = self._glob_match(base_path, part)
                if matches:
                    result.extend(sorted(matches))
                else:
                    result.append(part)
            else:
                result.append(part)
        return result

    def _glob_match(self, base_path, pattern):
        matches = []
        
        files = self.system.filesystem.list_dir(base_path)
        if files is None:
            return matches
        
        import fnmatch
        for f in files:
            if fnmatch.fnmatch(f, pattern):
                matches.append(f)
        
        return matches

    def tab_complete(self, partial):
        completions = []
        
        parts = partial.split()
        
        if not parts or (len(parts) == 1 and not partial.endswith(' ')):
            prefix = parts[0] if parts else ''
            
            builtins = ['cd', 'pwd', 'echo', 'export', 'alias', 'unalias', 'history', 
                       'exit', 'source', 'set', 'unset', 'type', 'help', 'jobs', 
                       'fg', 'bg', 'wait', 'kill', 'exec', 'eval', 'read', 'test',
                       'true', 'false', 'return', 'break', 'continue', 'shift',
                       'getopts', 'hash', 'ulimit', 'umask', 'times', 'trap',
                       'declare', 'local', 'readonly', 'let', 'pushd', 'popd', 'dirs']
            
            commands = ['ls', 'cat', 'grep', 'find', 'ps', 'top', 'kill', 'mkdir', 
                       'rm', 'cp', 'mv', 'touch', 'chmod', 'chown', 'df', 'du',
                       'free', 'uname', 'hostname', 'date', 'cal', 'uptime',
                       'whoami', 'id', 'who', 'w', 'last', 'head', 'tail', 'wc',
                       'sort', 'uniq', 'cut', 'tr', 'sed', 'awk', 'diff', 'tar',
                       'gzip', 'gunzip', 'zip', 'unzip', 'ifconfig', 'ip', 'ping',
                       'netstat', 'ss', 'curl', 'wget', 'ssh', 'scp', 'man',
                       'which', 'whereis', 'file', 'stat', 'ln', 'env', 'printenv',
                       'clear', 'reset', 'less', 'more', 'nano', 'vi', 'vim',
                       'apt', 'apt-get', 'dpkg', 'systemctl', 'service', 'journalctl',
                       'mount', 'umount', 'fdisk', 'lsblk', 'blkid', 'dmesg',
                       'lsmod', 'modprobe', 'useradd', 'userdel', 'passwd', 'su', 'sudo',
                       'shutdown', 'reboot', 'poweroff', 'halt', 'init']
            
            all_cmds = list(set(builtins + commands + list(self.system.aliases.keys())))
            
            for cmd in all_cmds:
                if cmd.startswith(prefix):
                    completions.append(cmd)
        else:
            path_part = parts[-1] if parts else ''
            
            if '/' in path_part:
                dir_path = '/'.join(path_part.split('/')[:-1]) or '/'
                prefix = path_part.split('/')[-1]
            else:
                dir_path = self.system.filesystem.cwd
                prefix = path_part
            
            resolved = self.system.filesystem.resolve_path(dir_path)
            files = self.system.filesystem.list_dir(resolved)
            
            if files:
                for f in files:
                    if f.startswith(prefix):
                        full_path = f"{dir_path}/{f}" if dir_path != '/' else f"/{f}"
                        if self.system.filesystem.is_dir(f"{resolved}/{f}"):
                            completions.append(f + '/')
                        else:
                            completions.append(f)
        
        return sorted(set(completions))

    def interrupt(self):
        self.interrupted = True
