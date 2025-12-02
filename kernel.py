import time
import platform
import random
import psutil
import os

class Kernel:
    def __init__(self, system):
        self.system = system
        self.version = "6.1.0-pylinux"
        self.release = "6.1.0-1-amd64"
        self.sysname = "Linux"
        self.machine = platform.machine()
        self.modules = []
        self.kernel_params = {
            'quiet': False,
            'splash': False,
            'ro': True,
            'root': '/dev/sda1'
        }
        self.dmesg_buffer = []
        self.interrupts = {}
        self.loadavg = [0.0, 0.0, 0.0]

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
        
        callback(self.log(t, "INFO", "kernel", f"x86/fpu: x87 FPU on CPU"))
        t += 0.000089
        
        callback(self.log(t, "INFO", "kernel", "BIOS-provided physical RAM map:"))
        t += 0.000045
        
        mem_total = psutil.virtual_memory().total
        callback(self.log(t, "INFO", "kernel", f"BIOS-e820: [mem 0x0000000000000000-0x{mem_total:016x}] usable"))
        t += 0.000123
        
        callback(self.log(t, "INFO", "kernel", f"Memory: {mem_total // 1024}K/available"))
        t += 0.001234
        
        callback(self.log(t, "INFO", "kernel", "CPU: Physical Processor ID: 0"))
        t += 0.000567
        
        cpu_count = psutil.cpu_count()
        callback(self.log(t, "INFO", "kernel", f"smpboot: Allowing {cpu_count} CPUs"))
        t += 0.002341
        
        callback(self.log(t, "INFO", "kernel", "Security Framework initialized"))
        t += 0.000234
        callback(self.log(t, "INFO", "kernel", "LSM: Security Framework initialized"))
        t += 0.000456
        
        callback(self.log(t, "INFO", "kernel", "Dentry cache hash table entries: 262144"))
        t += 0.000789
        callback(self.log(t, "INFO", "kernel", "Inode-cache hash table entries: 131072"))
        t += 0.000234
        
        callback(self.log(t, "INFO", "kernel", "Mount-cache hash table entries: 4096"))
        t += 0.001234
        
        callback(self.log(t, "INFO", "kernel", "CPU0: Thermal monitoring enabled"))
        t += 0.002345
        
        callback(self.log(t, "INFO", "kernel", f"smpboot: CPU{cpu_count-1} booted"))
        t += 0.003456
        
        callback(self.log(t, "INFO", "kernel", "NET: Registered PF_NETLINK/PF_ROUTE protocol family"))
        t += 0.000234
        
        callback(self.log(t, "INFO", "kernel", "PCI: Using configuration type 1"))
        t += 0.001234
        
        callback(self.log(t, "INFO", "kernel", "ACPI: Core revision 20220331"))
        t += 0.002345
        
        callback(self.log(t, "INFO", "kernel", "clocksource: Switched to clocksource tsc"))
        t += 0.000567
        
        callback(self.log(t, "INFO", "kernel", "VFS: Disk quotas dquot_6.6.0"))
        t += 0.000234
        callback(self.log(t, "INFO", "kernel", "VFS: Dquot-cache hash table entries: 512"))
        t += 0.000456
        
        callback(self.log(t, "INFO", "kernel", "NET: Registered PF_INET protocol family"))
        t += 0.001234
        callback(self.log(t, "INFO", "kernel", "NET: Registered PF_INET6 protocol family"))
        t += 0.000567
        
        callback(self.log(t, "INFO", "kernel", "RPC: Registered named UNIX socket transport module"))
        t += 0.000234
        callback(self.log(t, "INFO", "kernel", "RPC: Registered udp transport module"))
        t += 0.000123
        callback(self.log(t, "INFO", "kernel", "RPC: Registered tcp transport module"))
        t += 0.000234
        
        modules = [
            ("ext4", "EXT4-fs driver"),
            ("xfs", "XFS filesystem driver"),
            ("btrfs", "BTRFS filesystem driver"),
            ("dm_mod", "Device Mapper driver"),
            ("sd_mod", "SCSI disk driver"),
            ("ahci", "AHCI SATA driver"),
            ("nvme", "NVMe driver"),
            ("usb_storage", "USB Mass Storage driver"),
            ("usbhid", "USB HID driver"),
            ("i915", "Intel Graphics driver"),
            ("snd_hda_intel", "Intel HD Audio driver"),
            ("e1000e", "Intel Ethernet driver"),
            ("iwlwifi", "Intel Wireless driver"),
            ("bluetooth", "Bluetooth driver"),
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
        
        callback(self.log(t, "INFO", "kernel", "Write protecting kernel text and rodata"))
        t += 0.001
        
        callback(self.log(t, "INFO", "kernel", "systemd[1]: Detected virtualization"))
        t += 0.003
        callback(self.log(t, "INFO", "kernel", "systemd[1]: Detected architecture x86-64"))
        t += 0.001
        callback(self.log(t, "INFO", "kernel", "systemd[1]: Running in initial RAM disk"))
        t += 0.002
        
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
        callback(f"  System load:  {psutil.getloadavg()[0]:.2f}\n")
        callback(f"  Memory usage: {psutil.virtual_memory().percent:.0f}%\n")
        callback(f"  Swap usage:   {psutil.swap_memory().percent:.0f}%\n")
        callback(f"  Processes:    {self.system.process_manager.get_count()}\n")
        callback(f"  Users:        1 user logged in\n")
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
            'p': self.machine,
            'i': self.machine,
            'o': "GNU/Linux"
        }
        
        if 'a' in options:
            return f"{parts['s']} {parts['n']} {parts['r']} {parts['v']} {parts['m']} {parts['o']}"
        
        result = []
        for opt in options:
            if opt in parts:
                result.append(parts[opt])
        return " ".join(result)

    def get_loadavg(self):
        try:
            load = psutil.getloadavg()
            return f"{load[0]:.2f} {load[1]:.2f} {load[2]:.2f} {self.system.process_manager.get_running_count()}/{self.system.process_manager.get_count()} {self.system.process_manager.get_last_pid()}"
        except:
            return "0.00 0.00 0.00 1/1 1"
