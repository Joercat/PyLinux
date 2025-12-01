import os
import asyncio
import time
import uuid
from filesystem import VirtualFileSystem
from commands import CommandExecutor
from process_manager import ProcessManager
from user_manager import UserManager
from system_monitor import SystemMonitor

class TerminalSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.filesystem = VirtualFileSystem()
        self.process_manager = ProcessManager()
        self.user_manager = UserManager()
        self.system_monitor = SystemMonitor()
        self.command_executor = CommandExecutor(self)
        
        self.env = {
            "USER": "user",
            "HOME": "/home/user",
            "PWD": "/home/user",
            "SHELL": "/bin/bash",
            "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "TERM": "xterm-256color",
            "LANG": "en_US.UTF-8",
            "HOSTNAME": "pylinux",
            "LOGNAME": "user",
            "EDITOR": "nano",
            "VISUAL": "nano",
            "PAGER": "less",
            "PS1": "\\u@\\h:\\w\\$ ",
            "PS2": "> ",
            "HISTSIZE": "1000",
            "HISTFILESIZE": "2000",
            "UID": "1000",
            "EUID": "1000",
            "PPID": "1",
            "SHLVL": "1",
            "OLDPWD": "/home/user",
            "MAIL": "/var/mail/user",
            "TMPDIR": "/tmp",
            "XDG_RUNTIME_DIR": "/run/user/1000",
            "XDG_SESSION_TYPE": "tty",
            "COLUMNS": "80",
            "LINES": "24"
        }
        
        self.cwd = "/home/user"
        self.history = []
        self.history_index = 0
        self.aliases = {
            "ll": "ls -la",
            "la": "ls -A",
            "l": "ls -CF",
            "..": "cd ..",
            "...": "cd ../..",
            "cls": "clear",
            "md": "mkdir",
            "rd": "rmdir",
            "grep": "grep --color=auto",
            "egrep": "egrep --color=auto",
            "fgrep": "fgrep --color=auto",
            "diff": "diff --color=auto"
        }
        
        self.is_root = False
        self.current_user = "user"
        self.current_uid = 1000
        self.current_gid = 1000
        self.umask = 0o022
        self.cols = 80
        self.rows = 24
        self.last_exit_code = 0
        self.background_jobs = []
        self.job_counter = 0
        self.start_time = time.time()
        self.login_time = time.time()
        self.last_command_time = None
        self.interrupted = False
        
        self.filesystem.initialize_default_structure()
    
    def get_prompt(self):
        if self.is_root:
            user = "root"
            prompt_char = "#"
        else:
            user = self.current_user
            prompt_char = "$"
        
        home = self.env.get("HOME", "/home/user")
        display_path = self.cwd
        if self.cwd.startswith(home):
            display_path = "~" + self.cwd[len(home):]
        
        hostname = self.env.get("HOSTNAME", "pylinux")
        
        return f"\033[1;32m{user}@{hostname}\033[0m:\033[1;34m{display_path}\033[0m{prompt_char} "
    
    def add_to_history(self, command: str):
        if command.strip() and (not self.history or self.history[-1] != command):
            self.history.append(command)
            max_history = int(self.env.get("HISTSIZE", "1000"))
            if len(self.history) > max_history:
                self.history = self.history[-max_history:]
        self.history_index = len(self.history)
    
    def expand_aliases(self, command: str) -> str:
        parts = command.split()
        if parts and parts[0] in self.aliases:
            parts[0] = self.aliases[parts[0]]
            return " ".join(parts)
        return command
    
    def expand_variables(self, command: str) -> str:
        import re
        
        def replace_var(match):
            var_name = match.group(1) or match.group(2)
            if var_name == "?":
                return str(self.last_exit_code)
            elif var_name == "$":
                return str(os.getpid())
            elif var_name == "!":
                if self.background_jobs:
                    return str(self.background_jobs[-1].get("pid", ""))
                return ""
            elif var_name == "#":
                return "0"
            elif var_name == "0":
                return "bash"
            elif var_name == "RANDOM":
                import random
                return str(random.randint(0, 32767))
            elif var_name == "SECONDS":
                return str(int(time.time() - self.start_time))
            elif var_name == "LINENO":
                return "1"
            return self.env.get(var_name, "")
        
        command = re.sub(r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*|[?$!#0-9]|RANDOM|SECONDS|LINENO)', replace_var, command)
        
        command = command.replace("~", self.env.get("HOME", "/home/user"))
        
        return command
    
    def expand_glob(self, pattern: str) -> list:
        import fnmatch
        
        if not any(c in pattern for c in "*?[]"):
            return [pattern]
        
        if pattern.startswith("/"):
            base_path = "/"
            pattern = pattern[1:]
        else:
            base_path = self.cwd
        
        parts = pattern.split("/")
        results = [base_path]
        
        for part in parts:
            new_results = []
            for path in results:
                if any(c in part for c in "*?[]"):
                    entries = self.filesystem.list_directory(path)
                    if entries:
                        for entry in entries:
                            if fnmatch.fnmatch(entry["name"], part):
                                new_path = os.path.join(path, entry["name"])
                                new_results.append(new_path)
                else:
                    new_path = os.path.join(path, part)
                    if self.filesystem.exists(new_path):
                        new_results.append(new_path)
            results = new_results if new_results else [pattern]
        
        return results if results else [pattern]
    
    async def execute(self, command: str) -> dict:
        self.last_command_time = time.time()
        self.interrupted = False
        
        command = command.strip()
        
        if not command:
            return {"output": [], "exit_code": 0}
        
        if command.startswith("#"):
            return {"output": [], "exit_code": 0}
        
        commands = self.parse_command_chain(command)
        
        final_output = []
        pipe_input = None
        
        for cmd_info in commands:
            if self.interrupted:
                final_output.append("^C")
                break
            
            cmd = cmd_info["command"]
            operator = cmd_info.get("operator")
            
            cmd = self.expand_aliases(cmd)
            cmd = self.expand_variables(cmd)
            
            result = await self.command_executor.execute(cmd, pipe_input)
            
            if result.get("type") == "shutdown":
                return result
            
            output = result.get("output", [])
            exit_code = result.get("exit_code", 0)
            self.last_exit_code = exit_code
            
            if cmd_info.get("pipe_to"):
                pipe_input = "\n".join(output) if output else ""
            else:
                final_output.extend(output)
                pipe_input = None
            
            if operator == "&&" and exit_code != 0:
                break
            elif operator == "||" and exit_code == 0:
                break
        
        return {"output": final_output, "exit_code": self.last_exit_code}
    
    def parse_command_chain(self, command: str) -> list:
        commands = []
        current = ""
        i = 0
        in_quotes = False
        quote_char = None
        
        while i < len(command):
            char = command[i]
            
            if char in "\"'" and not in_quotes:
                in_quotes = True
                quote_char = char
                current += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current += char
            elif not in_quotes:
                if char == "|" and i + 1 < len(command) and command[i + 1] == "|":
                    if current.strip():
                        commands.append({"command": current.strip(), "operator": "||"})
                    current = ""
                    i += 2
                    continue
                elif char == "&" and i + 1 < len(command) and command[i + 1] == "&":
                    if current.strip():
                        commands.append({"command": current.strip(), "operator": "&&"})
                    current = ""
                    i += 2
                    continue
                elif char == "|":
                    if current.strip():
                        commands.append({"command": current.strip(), "pipe_to": True})
                    current = ""
                    i += 1
                    continue
                elif char == ";":
                    if current.strip():
                        commands.append({"command": current.strip(), "operator": ";"})
                    current = ""
                    i += 1
                    continue
                elif char == "&" and (i + 1 >= len(command) or command[i + 1] != "&"):
                    if current.strip():
                        commands.append({"command": current.strip(), "background": True})
                    current = ""
                    i += 1
                    continue
                else:
                    current += char
            else:
                current += char
            
            i += 1
        
        if current.strip():
            commands.append({"command": current.strip()})
        
        return commands
    
    def handle_signal(self, signal: str):
        if signal == "SIGINT":
            self.interrupted = True
        elif signal == "SIGTSTP":
            pass
    
    def resize(self, cols: int, rows: int):
        self.cols = cols
        self.rows = rows
        self.env["COLUMNS"] = str(cols)
        self.env["LINES"] = str(rows)
