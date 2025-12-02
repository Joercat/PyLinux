import time
import random

class PackageManager:
    def __init__(self, filesystem):
        self.filesystem = filesystem
        self.installed_packages = {}
        self.available_packages = {}
        self.initialize_packages()

    def initialize_packages(self):
        self.installed_packages = {
            'apt': {'version': '2.2.4', 'size': 4096, 'description': 'Advanced Package Tool'},
            'base-files': {'version': '11.1', 'size': 340, 'description': 'Debian base system miscellaneous files'},
            'base-passwd': {'version': '3.5.51', 'size': 235, 'description': 'Debian base system master password and group files'},
            'bash': {'version': '5.1-6', 'size': 6416, 'description': 'GNU Bourne Again SHell'},
            'bsdutils': {'version': '2.37.2', 'size': 304, 'description': 'basic utilities from 4.4BSD-Lite'},
            'coreutils': {'version': '8.32-4', 'size': 17840, 'description': 'GNU core utilities'},
            'dash': {'version': '0.5.11', 'size': 192, 'description': 'POSIX-compliant shell'},
            'diffutils': {'version': '3.7-5', 'size': 1568, 'description': 'File comparison utilities'},
            'dpkg': {'version': '1.20.12', 'size': 6600, 'description': 'Debian package management system'},
            'e2fsprogs': {'version': '1.46.5', 'size': 1524, 'description': 'ext2/ext3/ext4 file system utilities'},
            'findutils': {'version': '4.8.0-1', 'size': 1800, 'description': 'utilities for finding files'},
            'gcc-10-base': {'version': '10.2.1', 'size': 260, 'description': 'GCC base package'},
            'grep': {'version': '3.6-1', 'size': 1336, 'description': 'GNU grep, egrep and fgrep'},
            'gzip': {'version': '1.10-4', 'size': 240, 'description': 'GNU compression utilities'},
            'hostname': {'version': '3.23', 'size': 52, 'description': 'utility to set/show the host name or domain name'},
            'init-system-helpers': {'version': '1.60', 'size': 132, 'description': 'helper tools for all init systems'},
            'libacl1': {'version': '2.2.53-10', 'size': 72, 'description': 'access control list - shared library'},
            'libc-bin': {'version': '2.31-13', 'size': 3320, 'description': 'GNU C Library: Binaries'},
            'libc6': {'version': '2.31-13', 'size': 12144, 'description': 'GNU C Library: Shared libraries'},
            'libcap-ng0': {'version': '0.7.9-2.2', 'size': 44, 'description': 'alternate POSIX capabilities library'},
            'libgcc-s1': {'version': '10.2.1-6', 'size': 112, 'description': 'GCC support library'},
            'libncurses6': {'version': '6.2', 'size': 296, 'description': 'shared libraries for terminal handling'},
            'libncursesw6': {'version': '6.2', 'size': 412, 'description': 'shared libraries for terminal handling (wide character)'},
            'libpam-runtime': {'version': '1.4.0-9', 'size': 1060, 'description': 'Runtime support for the PAM library'},
            'libpam0g': {'version': '1.4.0-9', 'size': 220, 'description': 'Pluggable Authentication Modules library'},
            'libpcre2-8-0': {'version': '10.36-2', 'size': 560, 'description': 'New Perl Compatible Regular Expression Library'},
            'libselinux1': {'version': '3.1-3', 'size': 168, 'description': 'SELinux runtime shared libraries'},
            'libsystemd0': {'version': '247.3-7', 'size': 916, 'description': 'systemd utility library'},
            'libtinfo6': {'version': '6.2', 'size': 544, 'description': 'shared low-level terminfo library'},
            'login': {'version': '4.8.1-1', 'size': 1020, 'description': 'system login tools'},
            'mawk': {'version': '1.3.4', 'size': 196, 'description': 'Pattern scanning and text processing language'},
            'ncurses-base': {'version': '6.2', 'size': 404, 'description': 'basic terminal type definitions'},
            'ncurses-bin': {'version': '6.2', 'size': 624, 'description': 'terminal-related programs and man pages'},
            'passwd': {'version': '4.8.1-1', 'size': 2356, 'description': 'change and administer password and group data'},
            'perl-base': {'version': '5.32.1-4', 'size': 7908, 'description': 'minimal Perl system'},
            'procps': {'version': '3.3.17-5', 'size': 1208, 'description': '/proc file system utilities'},
            'sed': {'version': '4.7-1', 'size': 720, 'description': 'GNU sed stream editor'},
            'sensible-utils': {'version': '0.0.14', 'size': 68, 'description': 'Utilities for sensible alternative selection'},
            'systemd': {'version': '247.3-7', 'size': 16544, 'description': 'system and service manager'},
            'systemd-sysv': {'version': '247.3-7', 'size': 132, 'description': 'system and service manager - SysV links'},
            'sysvinit-utils': {'version': '2.96-7', 'size': 128, 'description': 'System-V-like utilities'},
            'tar': {'version': '1.34', 'size': 2928, 'description': 'GNU version of the tar archiving utility'},
            'util-linux': {'version': '2.37.2', 'size': 4472, 'description': 'miscellaneous system utilities'},
            'zlib1g': {'version': '1.2.11', 'size': 164, 'description': 'compression library - runtime'},
            'openssh-server': {'version': '8.4p1-5', 'size': 1576, 'description': 'secure shell (SSH) server'},
            'openssh-client': {'version': '8.4p1-5', 'size': 1996, 'description': 'secure shell (SSH) client'},
            'openssl': {'version': '1.1.1k-1', 'size': 1840, 'description': 'Secure Sockets Layer toolkit'},
            'curl': {'version': '7.74.0-1.3', 'size': 392, 'description': 'command line tool for transferring data with URL syntax'},
            'wget': {'version': '1.21-1', 'size': 976, 'description': 'retrieves files from the web'},
            'nano': {'version': '5.4-2', 'size': 856, 'description': 'small, friendly text editor'},
            'vim-tiny': {'version': '8.2.2434-3', 'size': 1660, 'description': 'Vi IMproved - tiny version'},
            'less': {'version': '551-2', 'size': 296, 'description': 'pager program similar to more'},
            'man-db': {'version': '2.9.4-2', 'size': 1744, 'description': 'tools for reading manual pages'},
            'net-tools': {'version': '1.60', 'size': 800, 'description': 'NET-3 networking toolkit'},
            'iproute2': {'version': '5.10.0-4', 'size': 2464, 'description': 'networking and traffic control tools'},
            'iputils-ping': {'version': '20210202-1', 'size': 124, 'description': 'Tools to test the reachability of network hosts'},
            'dnsutils': {'version': '9.16.22-1', 'size': 548, 'description': 'Clients provided with BIND 9'},
            'traceroute': {'version': '2.1.0-2', 'size': 128, 'description': 'Traces the route taken by packets'},
            'rsync': {'version': '3.2.3-4', 'size': 740, 'description': 'fast, versatile, remote file-copying tool'},
            'git': {'version': '2.30.2-1', 'size': 38912, 'description': 'fast, scalable, distributed revision control system'},
            'python3': {'version': '3.9.2-3', 'size': 316, 'description': 'interactive high-level object-oriented language'},
            'python3-minimal': {'version': '3.9.2-3', 'size': 140, 'description': 'minimal subset of the Python language'},
            'sudo': {'version': '1.9.5p2-3', 'size': 5020, 'description': 'Provide limited super user privileges'},
            'ca-certificates': {'version': '20210119', 'size': 384, 'description': 'Common CA certificates'},
            'gnupg': {'version': '2.2.27-2', 'size': 1376, 'description': 'GNU privacy guard'}
        }
        
        self.available_packages = {
            'nginx': {'version': '1.18.0-6.1', 'size': 2080, 'description': 'small, powerful, scalable web/proxy server'},
            'apache2': {'version': '2.4.51-1', 'size': 548, 'description': 'Apache HTTP Server'},
            'mysql-server': {'version': '8.0.27-1', 'size': 24576, 'description': 'MySQL database server'},
            'postgresql': {'version': '13+225', 'size': 192, 'description': 'object-relational SQL database'},
            'redis-server': {'version': '6.0.16-1', 'size': 1024, 'description': 'Persistent key-value database with network interface'},
            'mongodb': {'version': '5.0.3', 'size': 70656, 'description': 'object/document-oriented database'},
            'nodejs': {'version': '16.13.0', 'size': 27648, 'description': 'Node.js event-based server-side javascript engine'},
            'npm': {'version': '8.1.0', 'size': 4096, 'description': 'package manager for Node.js'},
            'docker.io': {'version': '20.10.10', 'size': 88064, 'description': 'Linux container runtime'},
            'docker-compose': {'version': '1.29.2', 'size': 9216, 'description': 'Punctual, lightweight development environments using Docker'},
            'ansible': {'version': '2.10.7', 'size': 17408, 'description': 'Configuration management, deployment, and task execution system'},
            'terraform': {'version': '1.0.11', 'size': 33792, 'description': 'Tool for building, changing, and versioning infrastructure'},
            'kubectl': {'version': '1.22.3', 'size': 44032, 'description': 'Kubernetes command line tool'},
            'helm': {'version': '3.7.1', 'size': 13312, 'description': 'Kubernetes package manager'},
            'htop': {'version': '3.1.2', 'size': 256, 'description': 'interactive processes viewer'},
            'tmux': {'version': '3.2a-4', 'size': 992, 'description': 'terminal multiplexer'},
            'screen': {'version': '4.8.0-6', 'size': 1008, 'description': 'terminal multiplexer with VT100/ANSI terminal emulation'},
            'zsh': {'version': '5.8-6', 'size': 2304, 'description': 'shell with lots of features'},
            'fish': {'version': '3.3.1', 'size': 9728, 'description': 'friendly interactive shell'},
            'neovim': {'version': '0.5.1-4', 'size': 9216, 'description': 'heavily refactored vim fork'},
            'emacs': {'version': '27.1', 'size': 128000, 'description': 'GNU Emacs editor'},
            'gcc': {'version': '10.2.1-6', 'size': 36864, 'description': 'GNU C compiler'},
            'g++': {'version': '10.2.1-6', 'size': 36864, 'description': 'GNU C++ compiler'},
            'make': {'version': '4.3-4.1', 'size': 1440, 'description': 'utility for directing compilation'},
            'cmake': {'version': '3.18.4-2', 'size': 28672, 'description': 'cross-platform, open-source make system'},
            'clang': {'version': '11.0.1-2', 'size': 92160, 'description': 'C, C++ and Objective-C compiler'},
            'golang': {'version': '1.17.3', 'size': 131072, 'description': 'Go programming language compiler'},
            'rustc': {'version': '1.56.1', 'size': 286720, 'description': 'Rust systems programming language'},
            'ruby': {'version': '2.7.4', 'size': 11264, 'description': 'Interpreter of object-oriented scripting language Ruby'},
            'php': {'version': '7.4.25', 'size': 5120, 'description': 'server-side, HTML-embedded scripting language'},
            'openjdk-11-jdk': {'version': '11.0.13', 'size': 237568, 'description': 'OpenJDK Development Kit (JDK)'},
            'maven': {'version': '3.6.3-5', 'size': 10240, 'description': 'Java software project management and comprehension tool'},
            'gradle': {'version': '7.3', 'size': 122880, 'description': 'Powerful build system for the JVM'},
            'ffmpeg': {'version': '4.3.3-0', 'size': 3072, 'description': 'Tools for transcoding, streaming and playing multimedia'},
            'imagemagick': {'version': '6.9.11.60', 'size': 3584, 'description': 'image manipulation programs'},
            'pandoc': {'version': '2.14.2', 'size': 57344, 'description': 'general markup converter'},
            'texlive': {'version': '2020.20210202-3', 'size': 262144, 'description': 'TeX Live: A decent selection of the TeX Live packages'},
            'fail2ban': {'version': '0.11.2-2', 'size': 2048, 'description': 'ban hosts that cause multiple authentication errors'},
            'ufw': {'version': '0.36-7.1', 'size': 840, 'description': 'program for managing a Netfilter firewall'},
            'certbot': {'version': '1.21.0-1', 'size': 768, 'description': 'automatically configure HTTPS using Let\'s Encrypt'},
            'logrotate': {'version': '3.18.0-2', 'size': 168, 'description': 'Log rotation utility'},
            'cron': {'version': '3.0pl1-137', 'size': 228, 'description': 'process scheduling daemon'},
            'at': {'version': '3.2.2-1', 'size': 156, 'description': 'Delayed job execution and batch processing'},
            'ntp': {'version': '4.2.8p15', 'size': 2048, 'description': 'Network Time Protocol daemon and utility programs'},
            'chrony': {'version': '4.1-1', 'size': 512, 'description': 'Versatile implementation of the Network Time Protocol'},
            'tree': {'version': '1.8.0-1', 'size': 96, 'description': 'displays an indented directory tree'},
            'ncdu': {'version': '1.15.1-1', 'size': 112, 'description': 'ncurses disk usage viewer'},
            'iotop': {'version': '0.6-24', 'size': 60, 'description': 'simple top-like I/O monitor'},
            'iftop': {'version': '1.0pre4-7', 'size': 80, 'description': 'displays bandwidth usage on an interface'},
            'nethogs': {'version': '0.8.6-1', 'size': 76, 'description': 'Net top tool grouping bandwidth per process'},
            'sysstat': {'version': '12.4.3-1', 'size': 1024, 'description': 'system performance tools for Linux'},
            'strace': {'version': '5.10-1', 'size': 1536, 'description': 'System call tracer'},
            'ltrace': {'version': '0.7.3-6.1', 'size': 360, 'description': 'Tracks runtime library calls in dynamically linked programs'},
            'gdb': {'version': '10.1-2', 'size': 8192, 'description': 'GNU Debugger'},
            'valgrind': {'version': '3.16.1-1', 'size': 27648, 'description': 'instrumentation framework for building dynamic analysis tools'},
            'perf': {'version': '5.10.70', 'size': 4096, 'description': 'Linux kernel performance analysis tool'}
        }
        
        self.available_packages.update(self.installed_packages)

    def apt(self, args):
        if not args:
            return self._apt_help()
        
        command = args[0]
        packages = args[1:] if len(args) > 1 else []
        
        if command == 'update':
            return self._update()
        elif command == 'upgrade':
            return self._upgrade(packages)
        elif command == 'full-upgrade' or command == 'dist-upgrade':
            return self._upgrade(packages, full=True)
        elif command == 'install':
            return self._install(packages)
        elif command == 'remove':
            return self._remove(packages)
        elif command == 'purge':
            return self._remove(packages, purge=True)
        elif command == 'autoremove':
            return self._autoremove()
        elif command == 'search':
            return self._search(packages)
        elif command == 'show':
            return self._show(packages)
        elif command == 'list':
            return self._list(packages)
        elif command == 'clean':
            return self._clean()
        elif command == 'autoclean':
            return self._clean()
        
        return f"apt: unknown command '{command}'\n"

    def apt_get(self, args):
        return self.apt(args)

    def apt_cache(self, args):
        if not args:
            return "apt-cache: missing command\n"
        
        command = args[0]
        packages = args[1:] if len(args) > 1 else []
        
        if command == 'search':
            return self._search(packages)
        elif command == 'show':
            return self._show(packages)
        elif command == 'policy':
            return self._policy(packages)
        elif command == 'depends':
            return self._depends(packages)
        elif command == 'rdepends':
            return self._rdepends(packages)
        elif command == 'stats':
            return self._stats()
        
        return f"apt-cache: unknown command '{command}'\n"

    def dpkg(self, args):
        if not args:
            return "dpkg: missing command\n"
        
        command = args[0]
        
        if command == '-l' or command == '--list':
            return self._dpkg_list(args[1:])
        elif command == '-L' or command == '--listfiles':
            return self._dpkg_listfiles(args[1:])
        elif command == '-s' or command == '--status':
            return self._dpkg_status(args[1:])
        elif command == '-S' or command == '--search':
            return self._dpkg_search(args[1:])
        elif command == '-i' or command == '--install':
            return "dpkg: package installation from file not supported\n"
        elif command == '-r' or command == '--remove':
            return self._remove(args[1:])
        elif command == '-P' or command == '--purge':
            return self._remove(args[1:], purge=True)
        elif command == '--configure':
            return "dpkg: configuring packages...\n"
        elif command == '--get-selections':
            output = ""
            for pkg in self.installed_packages:
                output += f"{pkg}\t\t\t\t\tinstall\n"
            return output
        
        return f"dpkg: unknown option '{command}'\n"

    def _apt_help(self):
        return """apt 2.2.4 (amd64)
Usage: apt [options] command

Most used commands:
  list - list packages based on package names
  search - search in package descriptions
  show - show package details
  install - install packages
  reinstall - reinstall packages
  remove - remove packages
  autoremove - Remove automatically all unused packages
  update - update list of available packages
  upgrade - upgrade the system by installing/upgrading packages
  full-upgrade - upgrade the system by removing/installing/upgrading packages
  edit-sources - edit the source information file
  satisfy - satisfy dependency strings

See apt(8) for more information about the available commands.
"""

    def _update(self):
        output = "Hit:1 http://deb.pylinux.org/pylinux stable InRelease\n"
        output += "Hit:2 http://security.pylinux.org/pylinux-security stable-security InRelease\n"
        output += f"Reading package lists... Done\n"
        output += f"Building dependency tree... Done\n"
        output += f"Reading state information... Done\n"
        output += f"All packages are up to date.\n"
        return output

    def _upgrade(self, packages, full=False):
        output = "Reading package lists... Done\n"
        output += "Building dependency tree... Done\n"
        output += "Reading state information... Done\n"
        output += "Calculating upgrade... Done\n"
        
        upgradable = random.randint(0, 5)
        if upgradable > 0:
            output += f"{upgradable} upgraded, 0 newly installed, 0 to remove and 0 not upgraded.\n"
            output += f"Need to get {random.randint(100, 1000)} kB of archives.\n"
            output += f"After this operation, {random.randint(0, 100)} kB of additional disk space will be used.\n"
            for _ in range(upgradable):
                pkg = random.choice(list(self.installed_packages.keys()))
                output += f"Setting up {pkg} ...\n"
        else:
            output += "0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.\n"
        
        return output

    def _install(self, packages):
        if not packages:
            return "apt: missing package name(s)\n"
        
        output = "Reading package lists... Done\n"
        output += "Building dependency tree... Done\n"
        output += "Reading state information... Done\n"
        
        to_install = []
        not_found = []
        already_installed = []
        
        for pkg in packages:
            if pkg.startswith('-'):
                continue
            if pkg in self.installed_packages:
                already_installed.append(pkg)
            elif pkg in self.available_packages:
                to_install.append(pkg)
            else:
                not_found.append(pkg)
        
        if not_found:
            output += f"E: Unable to locate package {not_found[0]}\n"
            return output
        
        if already_installed and not to_install:
            output += f"{already_installed[0]} is already the newest version ({self.installed_packages[already_installed[0]]['version']}).\n"
            output += "0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.\n"
            return output
        
        if to_install:
            total_size = sum(self.available_packages[p]['size'] for p in to_install)
            output += f"The following NEW packages will be installed:\n"
            output += f"  {' '.join(to_install)}\n"
            output += f"0 upgraded, {len(to_install)} newly installed, 0 to remove and 0 not upgraded.\n"
            output += f"Need to get {total_size} kB of archives.\n"
            output += f"After this operation, {total_size * 3} kB of additional disk space will be used.\n"
            
            for pkg in to_install:
                pkg_info = self.available_packages[pkg]
                output += f"Get:1 http://deb.pylinux.org/pylinux stable/main amd64 {pkg} amd64 {pkg_info['version']} [{pkg_info['size']} kB]\n"
            
            output += f"Fetched {total_size} kB in 1s ({total_size} kB/s)\n"
            output += "Selecting previously unselected packages.\n"
            
            for pkg in to_install:
                output += f"Preparing to unpack .../{pkg}.deb ...\n"
                output += f"Unpacking {pkg} ({self.available_packages[pkg]['version']}) ...\n"
            
            for pkg in to_install:
                output += f"Setting up {pkg} ({self.available_packages[pkg]['version']}) ...\n"
                self.installed_packages[pkg] = self.available_packages[pkg].copy()
            
            output += "Processing triggers for man-db ...\n"
        
        return output

    def _remove(self, packages, purge=False):
        if not packages:
            return "apt: missing package name(s)\n"
        
        output = "Reading package lists... Done\n"
        output += "Building dependency tree... Done\n"
        output += "Reading state information... Done\n"
        
        to_remove = []
        not_installed = []
        
        for pkg in packages:
            if pkg.startswith('-'):
                continue
            if pkg in self.installed_packages:
                to_remove.append(pkg)
            else:
                not_installed.append(pkg)
        
        if not_installed:
            output += f"Package '{not_installed[0]}' is not installed, so not removed\n"
        
        if to_remove:
            total_size = sum(self.installed_packages[p]['size'] for p in to_remove)
            output += f"The following packages will be REMOVED:\n"
            output += f"  {' '.join(to_remove)}\n"
            output += f"0 upgraded, 0 newly installed, {len(to_remove)} to remove and 0 not upgraded.\n"
            output += f"After this operation, {total_size * 3} kB disk space will be freed.\n"
            
            for pkg in to_remove:
                action = "Purging" if purge else "Removing"
                output += f"{action} {pkg} ({self.installed_packages[pkg]['version']}) ...\n"
                del self.installed_packages[pkg]
            
            output += "Processing triggers for man-db ...\n"
        else:
            output += "0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.\n"
        
        return output

    def _autoremove(self):
        output = "Reading package lists... Done\n"
        output += "Building dependency tree... Done\n"
        output += "Reading state information... Done\n"
        output += "0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.\n"
        return output

    def _search(self, terms):
        if not terms:
            return ""
        
        output = ""
        search_term = terms[0].lower()
        
        for pkg, info in self.available_packages.items():
            if search_term in pkg.lower() or search_term in info['description'].lower():
                installed = " [installed]" if pkg in self.installed_packages else ""
                output += f"{pkg}/{info['version']} - {info['description']}{installed}\n"
        
        return output if output else f"No packages found matching '{terms[0]}'\n"

    def _show(self, packages):
        if not packages:
            return "apt: missing package name\n"
        
        output = ""
        for pkg in packages:
            if pkg.startswith('-'):
                continue
            if pkg in self.available_packages:
                info = self.available_packages[pkg]
                output += f"Package: {pkg}\n"
                output += f"Version: {info['version']}\n"
                output += f"Priority: optional\n"
                output += f"Section: {'base' if pkg in self.installed_packages else 'universe'}\n"
                output += f"Maintainer: PyLinux Developers <dev@pylinux.org>\n"
                output += f"Installed-Size: {info['size']}\n"
                output += f"Download-Size: {info['size'] // 3} kB\n"
                output += f"APT-Sources: http://deb.pylinux.org/pylinux stable/main amd64 Packages\n"
                output += f"Description: {info['description']}\n"
                output += "\n"
            else:
                output += f"N: Unable to locate package {pkg}\n"
        
        return output

    def _list(self, args):
        installed_only = '--installed' in args
        upgradable = '--upgradable' in args
        
        output = "Listing...\n"
        
        packages = self.installed_packages if installed_only else self.available_packages
        
        for pkg, info in sorted(packages.items()):
            installed = "[installed]" if pkg in self.installed_packages else ""
            if not installed_only or installed:
                output += f"{pkg}/{info['version']} amd64 {installed}\n"
        
        return output

    def _clean(self):
        return ""

    def _policy(self, packages):
        if not packages:
            return "apt-cache: missing package name\n"
        
        output = ""
        for pkg in packages:
            if pkg in self.available_packages:
                info = self.available_packages[pkg]
                installed = f"Installed: {info['version']}" if pkg in self.installed_packages else "Installed: (none)"
                output += f"{pkg}:\n"
                output += f"  {installed}\n"
                output += f"  Candidate: {info['version']}\n"
                output += f"  Version table:\n"
                if pkg in self.installed_packages:
                    output += f" *** {info['version']} 500\n"
                else:
                    output += f"     {info['version']} 500\n"
                output += f"        500 http://deb.pylinux.org/pylinux stable/main amd64 Packages\n"
            else:
                output += f"N: Unable to locate package {pkg}\n"
        
        return output

    def _depends(self, packages):
        if not packages:
            return "apt-cache: missing package name\n"
        
        output = ""
        common_deps = ['libc6', 'libgcc-s1', 'libstdc++6', 'zlib1g']
        
        for pkg in packages:
            if pkg in self.available_packages:
                output += f"{pkg}\n"
                for dep in random.sample(common_deps, min(len(common_deps), random.randint(1, 3))):
                    output += f"  Depends: {dep}\n"
            else:
                output += f"N: Unable to locate package {pkg}\n"
        
        return output

    def _rdepends(self, packages):
        if not packages:
            return "apt-cache: missing package name\n"
        
        output = ""
        for pkg in packages:
            if pkg in self.available_packages:
                output += f"{pkg}\n"
                output += f"Reverse Depends:\n"
                count = 0
                for other_pkg in self.available_packages:
                    if other_pkg != pkg and random.random() < 0.1 and count < 5:
                        output += f"  {other_pkg}\n"
                        count += 1
            else:
                output += f"N: Unable to locate package {pkg}\n"
        
        return output

    def _stats(self):
        total = len(self.available_packages)
        installed = len(self.installed_packages)
        return f"""Total package names: {total} ({installed} installed)
Total package structures: {total}
  Normal packages: {total}
  Pure virtual packages: 0
  Single virtual packages: 0
  Mixed virtual packages: 0
  Missing: 0
Total distinct versions: {total}
Total distinct descriptions: {total}
Total dependencies: {total * 3}
"""

    def _dpkg_list(self, packages):
        output = "Desired=Unknown/Install/Remove/Purge/Hold\n"
        output += "| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend\n"
        output += "|/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)\n"
        output += "||/ Name                           Version                Architecture Description\n"
        output += "+++-==============================-======================-============-=================================================\n"
        
        pkgs = packages if packages else self.installed_packages.keys()
        
        for pkg in pkgs:
            if pkg.startswith('-'):
                continue
            if pkg in self.installed_packages:
                info = self.installed_packages[pkg]
                output += f"ii  {pkg:<30} {info['version']:<22} amd64        {info['description'][:50]}\n"
        
        return output

    def _dpkg_listfiles(self, packages):
        if not packages:
            return "dpkg: missing package name\n"
        
        output = ""
        for pkg in packages:
            if pkg.startswith('-'):
                continue
            if pkg in self.installed_packages:
                output += f"/usr/bin/{pkg}\n"
                output += f"/usr/share/doc/{pkg}/README\n"
                output += f"/usr/share/doc/{pkg}/copyright\n"
                output += f"/usr/share/man/man1/{pkg}.1.gz\n"
            else:
                output += f"dpkg-query: package '{pkg}' is not installed\n"
        
        return output

    def _dpkg_status(self, packages):
        if not packages:
            return "dpkg: missing package name\n"
        
        output = ""
        for pkg in packages:
            if pkg.startswith('-'):
                continue
            if pkg in self.installed_packages:
                info = self.installed_packages[pkg]
                output += f"Package: {pkg}\n"
                output += f"Status: install ok installed\n"
                output += f"Priority: optional\n"
                output += f"Section: utils\n"
                output += f"Installed-Size: {info['size']}\n"
                output += f"Maintainer: PyLinux Developers <dev@pylinux.org>\n"
                output += f"Architecture: amd64\n"
                output += f"Version: {info['version']}\n"
                output += f"Description: {info['description']}\n"
                output += "\n"
            else:
                output += f"dpkg-query: package '{pkg}' is not installed and no information is available\n"
        
        return output

    def _dpkg_search(self, patterns):
        if not patterns:
            return "dpkg: missing file pattern\n"
        
        output = ""
        pattern = patterns[0]
        
        for pkg in self.installed_packages:
            if pattern in pkg or random.random() < 0.1:
                output += f"{pkg}: /usr/bin/{pattern}\n"
                break
        
        if not output:
            output = f"dpkg-query: no path found matching pattern {pattern}\n"
        
        return output
