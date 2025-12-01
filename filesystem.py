import os
import time
import json
import hashlib
import base64
import gzip
from typing import Optional, Dict, List, Any

class VirtualFileSystem:
    def __init__(self):
        self.inodes = {}
        self.next_inode = 1
        self.root = None
        self.open_files = {}
        self.next_fd = 3
        self.mounts = {}
        self.symlinks = {}
    
    def initialize_default_structure(self):
        self.create_directory("/", mode=0o755, uid=0, gid=0)
        
        dirs = [
            "/bin", "/sbin", "/usr", "/usr/bin", "/usr/sbin", "/usr/lib",
            "/usr/local", "/usr/local/bin", "/usr/share", "/usr/share/man",
            "/etc", "/etc/skel", "/etc/default", "/etc/init.d", "/etc/cron.d",
            "/var", "/var/log", "/var/run", "/var/tmp", "/var/spool",
            "/var/cache", "/var/lib", "/var/mail",
            "/home", "/home/user", "/home/user/Documents", "/home/user/Downloads",
            "/home/user/Pictures", "/home/user/Music", "/home/user/Videos",
            "/home/user/.config", "/home/user/.local", "/home/user/.cache",
            "/tmp", "/root", "/opt", "/srv", "/mnt", "/media",
            "/lib", "/lib64", "/dev", "/proc", "/sys", "/run"
        ]
        
        for d in dirs:
            if d.startswith("/home/user"):
                self.create_directory(d, mode=0o755, uid=1000, gid=1000)
            elif d in ["/tmp", "/var/tmp"]:
                self.create_directory(d, mode=0o1777, uid=0, gid=0)
            else:
                self.create_directory(d, mode=0o755, uid=0, gid=0)
        
        self.create_file("/etc/passwd", self._generate_passwd(), mode=0o644)
        self.create_file("/etc/group", self._generate_group(), mode=0o644)
        self.create_file("/etc/shadow", self._generate_shadow(), mode=0o640)
        self.create_file("/etc/hostname", "pylinux\n", mode=0o644)
        self.create_file("/etc/hosts", "127.0.0.1\tlocalhost\n127.0.1.1\tpylinux\n", mode=0o644)
        self.create_file("/etc/resolv.conf", "nameserver 8.8.8.8\nnameserver 8.8.4.4\n", mode=0o644)
        self.create_file("/etc/fstab", self._generate_fstab(), mode=0o644)
        self.create_file("/etc/os-release", self._generate_os_release(), mode=0o644)
        self.create_file("/etc/issue", "PyLinux 1.0 \\n \\l\n\n", mode=0o644)
        self.create_file("/etc/motd", self._generate_motd(), mode=0o644)
        self.create_file("/etc/shells", "/bin/sh\n/bin/bash\n/bin/dash\n/usr/bin/bash\n", mode=0o644)
        self.create_file("/etc/profile", self._generate_profile(), mode=0o644)
        self.create_file("/etc/bash.bashrc", self._generate_bashrc(), mode=0o644)
        self.create_file("/etc/inputrc", self._generate_inputrc(), mode=0o644)
        self.create_file("/etc/environment", 'PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"\n', mode=0o644)
        self.create_file("/etc/timezone", "UTC\n", mode=0o644)
        self.create_file("/etc/localtime", "", mode=0o644)
        self.create_file("/etc/services", self._generate_services(), mode=0o644)
        self.create_file("/etc/protocols", self._generate_protocols(), mode=0o644)
        
        self.create_file("/var/log/syslog", "", mode=0o640)
        self.create_file("/var/log/auth.log", "", mode=0o640)
        self.create_file("/var/log/kern.log", "", mode=0o640)
        self.create_file("/var/log/dmesg", self._generate_dmesg(), mode=0o644)
        self.create_file("/var/log/wtmp", "", mode=0o664)
        self.create_file("/var/log/lastlog", "", mode=0o644)
        
        self.create_file("/home/user/.bashrc", self._generate_user_bashrc(), mode=0o644, uid=1000, gid=1000)
        self.create_file("/home/user/.bash_profile", self._generate_bash_profile(), mode=0o644, uid=1000, gid=1000)
        self.create_file("/home/user/.profile", self._generate_user_profile(), mode=0o644, uid=1000, gid=1000)
        self.create_file("/home/user/.bash_history", "", mode=0o600, uid=1000, gid=1000)
        self.create_file("/home/user/.bash_logout", "# ~/.bash_logout\nclear\n", mode=0o644, uid=1000, gid=1000)
        
        self._create_proc_entries()
        self._create_dev_entries()
        self._create_sys_entries()
    
    def _generate_passwd(self):
        return """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System:/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
syslog:x:102:106::/home/syslog:/usr/sbin/nologin
messagebus:x:103:107::/nonexistent:/usr/sbin/nologin
user:x:1000:1000:PyLinux User:/home/user:/bin/bash
"""
    
    def _generate_group(self):
        return """root:x:0:
daemon:x:1:
bin:x:2:
sys:x:3:
adm:x:4:user
tty:x:5:
disk:x:6:
lp:x:7:
mail:x:8:
news:x:9:
uucp:x:10:
man:x:12:
proxy:x:13:
kmem:x:15:
dialout:x:20:
fax:x:21:
voice:x:22:
cdrom:x:24:user
floppy:x:25:
tape:x:26:
sudo:x:27:user
audio:x:29:user
dip:x:30:user
www-data:x:33:
backup:x:34:
operator:x:37:
list:x:38:
irc:x:39:
src:x:40:
gnats:x:41:
shadow:x:42:
utmp:x:43:
video:x:44:user
sasl:x:45:
plugdev:x:46:user
staff:x:50:
games:x:60:
users:x:100:
nogroup:x:65534:
user:x:1000:
"""
    
    def _generate_shadow(self):
        return """root:*:19000:0:99999:7:::
daemon:*:19000:0:99999:7:::
bin:*:19000:0:99999:7:::
sys:*:19000:0:99999:7:::
user:$6$rounds=4096$saltsalt$hashedpassword:19000:0:99999:7:::
"""
    
    def _generate_fstab(self):
        return """# /etc/fstab: static file system information.
# <file system> <mount point>   <type>  <options>       <dump>  <pass>
/dev/sda1       /               ext4    errors=remount-ro 0       1
/dev/sda2       none            swap    sw              0       0
proc            /proc           proc    defaults        0       0
sysfs           /sys            sysfs   defaults        0       0
tmpfs           /tmp            tmpfs   defaults        0       0
tmpfs           /run            tmpfs   defaults        0       0
devpts          /dev/pts        devpts  defaults        0       0
"""
    
    def _generate_os_release(self):
        return """NAME="PyLinux"
VERSION="1.0"
ID=pylinux
ID_LIKE=debian
PRETTY_NAME="PyLinux 1.0"
VERSION_ID="1.0"
HOME_URL="https://pylinux.example.com/"
SUPPORT_URL="https://pylinux.example.com/support"
BUG_REPORT_URL="https://pylinux.example.com/bugs"
"""
    
    def _generate_motd(self):
        return """
  ____        _     _                  
 |  _ \\ _   _| |   (_)_ __  _   ___  __
 | |_) | | | | |   | | '_ \\| | | \\ \\/ /
 |  __/| |_| | |___| | | | | |_| |>  < 
 |_|    \\__, |_____|_|_| |_|\\__,_/_/\\_\\
        |___/                          

Welcome to PyLinux 1.0 - A Linux Terminal Emulator
"""
    
    def _generate_profile(self):
        return """if [ -n "$BASH_VERSION" ]; then
    if [ -f "$HOME/.bashrc" ]; then
        . "$HOME/.bashrc"
    fi
fi

if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi

if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi
"""
    
    def _generate_bashrc(self):
        return """export HISTSIZE=1000
export HISTFILESIZE=2000
export HISTCONTROL=ignoreboth
shopt -s histappend
shopt -s checkwinsize
shopt -s globstar

if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
fi

PS1='\\u@\\h:\\w\\$ '
"""
    
    def _generate_inputrc(self):
        return """set bell-style none
set completion-ignore-case on
set show-all-if-ambiguous on
set mark-symlinked-directories on
"\\e[A": history-search-backward
"\\e[B": history-search-forward
"\\e[C": forward-char
"\\e[D": backward-char
"\\e[1;5C": forward-word
"\\e[1;5D": backward-word
"""
    
    def _generate_services(self):
        return """tcpmux          1/tcp
echo            7/tcp
echo            7/udp
discard         9/tcp
discard         9/udp
systat          11/tcp
daytime         13/tcp
daytime         13/udp
netstat         15/tcp
qotd            17/tcp
chargen         19/tcp
chargen         19/udp
ftp-data        20/tcp
ftp             21/tcp
ssh             22/tcp
telnet          23/tcp
smtp            25/tcp
time            37/tcp
time            37/udp
domain          53/tcp
domain          53/udp
bootps          67/udp
bootpc          68/udp
tftp            69/udp
http            80/tcp
kerberos        88/tcp
kerberos        88/udp
pop3            110/tcp
sunrpc          111/tcp
sunrpc          111/udp
nntp            119/tcp
ntp             123/udp
imap            143/tcp
snmp            161/udp
snmptrap        162/udp
ldap            389/tcp
https           443/tcp
ssmtp           465/tcp
submission      587/tcp
ldaps           636/tcp
imaps           993/tcp
pop3s           995/tcp
mysql           3306/tcp
postgresql      5432/tcp
"""
    
    def _generate_protocols(self):
        return """ip      0       IP
hopopt  0       HOPOPT
icmp    1       ICMP
igmp    2       IGMP
ggp     3       GGP
ipencap 4       IP-ENCAP
st      5       ST
tcp     6       TCP
egp     8       EGP
igp     9       IGP
pup     12      PUP
udp     17      UDP
hmp     20      HMP
xns-idp 22      XNS-IDP
rdp     27      RDP
iso-tp4 29      ISO-TP4
dccp    33      DCCP
xtp     36      XTP
ddp     37      DDP
ipv6    41      IPv6
ipv6-route      43      IPv6-Route
ipv6-frag       44      IPv6-Frag
idrp    45      IDRP
rsvp    46      RSVP
gre     47      GRE
esp     50      ESP
ah      51      AH
ipv6-icmp       58      IPv6-ICMP
ipv6-nonxt      59      IPv6-NoNxt
ipv6-opts       60      IPv6-Opts
eigrp   88      EIGRP
ospf    89      OSPF
ax.25   93      AX.25
ipip    94      IPIP
etherip 97      ETHERIP
encap   98      ENCAP
pim     103     PIM
ipcomp  108     IPCOMP
vrrp    112     VRRP
l2tp    115     L2TP
sctp    132     SCTP
udplite 136     UDPLite
mpls-in-ip      137     MPLS-in-IP
"""
    
    def _generate_dmesg(self):
        return """[    0.000000] Linux version 5.15.0-pylinux (gcc version 11.2.0)
[    0.000000] Command line: BOOT_IMAGE=/boot/vmlinuz-5.15.0-pylinux root=/dev/sda1 ro quiet splash
[    0.000000] KERNEL supported cpus:
[    0.000000]   Intel GenuineIntel
[    0.000000]   AMD AuthenticAMD
[    0.000000] BIOS-provided physical RAM map:
[    0.000000] BIOS-e820: [mem 0x0000000000000000-0x000000000009fbff] usable
[    0.000000] BIOS-e820: [mem 0x0000000000100000-0x00000000bfffffff] usable
[    0.000000] NX (Execute Disable) protection: active
[    0.000000] DMI: PyLinux Virtual Machine/Virtual Platform, BIOS 1.0 01/01/2024
[    0.000000] Hypervisor detected: KVM
[    0.000001] tsc: Fast TSC calibration using PIT
[    0.000001] tsc: Detected 2400.000 MHz processor
[    0.001000] Memory: 4096MB available
[    0.001500] CPU: Checking for self-snoop capability
[    0.002000] Calibrating delay loop (skipped), value calculated using timer frequency.. 4800.00 BogoMIPS
[    0.003000] pid_max: default: 32768 minimum: 301
[    0.004000] Mount-cache hash table entries: 4096
[    0.005000] Initializing cgroup subsys memory
[    0.006000] CPU: Physical Processor ID: 0
[    0.007000] mce: CPU supports 6 MCE banks
[    0.008000] Last level iTLB entries: 4KB 512, 2MB 8, 4MB 8
[    0.009000] Last level dTLB entries: 4KB 512, 2MB 32, 4MB 32, 1GB 0
[    0.010000] Freeing SMP alternatives memory: 32K
[    0.011000] smpboot: Estimated ratio of average max frequency by base frequency (times 1024): 1024
[    0.012000] smpboot: Total of 4 processors activated
[    0.013000] devtmpfs: initialized
[    0.014000] clocksource: jiffies: mask: 0xffffffff max_cycles: 0xffffffff
[    0.015000] NET: Registered protocol family 16
[    0.016000] PCI: Using configuration type 1 for base access
[    0.020000] ACPI: All ACPI Tables successfully acquired
[    0.025000] PCI: Probing PCI hardware
[    0.030000] SCSI subsystem initialized
[    0.035000] Block layer SCSI generic driver version 0.4 loaded
[    0.040000] sd 0:0:0:0: [sda] 41943040 512-byte logical blocks: (21.5 GB/20.0 GiB)
[    0.045000] sd 0:0:0:0: [sda] Write Protect is off
[    0.050000] EXT4-fs (sda1): mounted filesystem with ordered data mode
[    0.055000] VFS: Mounted root (ext4 filesystem) readonly on device 8:1
[    0.060000] systemd[1]: Detected virtualization kvm
[    0.065000] systemd[1]: Detected architecture x86-64
[    0.070000] systemd[1]: Set hostname to <pylinux>
"""
    
    def _generate_user_bashrc(self):
        return """case $- in
    *i*) ;;
      *) return;;
esac

HISTCONTROL=ignoreboth
shopt -s histappend
HISTSIZE=1000
HISTFILESIZE=2000
shopt -s checkwinsize

if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

case "$TERM" in
    xterm-color|*-256color) color_prompt=yes;;
esac

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\\[\\033[01;32m\\]\\u@\\h\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\\u@\\h:\\w\\$ '
fi

case "$TERM" in
xterm*|rxvt*)
    PS1="\\[\\e]0;${debian_chroot:+($debian_chroot)}\\u@\\h: \\w\\a\\]$PS1"
    ;;
*)
    ;;
esac

if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias dir='dir --color=auto'
    alias vdir='vdir --color=auto'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi
"""
    
    def _generate_bash_profile(self):
        return """if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi
"""
    
    def _generate_user_profile(self):
        return """if [ -n "$BASH_VERSION" ]; then
    if [ -f "$HOME/.bashrc" ]; then
        . "$HOME/.bashrc"
    fi
fi

if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi

if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi
"""
    
    def _create_proc_entries(self):
        import psutil
        import platform
        import os
        
        mem = psutil.virtual_memory()
        cpu_count = psutil.cpu_count()
        
        meminfo = f"""MemTotal:       {mem.total // 1024} kB
MemFree:        {mem.available // 1024} kB
MemAvailable:   {mem.available // 1024} kB
Buffers:        {getattr(mem, 'buffers', 0) // 1024} kB
Cached:         {getattr(mem, 'cached', 0) // 1024} kB
SwapTotal:      {psutil.swap_memory().total // 1024} kB
SwapFree:       {psutil.swap_memory().free // 1024} kB
"""
        self.create_file("/proc/meminfo", meminfo, mode=0o444)
        
        cpuinfo = ""
        for i in range(cpu_count or 1):
            cpuinfo += f"""processor\t: {i}
vendor_id\t: GenuineIntel
cpu family\t: 6
model\t\t: 158
model name\t: Intel(R) Core(TM) i7-8700 CPU @ 3.20GHz
stepping\t: 10
microcode\t: 0xea
cpu MHz\t\t: 3200.000
cache size\t: 12288 KB
physical id\t: 0
siblings\t: {cpu_count}
core id\t\t: {i}
cpu cores\t: {cpu_count}
apicid\t\t: {i}
fpu\t\t: yes
fpu_exception\t: yes
cpuid level\t: 22
wp\t\t: yes
flags\t\t: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx rdtscp lm constant_tsc rep_good nopl xtopology cpuid pni pclmulqdq ssse3 cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt aes xsave avx f16c rdrand hypervisor lahf_lm abm 3dnowprefetch cpuid_fault pti ssbd ibrs ibpb stibp fsgsbase bmi1 avx2 smep bmi2 erms invpcid rdseed adx smap clflushopt xsaveopt xsavec xgetbv1 xsaves
bogomips\t: 6400.00
clflush size\t: 64
cache_alignment\t: 64
address sizes\t: 40 bits physical, 48 bits virtual
power management:

"""
        self.create_file("/proc/cpuinfo", cpuinfo, mode=0o444)
        
        self.create_file("/proc/version", f"Linux version 5.15.0-pylinux (gcc version 11.2.0) #1 SMP {time.strftime('%a %b %d %H:%M:%S UTC %Y')}\n", mode=0o444)
        self.create_file("/proc/uptime", f"{time.time() % 100000:.2f} {time.time() % 50000:.2f}\n", mode=0o444)
        
        loadavg = os.getloadavg() if hasattr(os, 'getloadavg') else (0.0, 0.0, 0.0)
        self.create_file("/proc/loadavg", f"{loadavg[0]:.2f} {loadavg[1]:.2f} {loadavg[2]:.2f} 1/100 {os.getpid()}\n", mode=0o444)
        
        self.create_file("/proc/stat", self._generate_proc_stat(), mode=0o444)
        self.create_file("/proc/filesystems", "nodev\tsysfs\nnodev\ttmpfs\nnodev\tbdev\nnodev\tproc\nnodev\tcgroup\nnodev\tdevpts\n\text4\nnodev\tnfs\nnodev\tnfs4\n", mode=0o444)
        self.create_file("/proc/mounts", "/dev/sda1 / ext4 rw,relatime 0 0\nproc /proc proc rw,nosuid,nodev,noexec,relatime 0 0\nsysfs /sys sysfs rw,nosuid,nodev,noexec,relatime 0 0\ntmpfs /tmp tmpfs rw,nosuid,nodev 0 0\n", mode=0o444)
        self.create_file("/proc/cmdline", "BOOT_IMAGE=/boot/vmlinuz-5.15.0-pylinux root=/dev/sda1 ro quiet splash\n", mode=0o444)
        self.create_file("/proc/partitions", "major minor  #blocks  name\n\n   8        0   20971520 sda\n   8        1   20970496 sda1\n", mode=0o444)
        self.create_file("/proc/swaps", "Filename\t\t\t\tType\t\tSize\tUsed\tPriority\n/dev/sda2\t\t\t\tpartition\t2097148\t0\t-2\n", mode=0o444)
        self.create_file("/proc/sys/kernel/hostname", "pylinux\n", mode=0o644)
        self.create_file("/proc/sys/kernel/ostype", "Linux\n", mode=0o444)
        self.create_file("/proc/sys/kernel/osrelease", "5.15.0-pylinux\n", mode=0o444)
        self.create_file("/proc/sys/kernel/version", "#1 SMP PREEMPT\n", mode=0o444)
    
    def _generate_proc_stat(self):
        import psutil
        cpu_times = psutil.cpu_times()
        return f"""cpu  {int(cpu_times.user*100)} {int(cpu_times.nice*100) if hasattr(cpu_times, 'nice') else 0} {int(cpu_times.system*100)} {int(cpu_times.idle*100)} {int(cpu_times.iowait*100) if hasattr(cpu_times, 'iowait') else 0} 0 0 0 0 0
cpu0 {int(cpu_times.user*25)} {int(cpu_times.nice*25) if hasattr(cpu_times, 'nice') else 0} {int(cpu_times.system*25)} {int(cpu_times.idle*25)} 0 0 0 0 0 0
intr 0
ctxt 0
btime {int(time.time() - 10000)}
processes 1000
procs_running 1
procs_blocked 0
softirq 0 0 0 0 0 0 0 0 0 0 0
"""
    
    def _create_dev_entries(self):
        devices = [
            ("/dev/null", "c", 1, 3),
            ("/dev/zero", "c", 1, 5),
            ("/dev/full", "c", 1, 7),
            ("/dev/random", "c", 1, 8),
            ("/dev/urandom", "c", 1, 9),
            ("/dev/tty", "c", 5, 0),
            ("/dev/console", "c", 5, 1),
            ("/dev/ptmx", "c", 5, 2),
            ("/dev/tty0", "c", 4, 0),
            ("/dev/tty1", "c", 4, 1),
            ("/dev/sda", "b", 8, 0),
            ("/dev/sda1", "b", 8, 1),
            ("/dev/sda2", "b", 8, 2),
            ("/dev/loop0", "b", 7, 0),
            ("/dev/loop1", "b", 7, 1),
        ]
        
        for path, dev_type, major, minor in devices:
            self.create_device(path, dev_type, major, minor)
    
    def _create_sys_entries(self):
        self.create_directory("/sys/class", mode=0o755, uid=0, gid=0)
        self.create_directory("/sys/class/net", mode=0o755, uid=0, gid=0)
        self.create_directory("/sys/class/net/eth0", mode=0o755, uid=0, gid=0)
        self.create_file("/sys/class/net/eth0/address", "00:00:00:00:00:01\n", mode=0o444)
        self.create_file("/sys/class/net/eth0/mtu", "1500\n", mode=0o444)
        self.create_file("/sys/class/net/eth0/operstate", "up\n", mode=0o444)
        self.create_directory("/sys/class/net/lo", mode=0o755, uid=0, gid=0)
        self.create_file("/sys/class/net/lo/address", "00:00:00:00:00:00\n", mode=0o444)
        self.create_file("/sys/class/net/lo/mtu", "65536\n", mode=0o444)
        self.create_file("/sys/class/net/lo/operstate", "unknown\n", mode=0o444)
        self.create_directory("/sys/devices", mode=0o755, uid=0, gid=0)
        self.create_directory("/sys/kernel", mode=0o755, uid=0, gid=0)
        self.create_directory("/sys/block", mode=0o755, uid=0, gid=0)
        self.create_directory("/sys/block/sda", mode=0o755, uid=0, gid=0)
        self.create_file("/sys/block/sda/size", "41943040\n", mode=0o444)
    
    def create_directory(self, path: str, mode: int = 0o755, uid: int = 0, gid: int = 0) -> bool:
        path = self.normalize_path(path)
        
        if path in self.inodes:
            return False
        
        inode = self.next_inode
        self.next_inode += 1
        
        self.inodes[path] = {
            "inode": inode,
            "type": "directory",
            "mode": mode,
            "uid": uid,
            "gid": gid,
            "size": 4096,
            "atime": time.time(),
            "mtime": time.time(),
            "ctime": time.time(),
            "nlink": 2,
            "children": {}
        }
        
        if path != "/":
            parent = os.path.dirname(path)
            if parent in self.inodes:
                name = os.path.basename(path)
                self.inodes[parent]["children"][name] = path
                self.inodes[parent]["nlink"] += 1
        
        return True
    
    def create_file(self, path: str, content: str = "", mode: int = 0o644, uid: int = 0, gid: int = 0) -> bool:
        path = self.normalize_path(path)
        
        parent = os.path.dirname(path)
        if parent and parent not in self.inodes:
            return False
        
        inode = self.next_inode
        self.next_inode += 1
        
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        self.inodes[path] = {
            "inode": inode,
            "type": "file",
            "mode": mode,
            "uid": uid,
            "gid": gid,
            "size": len(content),
            "atime": time.time(),
            "mtime": time.time(),
            "ctime": time.time(),
            "nlink": 1,
            "content": content
        }
        
        if parent in self.inodes:
            name = os.path.basename(path)
            self.inodes[parent]["children"][name] = path
        
        return True
    
    def create_device(self, path: str, dev_type: str, major: int, minor: int, mode: int = 0o666):
        path = self.normalize_path(path)
        
        inode = self.next_inode
        self.next_inode += 1
        
        self.inodes[path] = {
            "inode": inode,
            "type": "device",
            "dev_type": dev_type,
            "major": major,
            "minor": minor,
            "mode": mode,
            "uid": 0,
            "gid": 0,
            "size": 0,
            "atime": time.time(),
            "mtime": time.time(),
            "ctime": time.time(),
            "nlink": 1
        }
        
        parent = os.path.dirname(path)
        if parent in self.inodes:
            name = os.path.basename(path)
            self.inodes[parent]["children"][name] = path
    
    def create_symlink(self, path: str, target: str, uid: int = 0, gid: int = 0) -> bool:
        path = self.normalize_path(path)
        
        inode = self.next_inode
        self.next_inode += 1
        
        self.inodes[path] = {
            "inode": inode,
            "type": "symlink",
            "mode": 0o777,
            "uid": uid,
            "gid": gid,
            "size": len(target),
            "atime": time.time(),
            "mtime": time.time(),
            "ctime": time.time(),
            "nlink": 1,
            "target": target
        }
        
        parent = os.path.dirname(path)
        if parent in self.inodes:
            name = os.path.basename(path)
            self.inodes[parent]["children"][name] = path
        
        self.symlinks[path] = target
        return True
    
    def normalize_path(self, path: str, base: str = "/") -> str:
        if not path:
            return base
        
        if not path.startswith("/"):
            path = os.path.join(base, path)
        
        parts = []
        for part in path.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part and part != ".":
                parts.append(part)
        
        return "/" + "/".join(parts) if parts else "/"
    
    def resolve_symlink(self, path: str, max_depth: int = 10) -> str:
        depth = 0
        while depth < max_depth:
            if path not in self.inodes:
                return path
            
            inode = self.inodes[path]
            if inode["type"] != "symlink":
                return path
            
            target = inode["target"]
            if not target.startswith("/"):
                target = self.normalize_path(target, os.path.dirname(path))
            path = target
            depth += 1
        
        return path
    
    def exists(self, path: str) -> bool:
        path = self.normalize_path(path)
        return path in self.inodes
    
    def is_directory(self, path: str) -> bool:
        path = self.normalize_path(path)
        path = self.resolve_symlink(path)
        return path in self.inodes and self.inodes[path]["type"] == "directory"
    
    def is_file(self, path: str) -> bool:
        path = self.normalize_path(path)
        path = self.resolve_symlink(path)
        return path in self.inodes and self.inodes[path]["type"] == "file"
    
    def read_file(self, path: str) -> Optional[bytes]:
        path = self.normalize_path(path)
        path = self.resolve_symlink(path)
        
        if path not in self.inodes:
            return None
        
        inode = self.inodes[path]
        if inode["type"] != "file":
            return None
        
        inode["atime"] = time.time()
        return inode.get("content", b"")
    
    def write_file(self, path: str, content: bytes, append: bool = False) -> bool:
        path = self.normalize_path(path)
        
        if path in self.inodes:
            inode = self.inodes[path]
            if inode["type"] != "file":
                return False
            
            if append:
                inode["content"] = inode.get("content", b"") + content
            else:
                inode["content"] = content
            
            inode["size"] = len(inode["content"])
            inode["mtime"] = time.time()
            return True
        else:
            return self.create_file(path, content)
    
    def delete(self, path: str, recursive: bool = False) -> bool:
        path = self.normalize_path(path)
        
        if path == "/" or path not in self.inodes:
            return False
        
        inode = self.inodes[path]
        
        if inode["type"] == "directory":
            if inode["children"] and not recursive:
                return False
            
            if recursive:
                for child_name in list(inode["children"].keys()):
                    child_path = inode["children"][child_name]
                    self.delete(child_path, recursive=True)
        
        parent = os.path.dirname(path)
        if parent in self.inodes:
            name = os.path.basename(path)
            if name in self.inodes[parent]["children"]:
                del self.inodes[parent]["children"][name]
                if inode["type"] == "directory":
                    self.inodes[parent]["nlink"] -= 1
        
        del self.inodes[path]
        return True
    
    def move(self, src: str, dst: str) -> bool:
        src = self.normalize_path(src)
        dst = self.normalize_path(dst)
        
        if src not in self.inodes:
            return False
        
        if self.is_directory(dst):
            dst = os.path.join(dst, os.path.basename(src))
        
        inode = self.inodes[src]
        
        src_parent = os.path.dirname(src)
        if src_parent in self.inodes:
            name = os.path.basename(src)
            if name in self.inodes[src_parent]["children"]:
                del self.inodes[src_parent]["children"][name]
        
        self.inodes[dst] = inode
        del self.inodes[src]
        
        dst_parent = os.path.dirname(dst)
        if dst_parent in self.inodes:
            name = os.path.basename(dst)
            self.inodes[dst_parent]["children"][name] = dst
        
        inode["ctime"] = time.time()
        
        return True
    
    def copy(self, src: str, dst: str, recursive: bool = False) -> bool:
        src = self.normalize_path(src)
        dst = self.normalize_path(dst)
        
        if src not in self.inodes:
            return False
        
        src_inode = self.inodes[src]
        
        if self.is_directory(dst):
            dst = os.path.join(dst, os.path.basename(src))
        
        if src_inode["type"] == "directory":
            if not recursive:
                return False
            
            self.create_directory(dst, src_inode["mode"], src_inode["uid"], src_inode["gid"])
            
            for child_name in src_inode["children"]:
                child_src = src_inode["children"][child_name]
                child_dst = os.path.join(dst, child_name)
                self.copy(child_src, child_dst, recursive=True)
        else:
            content = src_inode.get("content", b"")
            self.create_file(dst, content, src_inode["mode"], src_inode["uid"], src_inode["gid"])
        
        return True
    
    def list_directory(self, path: str) -> Optional[List[Dict]]:
        path = self.normalize_path(path)
        path = self.resolve_symlink(path)
        
        if path not in self.inodes:
            return None
        
        inode = self.inodes[path]
        if inode["type"] != "directory":
            return None
        
        inode["atime"] = time.time()
        
        entries = []
        for name, child_path in inode["children"].items():
            if child_path in self.inodes:
                child_inode = self.inodes[child_path]
                entries.append({
                    "name": name,
                    "path": child_path,
                    "type": child_inode["type"],
                    "mode": child_inode["mode"],
                    "uid": child_inode["uid"],
                    "gid": child_inode["gid"],
                    "size": child_inode["size"],
                    "mtime": child_inode["mtime"],
                    "nlink": child_inode.get("nlink", 1),
                    "inode": child_inode["inode"]
                })
        
        return entries
    
    def get_stat(self, path: str) -> Optional[Dict]:
        path = self.normalize_path(path)
        
        if path not in self.inodes:
            return None
        
        inode = self.inodes[path]
        return {
            "inode": inode["inode"],
            "type": inode["type"],
            "mode": inode["mode"],
            "uid": inode["uid"],
            "gid": inode["gid"],
            "size": inode["size"],
            "atime": inode["atime"],
            "mtime": inode["mtime"],
            "ctime": inode["ctime"],
            "nlink": inode.get("nlink", 1),
            "target": inode.get("target")
        }
    
    def chmod(self, path: str, mode: int) -> bool:
        path = self.normalize_path(path)
        
        if path not in self.inodes:
            return False
        
        self.inodes[path]["mode"] = mode
        self.inodes[path]["ctime"] = time.time()
        return True
    
    def chown(self, path: str, uid: int = None, gid: int = None) -> bool:
        path = self.normalize_path(path)
        
        if path not in self.inodes:
            return False
        
        if uid is not None:
            self.inodes[path]["uid"] = uid
        if gid is not None:
            self.inodes[path]["gid"] = gid
        self.inodes[path]["ctime"] = time.time()
        return True
    
    def touch(self, path: str) -> bool:
        path = self.normalize_path(path)
        
        if path in self.inodes:
            self.inodes[path]["atime"] = time.time()
            self.inodes[path]["mtime"] = time.time()
            return True
        else:
            return self.create_file(path, "")
    
    def get_disk_usage(self, path: str = "/") -> Dict:
        total_size = 0
        file_count = 0
        dir_count = 0
        
        path = self.normalize_path(path)
        
        for inode_path, inode in self.inodes.items():
            if inode_path.startswith(path) or path == "/":
                if inode["type"] == "file":
                    total_size += inode["size"]
                    file_count += 1
                elif inode["type"] == "directory":
                    dir_count += 1
        
        return {
            "total_size": total_size,
            "file_count": file_count,
            "dir_count": dir_count
        }
    
    def export_to_indexeddb(self) -> Dict:
        export_data = {}
        
        for path, inode in self.inodes.items():
            if path.startswith("/home/user") or path.startswith("/tmp"):
                export_entry = {
                    "type": inode["type"],
                    "mode": inode["mode"],
                    "uid": inode["uid"],
                    "gid": inode["gid"],
                    "mtime": inode["mtime"]
                }
                
                if inode["type"] == "file":
                    content = inode.get("content", b"")
                    if isinstance(content, bytes):
                        export_entry["content"] = base64.b64encode(content).decode('utf-8')
                    else:
                        export_entry["content"] = base64.b64encode(content.encode('utf-8')).decode('utf-8')
                elif inode["type"] == "symlink":
                    export_entry["target"] = inode.get("target", "")
                
                export_data[path] = export_entry
        
        return export_data
    
    def sync_from_indexeddb(self, data: Dict):
        for path, entry in data.items():
            if entry["type"] == "directory":
                if path not in self.inodes:
                    self.create_directory(path, entry.get("mode", 0o755), entry.get("uid", 1000), entry.get("gid", 1000))
            elif entry["type"] == "file":
                content = base64.b64decode(entry.get("content", ""))
                if path in self.inodes:
                    self.inodes[path]["content"] = content
                    self.inodes[path]["size"] = len(content)
                    self.inodes[path]["mtime"] = entry.get("mtime", time.time())
                else:
                    self.create_file(path, content, entry.get("mode", 0o644), entry.get("uid", 1000), entry.get("gid", 1000))
            elif entry["type"] == "symlink":
                if path not in self.inodes:
                    self.create_symlink(path, entry.get("target", ""), entry.get("uid", 1000), entry.get("gid", 1000))
