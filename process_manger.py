import time
import random
import threading

class Process:
    _pid_counter = 1
    _lock = threading.Lock()
    
    def __init__(self, name, command='', user='root', parent_pid=0):
        with Process._lock:
            self.pid = Process._pid_counter
            Process._pid_counter += 1
        
        self.name = name
        self.command = command
        self.user = user
        self.parent_pid = parent_pid
        self.state = 'R'
        self.cpu_percent = random.uniform(0.0, 5.0)
        self.memory_kb = random.randint(1024, 8192)
        self.start_time = time.time()
        self.priority = 20
        self.nice = 0
        self.threads = 1

    def update_stats(self):
        self.cpu_percent = random.uniform(0.0, 5.0)

    def get_runtime(self):
        return time.time() - self.start_time

    def to_dict(self):
        return {
            'pid': self.pid,
            'name': self.name,
            'command': self.command,
            'user': self.user,
            'parent_pid': self.parent_pid,
            'state': self.state,
            'cpu_percent': round(self.cpu_percent, 1),
            'memory_kb': self.memory_kb,
            'start_time': self.start_time,
            'priority': self.priority,
            'nice': self.nice,
            'threads': self.threads
        }

class ProcessManager:
    def __init__(self, memory_manager):
        self.processes = {}
        self.memory_manager = memory_manager
        self._initialize_system_processes()

    def _initialize_system_processes(self):
        system_processes = [
            ('init', '/sbin/init', 'root'),
            ('kthreadd', '[kthreadd]', 'root'),
            ('systemd', '/lib/systemd/systemd', 'root'),
            ('systemd-journal', '/lib/systemd/systemd-journald', 'root'),
            ('systemd-udevd', '/lib/systemd/systemd-udevd', 'root'),
            ('dbus-daemon', '/usr/bin/dbus-daemon', 'messagebus'),
            ('rsyslogd', '/usr/sbin/rsyslogd', 'syslog'),
            ('cron', '/usr/sbin/cron', 'root'),
            ('sshd', '/usr/sbin/sshd', 'root'),
            ('getty', '/sbin/getty', 'root'),
        ]
        
        for name, command, user in system_processes:
            proc = Process(name, command, user, parent_pid=1 if name != 'init' else 0)
            self.processes[proc.pid] = proc
            self.memory_manager.allocate(proc.memory_kb * 1024, f"process_{proc.pid}")

    def create_process(self, name, command='', user='root', parent_pid=1):
        proc = Process(name, command, user, parent_pid)
        self.processes[proc.pid] = proc
        self.memory_manager.allocate(proc.memory_kb * 1024, f"process_{proc.pid}")
        return proc.pid

    def get_process(self, pid):
        return self.processes.get(pid)

    def kill_process(self, pid):
        if pid in self.processes and pid > 10:
            proc = self.processes[pid]
            self.memory_manager.free(f"process_{pid}")
            del self.processes[pid]
            return True
        return False

    def list_processes(self):
        for proc in self.processes.values():
            proc.update_stats()
        return list(self.processes.values())

    def get_process_tree(self):
        tree = {}
        for proc in self.processes.values():
            if proc.parent_pid not in tree:
                tree[proc.parent_pid] = []
            tree[proc.parent_pid].append(proc)
        return tree

    def get_stats(self):
        return {
            'total': len(self.processes),
            'running': sum(1 for p in self.processes.values() if p.state == 'R'),
            'sleeping': sum(1 for p in self.processes.values() if p.state == 'S'),
            'stopped': sum(1 for p in self.processes.values() if p.state == 'T'),
            'zombie': sum(1 for p in self.processes.values() if p.state == 'Z'),
        }
