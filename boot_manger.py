import time
import random

class BootManager:
    def __init__(self, filesystem, process_manager, memory_manager, device_manager, network_manager):
        self.filesystem = filesystem
        self.process_manager = process_manager
        self.memory_manager = memory_manager
        self.device_manager = device_manager
        self.network_manager = network_manager

    def boot(self):
        boot_messages = [
            '[    0.000000] Linux version 5.15.0-terminal (root@localhost) (gcc 11.2.0)',
            '[    0.000000] Command line: BOOT_IMAGE=/boot/vmlinuz root=/dev/sda1 ro quiet',
            '[    0.000000] x86/fpu: Supporting XSAVE feature 0x001: \'x87 floating point registers\'',
            '[    0.000000] x86/fpu: Supporting XSAVE feature 0x002: \'SSE registers\'',
            '[    0.000000] x86/fpu: xstate_offset[2]:  576, xstate_sizes[2]:  256',
            '[    0.000000] Memory: 2048000K/2097152K available',
            '[    0.001000] Calibrating delay loop... 4800.00 BogoMIPS',
            '[    0.002000] pid_max: default: 32768 minimum: 301',
            '[    0.003000] Mount-cache hash table entries: 2048',
            '[    0.004000] CPU: Intel(R) Virtual CPU',
            '[    0.005000] Initializing CPU#0',
            '[    0.010000] ACPI: Core revision 20210730',
            '[    0.015000] clocksource: tsc: mask: 0xffffffffffffffff',
            '[    0.020000] PCI: Using configuration type 1 for base access',
            '[    0.025000] SCSI subsystem initialized',
            '[    0.030000] usbcore: registered new interface driver usbfs',
            '[    0.035000] PCI: Probing PCI hardware',
            '[    0.040000] NetLabel: Initializing',
            '[    0.045000] NetLabel: protocols = UNLABELED CIPSOv4 CALIPSO',
            '[    0.050000] random: get_random_bytes called',
            '[    0.060000] Freeing SMP alternatives memory',
            '[    0.070000] Running /sbin/init',
            '',
            '[ OK ] Started System Logging Service',
            '[ OK ] Started D-Bus System Message Bus',
            '[ OK ] Started Network Manager',
            '[ OK ] Started User Manager for UID 0',
            '[ OK ] Reached target Multi-User System',
            '[ OK ] Reached target Graphical Interface',
            '',
            'LinuxTerminal 1.0 LTS localhost tty1',
            ''
        ]
        
        for msg in boot_messages:
            yield msg
        
        self.device_manager.initialize_devices()
        self.network_manager.start()

    def shutdown(self):
        shutdown_messages = [
            '',
            'Broadcast message from root@localhost',
            f'        ({time.strftime("%a %Y-%m-%d %H:%M:%S %Z")})',
            '',
            'The system is going down for poweroff NOW!',
            '',
            '[ OK ] Stopped target Graphical Interface',
            '[ OK ] Stopped target Multi-User System',
            '[ OK ] Stopped User Manager for UID 0',
            '[ OK ] Stopped Network Manager',
            '[ OK ] Stopped D-Bus System Message Bus',
            '[ OK ] Stopped System Logging Service',
            '[   OK   ] Stopping Session 1 of user root',
            '[   OK   ] Removed slice User Slice of UID 0',
            '[   OK   ] Stopped target Basic System',
            '[   OK   ] Stopped target Paths',
            '[   OK   ] Stopped target Sockets',
            '[   OK   ] Stopped target Timers',
            '[   OK   ] Unmounted /boot',
            '[   OK   ] Unmounted /home',
            '[   OK   ] Reached target Unmount All Filesystems',
            '[   OK   ] Reached target Final Step',
            '[   OK   ] Reached target Poweroff',
            '',
            'System halted.',
            ''
        ]
        
        for msg in shutdown_messages:
            yield msg
