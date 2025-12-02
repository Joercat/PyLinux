import time
import random

class SystemD:
    def __init__(self, system):
        self.system = system
        self.services = {}
        self.targets = {}
        self.units = {}
        self.journal = []

    def start_services(self, callback):
        services = [
            ('systemd-journald.service', 'Journal Service'),
            ('systemd-udevd.service', 'udev Kernel Device Manager'),
            ('systemd-tmpfiles-setup.service', 'Create Volatile Files'),
            ('systemd-sysctl.service', 'Apply Kernel Variables'),
            ('systemd-modules-load.service', 'Load Kernel Modules'),
            ('systemd-random-seed.service', 'Load/Save Random Seed'),
            ('sys-kernel-debug.mount', 'Kernel Debug File System'),
            ('dev-mqueue.mount', 'POSIX Message Queue FS'),
            ('kmod-static-nodes.service', 'Create Static Device Nodes'),
            ('systemd-networkd.service', 'Network Service'),
            ('systemd-resolved.service', 'Network Name Resolution'),
            ('dbus.service', 'D-Bus System Message Bus'),
            ('rsyslog.service', 'System Logging Service'),
            ('cron.service', 'Regular background program processing'),
            ('ssh.service', 'OpenBSD Secure Shell server'),
            ('systemd-logind.service', 'Login Service'),
            ('getty@tty1.service', 'Getty on tty1'),
            ('multi-user.target', 'Multi-User System')
        ]
        
        for service_name, description in services:
            t = random.uniform(0.02, 0.1)
            status = "[\033[32m  OK  \033[0m]"
            
            if service_name.endswith('.target'):
                callback(f"{status} Reached target {description}.\n")
            elif service_name.endswith('.mount'):
                callback(f"{status} Mounted {description}.\n")
            else:
                callback(f"{status} Started {description}.\n")
            
            self.services[service_name] = {
                'state': 'running' if not service_name.endswith(('.target', '.mount')) else 'active',
                'description': description,
                'pid': random.randint(100, 500) if not service_name.endswith(('.target', '.mount')) else None,
                'start_time': time.time(),
                'type': 'simple',
                'main_pid': random.randint(100, 500)
            }
            
            self.log(service_name, 'info', f'Started {description}')
            
            time.sleep(t)

    def stop_all_services(self, callback):
        for service_name, service in reversed(list(self.services.items())):
            if service['state'] == 'running':
                status = "[\033[32m  OK  \033[0m]"
                callback(f"{status} Stopped {service['description']}.\n")
                service['state'] = 'stopped'
                time.sleep(0.02)

    def log(self, unit, priority, message):
        entry = {
            'timestamp': time.time(),
            'unit': unit,
            'priority': priority,
            'message': message,
            'pid': random.randint(1, 1000)
        }
        self.journal.append(entry)

    def systemctl(self, args):
        if not args:
            return self._list_units()
        
        command = args[0]
        unit = args[1] if len(args) > 1 else None
        
        if command == 'status':
            return self._status(unit)
        elif command == 'start':
            return self._start(unit)
        elif command == 'stop':
            return self._stop(unit)
        elif command == 'restart':
            return self._restart(unit)
        elif command == 'enable':
            return self._enable(unit)
        elif command == 'disable':
            return self._disable(unit)
        elif command == 'is-active':
            return self._is_active(unit)
        elif command == 'is-enabled':
            return self._is_enabled(unit)
        elif command == 'list-units':
            return self._list_units()
        elif command == 'list-unit-files':
            return self._list_unit_files()
        elif command == 'daemon-reload':
            return ''
        elif command == 'cat':
            return self._cat_unit(unit)
        elif command == 'show':
            return self._show_unit(unit)
        elif command == '--version':
            return "systemd 247 (247.3-7)\n+PAM +AUDIT +SELINUX +IMA +APPARMOR +SMACK +SYSVINIT +UTMP +LIBCRYPTSETUP +GCRYPT +GNUTLS +ACL +XZ +LZ4 +ZSTD +SECCOMP +BLKID +ELFUTILS +KMOD +IDN2 -IDN +PCRE2 default-hierarchy=unified\n"
        
        return f"systemctl: unknown command '{command}'\n"

    def _list_units(self):
        output = "UNIT                           LOAD   ACTIVE SUB       DESCRIPTION\n"
        
        for name, service in self.services.items():
            state = service['state']
            active = 'active' if state in ['running', 'active'] else 'inactive'
            sub = state if state != 'active' else 'exited'
            load = 'loaded'
            
            output += f"{name:<30} {load:<6} {active:<6} {sub:<9} {service['description']}\n"
        
        output += f"\n{len(self.services)} loaded units listed.\n"
        return output

    def _list_unit_files(self):
        output = "UNIT FILE                     STATE    VENDOR PRESET\n"
        
        for name in self.services:
            state = 'enabled' if random.random() > 0.3 else 'disabled'
            preset = 'enabled' if random.random() > 0.5 else 'disabled'
            output += f"{name:<30}{state:<9}{preset}\n"
        
        output += f"\n{len(self.services)} unit files listed.\n"
        return output

    def _status(self, unit):
        if not unit:
            return "systemctl: missing unit name\n"
        
        if unit not in self.services:
            return f"Unit {unit} could not be found.\n"
        
        service = self.services[unit]
        state = service['state']
        active = 'active' if state in ['running', 'active'] else 'inactive'
        
        output = f"● {unit} - {service['description']}\n"
        output += f"     Loaded: loaded (/lib/systemd/system/{unit}; enabled; vendor preset: enabled)\n"
        output += f"     Active: {active} ({state}) since {time.strftime('%a %Y-%m-%d %H:%M:%S %Z', time.localtime(service['start_time']))}\n"
        
        if service.get('pid'):
            output += f"   Main PID: {service['pid']} ({unit.replace('.service', '')})\n"
        
        output += f"      Tasks: {random.randint(1, 10)} (limit: 4915)\n"
        output += f"     Memory: {random.randint(1, 100)}M\n"
        output += f"        CPU: {random.randint(1, 1000)}ms\n"
        output += f"     CGroup: /system.slice/{unit}\n"
        
        if service.get('pid'):
            output += f"
                         └─{service['pid']} /usr/sbin/{unit.replace('.service', '')}\n"
        
        output += f"\n{time.strftime('%b %d %H:%M:%S')} {self.system.hostname} systemd[1]: Started {service['description']}.\n"
        
        return output

    def _start(self, unit):
        if not unit:
            return "systemctl: missing unit name\n"
        
        if unit not in self.services:
            self.services[unit] = {
                'state': 'running',
                'description': unit.replace('.service', '').replace('-', ' ').title(),
                'pid': random.randint(1000, 9999),
                'start_time': time.time(),
                'type': 'simple',
                'main_pid': random.randint(1000, 9999)
            }
        else:
            self.services[unit]['state'] = 'running'
            self.services[unit]['start_time'] = time.time()
        
        self.log(unit, 'info', f'Started {unit}')
        return ''

    def _stop(self, unit):
        if not unit:
            return "systemctl: missing unit name\n"
        
        if unit in self.services:
            self.services[unit]['state'] = 'stopped'
            self.log(unit, 'info', f'Stopped {unit}')
        
        return ''

    def _restart(self, unit):
        self._stop(unit)
        return self._start(unit)

    def _enable(self, unit):
        if not unit:
            return "systemctl: missing unit name\n"
        
        return f"Created symlink /etc/systemd/system/multi-user.target.wants/{unit} → /lib/systemd/system/{unit}.\n"

    def _disable(self, unit):
        if not unit:
            return "systemctl: missing unit name\n"
        
        return f"Removed /etc/systemd/system/multi-user.target.wants/{unit}.\n"

    def _is_active(self, unit):
        if unit in self.services:
            state = self.services[unit]['state']
            if state in ['running', 'active']:
                return "active\n"
        return "inactive\n"

    def _is_enabled(self, unit):
        return "enabled\n" if random.random() > 0.3 else "disabled\n"

    def _cat_unit(self, unit):
        if not unit:
            return "systemctl: missing unit name\n"
        
        return f"""# /lib/systemd/system/{unit}
[Unit]
Description={self.services.get(unit, {}).get('description', unit)}
Documentation=man:{unit.replace('.service', '')}(8)
After=network.target

[Service]
Type=simple
ExecStart=/usr/sbin/{unit.replace('.service', '')}
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
"""

    def _show_unit(self, unit):
        if not unit:
            return "systemctl: missing unit name\n"
        
        service = self.services.get(unit, {})
        return f"""Type=simple
Restart=on-failure
NotifyAccess=none
RestartUSec=5s
TimeoutStartUSec=1min 30s
TimeoutStopUSec=1min 30s
RuntimeMaxUSec=infinity
WatchdogUSec=0
WatchdogTimestamp={time.strftime('%a %Y-%m-%d %H:%M:%S %Z')}
PermissionsStartOnly=no
RootDirectoryStartOnly=no
RemainAfterExit=no
GuessMainPID=yes
MainPID={service.get('pid', 0)}
ControlPID=0
FileDescriptorStoreMax=0
NFileDescriptorStore=0
StatusErrno=0
Result=success
UID=[not set]
GID=[not set]
NRestarts=0
"""

    def journalctl(self, args):
        lines = 10
        unit = None
        follow = False
        boot = False
        priority = None
        since = None
        until = None
        output_format = 'short'
        
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
            elif arg == '-u' and i + 1 < len(args):
                unit = args[i + 1]
                i += 1
            elif arg == '-f' or arg == '--follow':
                follow = True
            elif arg == '-b' or arg == '--boot':
                boot = True
            elif arg == '-p' and i + 1 < len(args):
                priority = args[i + 1]
                i += 1
            elif arg == '--since' and i + 1 < len(args):
                since = args[i + 1]
                i += 1
            elif arg == '--until' and i + 1 < len(args):
                until = args[i + 1]
                i += 1
            elif arg == '-o' and i + 1 < len(args):
                output_format = args[i + 1]
                i += 1
            elif arg == '-k' or arg == '--dmesg':
                return self.system.kernel.get_dmesg() + '\n'
            elif arg == '--disk-usage':
                return "Archived and active journals take up 48.0M in the file system.\n"
            elif arg == '--list-boots':
                return f" 0 {'0' * 32} {time.strftime('%a %Y-%m-%d %H:%M:%S %Z')} - {time.strftime('%a %Y-%m-%d %H:%M:%S %Z')}\n"
            i += 1
        
        filtered_entries = self.journal[-lines:] if self.journal else []
        
        if unit:
            filtered_entries = [e for e in filtered_entries if unit in e.get('unit', '')]
        
        output = f"-- Journal begins at {time.strftime('%a %Y-%m-%d %H:%M:%S %Z')}, ends at {time.strftime('%a %Y-%m-%d %H:%M:%S %Z')}. --\n"
        
        for entry in filtered_entries:
            ts = time.strftime('%b %d %H:%M:%S', time.localtime(entry['timestamp']))
            output += f"{ts} {self.system.hostname} {entry['unit']}[{entry['pid']}]: {entry['message']}\n"
        
        if not filtered_entries:
            output += f"{time.strftime('%b %d %H:%M:%S')} {self.system.hostname} systemd[1]: System started.\n"
            output += f"{time.strftime('%b %d %H:%M:%S')} {self.system.hostname} kernel: Linux version 6.1.0-pylinux\n"
        
        return output
