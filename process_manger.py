import time
import random
import threading
import psutil


class Process:
    def __init__(self, pid, ppid, name, user='root', state='S', nice=0, command=''):
        self.pid = pid
        self.ppid = ppid
        self.name = name
        self.user = user
        self.state = state
        self.nice = nice
        self.priority = 20 + nice
        self.command = command or name
        self.start_time = time.time()
        self.cpu_time = 0.0
        self.memory_percent = random.uniform(0.1, 2.0)
        self.threads = 1
        self.tty = '?'
        self.virtual_mem = random.randint(1000, 500000)
        self.resident_mem = random.randint(500, 100000)
        self.shared_mem = random.randint(100, 50000)
        self.children = []

    def to_dict(self):
        return {
            'pid': self.pid, 'ppid': self.ppid, 'name': self.name,
            'user': self.user, 'state': self.state, 'command': self.command,
            'memory_percent': self.memory_percent
        }


class ProcessManager:
    def __init__(self):
        self.processes = {}
        self.pid_counter = 1
        self.lock = threading.Lock()

    def create_init_processes(self):
        init_procs = [
            (1, 0, 'systemd', 'root', 'S', '/sbin/init'),
            (2, 0, 'kthreadd', 'root', 'S', '[kthreadd]'),
            (100, 1, 'systemd-journal', 'root', 'S', '/lib/systemd/systemd-journald'),
            (101, 1, 'systemd-udevd', 'root', 'S', '/lib/systemd/systemd-udevd'),
            (102, 1, 'systemd-logind', 'root', 'S', '/lib/systemd/systemd-logind'),
            (103, 1, 'dbus-daemon', 'messagebus', 'S', '/usr/bin/dbus-daemon'),
            (104, 1, 'rsyslogd', 'root', 'S', '/usr/sbin/rsyslogd'),
            (105, 1, 'cron', 'root', 'S', '/usr/sbin/cron'),
            (106, 1, 'sshd', 'root', 'S', '/usr/sbin/sshd'),
            (107, 1, 'agetty', 'root', 'S', '/sbin/agetty tty1'),
            (108, 107, 'login', 'root', 'S', '/bin/login'),
            (109, 108, 'bash', 'root', 'S', '-bash'),
        ]
        for pid, ppid, name, user, state, cmd in init_procs:
            self.processes[pid] = Process(pid, ppid, name, user, state, 0, cmd)
            if pid >= self.pid_counter:
                self.pid_counter = pid + 1

    def create_process(self, name, user='root', command=None, ppid=1):
        with self.lock:
            pid = self.pid_counter
            self.pid_counter += 1
            self.processes[pid] = Process(pid, ppid, name, user, 'R', 0, command or name)
            return pid

    def kill_process(self, pid, signal=15):
        with self.lock:
            if pid in self.processes:
                del self.processes[pid]
                return True, f"Process {pid} terminated"
            return False, f"No such process: {pid}"

    def get_process(self, pid):
        return self.processes.get(pid)

    def get_all_processes(self):
        return list(self.processes.values())

    def get_count(self):
        return len(self.processes)

    def get_running_count(self):
        return len([p for p in self.processes.values() if p.state == 'R'])

    def get_last_pid(self):
        return self.pid_counter - 1

    def get_processes_by_name(self, name):
        return [p for p in self.processes.values() if name in p.name or name in p.command]

    def set_nice(self, pid, nice_value):
        if pid in self.processes:
            self.processes[pid].nice = max(-20, min(19, nice_value))
            self.processes[pid].priority = 20 + self.processes[pid].nice
            return True
        return False

    def format_ps_output(self, processes=None, full=False, aux=False):
        if processes is None:
            processes = self.get_all_processes()
        output = []
        if aux:
            output.append(f"{'USER':<10} {'PID':>6} {'%CPU':>5} {'%MEM':>5} {'VSZ':>8} {'RSS':>8} {'STAT':<5} {'COMMAND'}")
            for p in sorted(processes, key=lambda x: x.pid):
                output.append(f"{p.user:<10} {p.pid:>6} {random.uniform(0, 5):>5.1f} {p.memory_percent:>5.1f} {p.virtual_mem:>8} {p.resident_mem:>8} {p.state:<5} {p.command}")
        else:
            output.append(f"{'PID':>6} {'TTY':<8} {'TIME':>8} CMD")
            for p in sorted(processes, key=lambda x: x.pid):
                cpu_time_str = f"{int(p.cpu_time // 60)}:{int(p.cpu_time % 60):02d}"
                output.append(f"{p.pid:>6} {p.tty:<8} {cpu_time_str:>8} {p.name}")
        return '\n'.join(output)

    def format_top_output(self):
        output = []
        try:
            load = psutil.getloadavg()
            load_str = f"{load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}"
        except:
            load_str = "0.00, 0.00, 0.00"
        
        output.append(f"top - {time.strftime('%H:%M:%S')} up 0:00,  1 user,  load average: {load_str}")
        total = len(self.processes)
        running = self.get_running_count()
        sleeping = len([p for p in self.processes.values() if p.state == 'S'])
        output.append(f"Tasks: {total:>3} total, {running:>3} running, {sleeping:>3} sleeping")
        
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            output.append(f"%Cpu(s): {cpu_percent:>5.1f} us,  0.0 sy,  0.0 ni, {100-cpu_percent:>5.1f} id")
            output.append(f"MiB Mem : {mem.total/1024/1024:>9.1f} total, {mem.free/1024/1024:>9.1f} free, {mem.used/1024/1024:>9.1f} used")
        except:
            output.append("%Cpu(s):  0.0 us,  0.0 sy,  0.0 ni, 100.0 id")
            output.append("MiB Mem :   1024.0 total,   512.0 free,   512.0 used")
        
        output.append("")
        output.append(f"{'PID':>7} {'USER':<9} {'PR':>3} {'NI':>3} {'VIRT':>10} {'RES':>8} {'S':>1} {'%CPU':>5} {'%MEM':>5} COMMAND")
        
        sorted_procs = sorted(self.processes.values(), key=lambda x: x.memory_percent, reverse=True)[:15]
        for p in sorted_procs:
            output.append(f"{p.pid:>7} {p.user:<9} {p.priority:>3} {p.nice:>3} {p.virtual_mem:>10} {p.resident_mem:>8} {p.state:>1} {random.uniform(0, 5):>5.1f} {p.memory_percent:>5.1f} {p.name}")
        
        return '\n'.join(output)
