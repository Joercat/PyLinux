import time
import platform
import random
import psutil


class Kernel:
    def __init__(self, system):
        self.system = system
        self.version = "6.1.0-pylinux"
        self.release = "6.1.0-1-amd64"
        self.sysname = "Linux"
        self.machine = platform.machine() or "x86_64"
        self.modules = []
        self.dmesg_buffer = []

    def log(self, timestamp, level, subsystem, message):
        entry = f"[{timestamp:>10.6f}] [{level}] {subsystem}: {message}"
        self.dmesg_buffer.append(entry)
        return entry + "\n"

    def boot(self, callback):
        t = 0.0
        
        callback("\n")
        callback("BIOS POST... ")
        time.sleep(0.1)
        callback("OK\n")
        callback(f"Detected CPU: {platform.processor() or 'x86_64'}\n")
        callback(f"Memory Test: {psutil.virtual_memory().total // (1024*1024)} MB OK\n")
        callback("\n")
        
        callback("Loading GRUB 2.06...\n")
        time.sleep(0.1)
        callback("  GNU GRUB  version 2.06\n")
        callback("  Booting 'PyLinux 6.1.0'\n")
        callback("\n")
        
        callback(self.log(t, "INFO", "kernel", f"Linux version {self.version} (gcc 12.2.0)"))
        t += 0.000234
        
        callback(self.log(t, "INFO", "kernel", f"Command line: BOOT_IMAGE=/boot/vmlinuz-{self.release} root=/dev/sda1 ro quiet"))
        t += 0.000156
        
        mem_total = psutil.virtual_memory().total
        callback(self.log(t, "INFO", "kernel", f"Memory: {mem_total // 1024}K available"))
        t += 0.001234
        
        cpu_count = psutil.cpu_count() or 1
        callback(self.log(t, "INFO", "kernel", f"smpboot: Allowing {cpu_count} CPUs"))
        t += 0.002341
        
        callback(self.log(t, "INFO", "kernel", "Security Framework initialized"))
        t += 0.000456
        
        callback(self.log(t, "INFO", "kernel", "Mount-cache hash table entries: 4096"))
        t += 0.001234
        
        callback(self.log(t, "INFO", "kernel", "NET: Registered PF_NETLINK/PF_ROUTE protocol family"))
        t += 0.000234
        
        callback(self.log(t, "INFO", "kernel", "PCI: Using configuration type 1"))
        t += 0.001234
        
        callback(self.log(t, "INFO", "kernel", "clocksource: Switched to clocksource tsc"))
        t += 0.000567
        
        modules = [
            ("ext4", "EXT4-fs driver"),
            ("dm_mod", "Device Mapper driver"),
            ("sd_mod", "SCSI disk driver"),
            ("ahci", "AHCI SATA driver"),
            ("e1000e", "Intel Ethernet driver"),
            ("virtio_blk", "VirtIO Block driver"),
            ("virtio_net", "VirtIO Network driver")
        ]
        
        for mod, desc in modules:
            t += random.uniform(0.001, 0.005)
            callback(self.log(t, "INFO", "kernel", f"Loading module: {mod}"))
            self.modules.append(mod)
        
        t += 0.005
        callback(self.log(t, "INFO", "kernel", "Freeing unused kernel memory: 2048K"))
        t += 0.002
        
        callback(self.log(t, "INFO", "kernel", "systemd[1]: Detected architecture x86-64"))
        t += 0.001
        
        callback("\n")
        callback("Starting systemd services...\n")
        callback("\n")
        
        self.system.systemd.start_services(callback)
        self.system.filesystem.initialize()
        self.system.process_manager.create_init_processes()
        self.system.user_manager.initialize()
        self.system.device_manager.initialize()
        self.system.network_manager.initialize()
        
        callback("\n")
        callback(f"PyLinux {self.version} ({self.system.hostname}) (tty1)\n")
        callback("\n")
        callback(f"{self.system.hostname} login: root (automatic login)\n")
        callback("\n")
        
        self.system.current_user = 'root'
        
        callback("Welcome to PyLinux 6.1.0!\n")
        callback(f"  System information as of {time.strftime('%a %b %d %H:%M:%S %Z %Y')}\n")
        callback("\n")
        
        try:
            load = psutil.getloadavg()
            callback(f"  System load:  {load[0]:.2f}\n")
        except:
            callback(f"  System load:  0.00\n")
        
        callback(f"  Memory usage: {psutil.virtual_memory().percent:.0f}%\n")
        callback(f"  Processes:    {self.system.process_manager.get_count()}\n")
        callback("\n")

    def shutdown(self, callback, reboot=False):
        action = "reboot" if reboot else "power off"
        callback(f"\nBroadcast message from root@{self.system.hostname}:\n")
        callback(f"The system is going down for {action} NOW!\n\n")
        
        callback("Stopping all services...\n")
        time.sleep(0.2)
        
        callback("Sending SIGTERM to remaining processes...\n")
        time.sleep(0.1)
        callback("Sending SIGKILL to remaining processes...\n")
        time.sleep(0.1)
        
        callback("Unmounting filesystems...\n")
        time.sleep(0.1)
        
        callback("Syncing disks...\n")
        time.sleep(0.1)
        
        if reboot:
            callback("\nRebooting system...\n\n")
        else:
            callback("\nPower down...\n")
            callback("System halted.\n")

    def get_dmesg(self):
        return "\n".join(self.dmesg_buffer)

    def get_uname(self, options='a'):
        parts = {
            's': self.sysname,
            'n': self.system.hostname,
            'r': self.release,
            'v': f"#1 SMP PREEMPT_DYNAMIC {time.strftime('%a %b %d %H:%M:%S UTC %Y')}",
            'm': self.machine,
            'o': "GNU/Linux"
        }
        
        if 'a' in options:
            return f"{parts['s']} {parts['n']} {parts['r']} {parts['v']} {parts['m']} {parts['o']}"
        
        result = []
        for opt in options:
            if opt in parts:
                result.append(parts[opt])
        return " ".join(result)
