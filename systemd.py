import time
import random


class SystemD:
    def __init__(self, system):
        self.system = system
        self.services = {}

    def start_services(self, callback):
        services = [
            ('systemd-journald.service', 'Journal Service'),
            ('systemd-udevd.service', 'udev Kernel Device Manager'),
            ('dbus.service', 'D-Bus System Message Bus'),
            ('rsyslog.service', 'System Logging Service'),
            ('cron.service', 'Regular background program processing'),
            ('ssh.service', 'OpenBSD Secure Shell server'),
            ('getty@tty1.service', 'Getty on tty1'),
            ('multi-user.target', 'Multi-User System')
        ]
        for name, desc in services:
            status = "[\033[32m  OK  \033[0m]"
            if name.endswith('.target'):
                callback(f"{status} Reached target {desc}.\n")
            else:
                callback(f"{status} Started {desc}.\n")
            self.services[name] = {'state': 'running', 'description': desc, 'start_time': time.time()}
            time.sleep(random.uniform(0.02, 0.08))

    def stop_all_services(self, callback):
        for name, svc in reversed(list(self.services.items())):
            if svc['state'] == 'running':
                callback(f"[\033[32m  OK  \033[0m] Stopped {svc['description']}.\n")
                svc['state'] = 'stopped'
                time.sleep(0.02)

    def systemctl(self, args):
        if not args:
            return self._list_units()
        cmd = args[0]
        unit = args[1] if len(args) > 1 else None
        
        if cmd == 'status':
            if unit and unit in self.services:
                svc = self.services[unit]
                return f"● {unit} - {svc['description']}\n   Loaded: loaded\n   Active: active (running)\n"
            return f"Unit {unit} not found.\n" if unit else self._list_units()
        elif cmd == 'start':
            if unit:
                self.services[unit] = {'state': 'running', 'description': unit, 'start_time': time.time()}
            return ''
        elif cmd == 'stop':
            if unit and unit in self.services:
                self.services[unit]['state'] = 'stopped'
            return ''
        elif cmd == 'restart':
            return ''
        elif cmd == 'enable':
            return f"Created symlink for {unit}\n" if unit else ''
        elif cmd == 'disable':
            return f"Removed symlink for {unit}\n" if unit else ''
        elif cmd == 'list-units':
            return self._list_units()
        elif cmd == 'daemon-reload':
            return ''
        return f"Unknown command: {cmd}\n"

    def _list_units(self):
        output = "UNIT                           LOAD   ACTIVE SUB     DESCRIPTION\n"
        for name, svc in self.services.items():
            output += f"{name:<30} loaded active running {svc['description']}\n"
        output += f"\n{len(self.services)} loaded units listed.\n"
        return output
