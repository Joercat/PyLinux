import time
import random
import threading
import psutil
import os

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
        self.fds = random.randint(3, 50)
        self.tty = '?'
        self.wchan = '-'
        self.virtual_mem = random.randint(1000, 500000)
        self.resident_mem = random.randint(500, 100000)
        self.shared_mem = random.randint(100, 50000)
        self.signals_pending = 0
        self.signals_blocked = 0
        self.signals_ignored = 0
        self.signals_caught = 0
        self.children = []
        self.environ = {}
        self.cwd = '/'
        self.exe = f'/usr/bin/{name}'

    def to_dict(self):
        return {
            'pid': self.pid,
            'ppid': self.ppid,
            'name': self.name,
            'user': self.user,
            'state': self.state,
            'nice': self.nice,
            'priority': self.priority,
            'command': self.command,
            'start_time': self.start_time,
            'cpu_time': self.cpu_time,
            'memory_percent': self.memory_percent,
            'threads': self.threads,
            'virtual_mem': self.virtual_mem,
            'resident_mem': self.resident_mem,
            'tty': self.tty
        }

class ProcessManager:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.processes = {}
        self.pid_counter = 1
        self.lock = threading.Lock()

    def create_init_processes(self):
        init_processes = [
            (1, 0, 'systemd', 'root', 'S', '/sbin/init'),
            (2, 0, 'kthreadd', 'root', 'S', '[kthreadd]'),
            (3, 2, 'rcu_gp', 'root', 'I', '[rcu_gp]'),
            (4, 2, 'rcu_par_gp', 'root', 'I', '[rcu_par_gp]'),
            (5, 2, 'slub_flushwq', 'root', 'I', '[slub_flushwq]'),
            (6, 2, 'netns', 'root', 'I', '[netns]'),
            (7, 2, 'kworker/0:0-events', 'root', 'I', '[kworker/0:0-events]'),
            (8, 2, 'kworker/0:0H-events_highpri', 'root', 'I', '[kworker/0:0H]'),
            (9, 2, 'kworker/u4:0-events_unbound', 'root', 'I', '[kworker/u4:0]'),
            (10, 2, 'mm_percpu_wq', 'root', 'I', '[mm_percpu_wq]'),
            (11, 2, 'rcu_tasks_kthre', 'root', 'S', '[rcu_tasks_kthre]'),
            (12, 2, 'rcu_tasks_trace', 'root', 'S', '[rcu_tasks_trace]'),
            (13, 2, 'ksoftirqd/0', 'root', 'S', '[ksoftirqd/0]'),
            (14, 2, 'rcu_preempt', 'root', 'I', '[rcu_preempt]'),
            (15, 2, 'migration/0', 'root', 'S', '[migration/0]'),
            (16, 2, 'cpuhp/0', 'root', 'S', '[cpuhp/0]'),
            (17, 2, 'cpuhp/1', 'root', 'S', '[cpuhp/1]'),
            (18, 2, 'migration/1', 'root', 'S', '[migration/1]'),
            (19, 2, 'ksoftirqd/1', 'root', 'S', '[ksoftirqd/1]'),
            (20, 2, 'kworker/1:0-events', 'root', 'I', '[kworker/1:0]'),
            (21, 2, 'kworker/1:0H-events_highpri', 'root', 'I', '[kworker/1:0H]'),
            (30, 2, 'kdevtmpfs', 'root', 'S', '[kdevtmpfs]'),
            (31, 2, 'inet_frag_wq', 'root', 'I', '[inet_frag_wq]'),
            (32, 2, 'kauditd', 'root', 'S', '[kauditd]'),
            (50, 2, 'khungtaskd', 'root', 'S', '[khungtaskd]'),
            (51, 2, 'oom_reaper', 'root', 'S', '[oom_reaper]'),
            (52, 2, 'writeback', 'root', 'I', '[writeback]'),
            (53, 2, 'kcompactd0', 'root', 'S', '[kcompactd0]'),
            (100, 1, 'systemd-journal', 'root', 'S', '/lib/systemd/systemd-journald'),
            (101, 1, 'systemd-udevd', 'root', 'S', '/lib/systemd/systemd-udevd'),
            (102, 1, 'systemd-logind', 'root', 'S', '/lib/systemd/systemd-logind'),
            (103, 1, 'dbus-daemon', 'messagebus', 'S', '/usr/bin/dbus-daemon --system'),
            (104, 1, 'rsyslogd', 'root', 'S', '/usr/sbin/rsyslogd'),
            (105, 1, 'cron', 'root', 'S', '/usr/sbin/cron'),
            (106, 1, 'sshd', 'root', 'S', '/usr/sbin/sshd -D'),
            (107, 1, 'agetty', 'root', 'S', '/sbin/agetty -o -p -- \\u --noclear tty1 linux'),
            (108, 1, 'login', 'root', 'S', '/bin/login'),
            (109, 108, 'bash', 'root', 'S', '-bash'),
            (150, 1, 'NetworkManager', 'root', 'S', '/usr/sbin/NetworkManager --no-daemon'),
            (151, 1, 'polkitd', 'polkitd', 'S', '/usr/lib/polkit-1/polkitd --no-debug'),
            (152, 1, 'accounts-daemon', 'root', 'S', '/usr/lib/accountsservice/accounts-daemon'),
            (153, 1, 'thermald', 'root', 'S', '/usr/sbin/thermald --no-daemon'),
            (154, 1, 'irqbalance', 'root', 'S', '/usr/sbin/irqbalance --foreground'),
            (200, 2, 'kworker/u4:1', 'root', 'I', '[kworker/u4:1]'),
            (201, 2, 'kworker/0:1', 'root', 'I', '[kworker/0:1]'),
            (202, 2, 'kworker/1:1', 'root', 'I', '[kworker/1:1]'),
            (250, 1, 'containerd', 'root', 'S', '/usr/bin/containerd'),
            (251, 1, 'dockerd', 'root', 'S', '/usr/bin/dockerd'),
        ]
        
        for pid, ppid, name, user, state, cmd in init_processes:
            proc = Process(pid, ppid, name, user, state, 0, cmd)
            self.processes[pid] = proc
            if pid >= self.pid_counter:
                self.pid_counter = pid + 1

    def create_process(self, name, user='root', command=None, ppid=1):
        with self.lock:
            pid = self.pid_counter
            self.pid_counter += 1
            
            proc = Process(pid, ppid, name, user, 'R', 0, command or name)
            self.processes[pid] = proc
            
            if ppid in self.processes:
                self.processes[ppid].children.append(pid)
            
            return pid

    def kill_process(self, pid, signal=15):
        with self.lock:
            if pid in self.processes:
                proc = self.processes[pid]
                
                if signal == 9:
                    for child_pid in proc.children:
                        if child_pid in self.processes:
                            del self.processes[child_pid]
                    del self.processes[pid]
                    return True, f"Process {pid} killed"
                elif signal == 15:
                    proc.state = 'T'
                    del self.processes[pid]
                    return True, f"Process {pid} terminated"
                elif signal == 19:
                    proc.state = 'T'
                    return True, f"Process {pid} stopped"
                elif signal == 18:
                    proc.state = 'S'
                    return True, f"Process {pid} continued"
                else:
                    return True, f"Signal {signal} sent to process {pid}"
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

    def get_processes_by_user(self, user):
        return [p for p in self.processes.values() if p.user == user]

    def get_processes_by_name(self, name):
        return [p for p in self.processes.values() if name in p.name or name in p.command]

    def get_children(self, pid):
        if pid in self.processes:
            return [self.processes[cpid] for cpid in self.processes[pid].children if cpid in self.processes]
        return []

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
            output.append(f"{'USER':<10} {'PID':>6} {'%CPU':>5} {'%MEM':>5} {'VSZ':>8} {'RSS':>8} {'TTY':<8} {'STAT':<5} {'START':>8} {'TIME':>8} COMMAND")
            for p in sorted(processes, key=lambda x: x.pid):
                elapsed = time.time() - p.start_time
                start_str = time.strftime('%H:%M', time.localtime(p.start_time))
                cpu_time_str = f"{int(p.cpu_time // 60)}:{int(p.cpu_time % 60):02d}"
                output.append(f"{p.user:<10} {p.pid:>6} {random.uniform(0, 5):>5.1f} {p.memory_percent:>5.1f} {p.virtual_mem:>8} {p.resident_mem:>8} {p.tty:<8} {p.state:<5} {start_str:>8} {cpu_time_str:>8} {p.command}")
        elif full:
            output.append(f"{'UID':<10} {'PID':>6} {'PPID':>6} {'C':>3} {'STIME':>8} {'TTY':<8} {'TIME':>8} CMD")
            for p in sorted(processes, key=lambda x: x.pid):
                start_str = time.strftime('%H:%M', time.localtime(p.start_time))
                cpu_time_str = f"{int(p.cpu_time // 60)}:{int(p.cpu_time % 60):02d}"
                output.append(f"{p.user:<10} {p.pid:>6} {p.ppid:>6} {0:>3} {start_str:>8} {p.tty:<8} {cpu_time_str:>8} {p.command}")
        else:
            output.append(f"{'PID':>6} {'TTY':<8} {'TIME':>8} CMD")
            for p in sorted(processes, key=lambda x: x.pid):
                cpu_time_str = f"{int(p.cpu_time // 60)}:{int(p.cpu_time % 60):02d}"
                output.append(f"{p.pid:>6} {p.tty:<8} {cpu_time_str:>8} {p.name}")
        
        return '\n'.join(output)

    def format_top_output(self):
        import psutil
        
        output = []
        
        uptime = time.time() - psutil.boot_time()
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        try:
            load = psutil.getloadavg()
            load_str = f"{load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}"
        except:
            load_str = "0.00, 0.00, 0.00"
        
        output.append(f"top - {time.strftime('%H:%M:%S')} up {hours}:{minutes:02d},  1 user,  load average: {load_str}")
        
        total = len(self.processes)
        running = self.get_running_count()
        sleeping = len([p for p in self.processes.values() if p.state == 'S'])
        stopped = len([p for p in self.processes.values() if p.state == 'T'])
        zombie = len([p for p in self.processes.values() if p.state == 'Z'])
        output.append(f"Tasks: {total:>3} total, {running:>3} running, {sleeping:>3} sleeping, {stopped:>3} stopped, {zombie:>3} zombie")
        
        cpu = psutil.cpu_percent(interval=0.1)
        cpu_times = psutil.cpu_times_percent()
        output.append(f"%Cpu(s): {cpu_times.user:>5.1f} us, {cpu_times.system:>5.1f} sy, {cpu_times.nice:>5.1f} ni, {cpu_times.idle:>5.1f} id, {cpu_times.iowait:>5.1f} wa, {0.0:>5.1f} hi, {cpu_times.softirq:>5.1f} si, {0.0:>5.1f} st")
        
        mem = psutil.virtual_memory()
        output.append(f"MiB Mem : {mem.total/1024/1024:>9.1f} total, {mem.free/1024/1024:>9.1f} free, {mem.used/1024/1024:>9.1f} used, {mem.cached/1024/1024 if hasattr(mem, 'cached') else 0:>9.1f} buff/cache")
        
        swap = psutil.swap_memory()
        output.append(f"MiB Swap: {swap.total/1024/1024:>9.1f} total, {swap.free/1024/1024:>9.1f} free, {swap.used/1024/1024:>9.1f} used. {mem.available/1024/1024:>9.1f} avail Mem")
        
        output.append("")
        output.append(f"{'PID':>7} {'USER':<9} {'PR':>3} {'NI':>3} {'VIRT':>10} {'RES':>8} {'SHR':>8} {'S':>1} {'%CPU':>5} {'%MEM':>5} {'TIME+':>10} COMMAND")
        
        sorted_procs = sorted(self.processes.values(), key=lambda x: x.memory_percent, reverse=True)[:20]
        for p in sorted_procs:
            cpu_time_str = f"{int(p.cpu_time // 60)}:{p.cpu_time % 60:05.2f}"
            output.append(f"{p.pid:>7} {p.user:<9} {p.priority:>3} {p.nice:>3} {p.virtual_mem:>10} {p.resident_mem:>8} {p.shared_mem:>8} {p.state:>1} {random.uniform(0, 5):>5.1f} {p.memory_percent:>5.1f} {cpu_time_str:>10} {p.name}")
        
        return '\n'.join(output)
