class PackageManager:
    def __init__(self, filesystem):
        self.filesystem = filesystem
        self.installed = {'apt': '2.2.4', 'bash': '5.1', 'coreutils': '8.32', 'systemd': '247'}
        self.available = {'nginx': '1.18.0', 'vim': '8.2', 'htop': '3.1', 'git': '2.30', 'python3': '3.9'}
        self.available.update(self.installed)

    def apt(self, args):
        if not args:
            return "Usage: apt [update|upgrade|install|remove|search|list]\n"
        cmd = args[0]
        pkgs = args[1:] if len(args) > 1 else []
        
        if cmd == 'update':
            return "Hit:1 http://deb.pylinux.org stable InRelease\nReading package lists... Done\n"
        elif cmd == 'upgrade':
            return "0 upgraded, 0 newly installed, 0 to remove.\n"
        elif cmd == 'install':
            if not pkgs:
                return "E: No packages specified\n"
            output = "Reading package lists... Done\n"
            for pkg in pkgs:
                if pkg in self.available:
                    self.installed[pkg] = self.available[pkg]
                    output += f"Setting up {pkg} ({self.available[pkg]}) ...\n"
                else:
                    output += f"E: Unable to locate package {pkg}\n"
            return output
        elif cmd == 'remove':
            if not pkgs:
                return "E: No packages specified\n"
            output = ""
            for pkg in pkgs:
                if pkg in self.installed:
                    del self.installed[pkg]
                    output += f"Removing {pkg} ...\n"
                else:
                    output += f"Package '{pkg}' is not installed\n"
            return output
        elif cmd == 'search':
            if not pkgs:
                return ""
            term = pkgs[0].lower()
            output = ""
            for pkg, ver in self.available.items():
                if term in pkg:
                    output += f"{pkg}/{ver}\n"
            return output if output else f"No packages found for '{term}'\n"
        elif cmd == 'list':
            if '--installed' in args:
                return '\n'.join(f"{p}/{v} [installed]" for p, v in self.installed.items()) + '\n'
            return '\n'.join(f"{p}/{v}" for p, v in self.available.items()) + '\n'
        elif cmd == 'show':
            if pkgs and pkgs[0] in self.available:
                return f"Package: {pkgs[0]}\nVersion: {self.available[pkgs[0]]}\nDescription: Package\n"
            return f"N: Unable to locate package {pkgs[0] if pkgs else ''}\n"
        return f"Unknown command: {cmd}\n"

    def dpkg(self, args):
        if not args:
            return "dpkg: missing command\n"
        cmd = args[0]
        if cmd == '-l' or cmd == '--list':
            output = "||/ Name           Version      Description\n"
            output += "+++-==============-============-===========\n"
            for pkg, ver in self.installed.items():
                output += f"ii  {pkg:<14} {ver:<12} Package\n"
            return output
        elif cmd == '-s' or cmd == '--status':
            if len(args) > 1 and args[1] in self.installed:
                return f"Package: {args[1]}\nStatus: install ok installed\nVersion: {self.installed[args[1]]}\n"
            return f"dpkg-query: package '{args[1] if len(args) > 1 else ''}' is not installed\n"
        elif cmd == '-L' or cmd == '--listfiles':
            if len(args) > 1 and args[1] in self.installed:
                return f"/usr/bin/{args[1]}\n/usr/share/doc/{args[1]}/README\n"
            return f"dpkg-query: package '{args[1] if len(args) > 1 else ''}' is not installed\n"
        return f"dpkg: unknown option: {cmd}\n"
