import time
import random

class Package:
    def __init__(self, name, version, description, size):
        self.name = name
        self.version = version
        self.description = description
        self.size = size
        self.installed = False
        self.install_date = None
        self.dependencies = []

class PackageManager:
    def __init__(self, filesystem):
        self.filesystem = filesystem
        self.packages = {}
        self.installed_packages = {}
        self._initialize_packages()

    def _initialize_packages(self):
        default_packages = [
            ('coreutils', '8.32', 'GNU core utilities', 6234567),
            ('bash', '5.1.8', 'GNU Bourne Again Shell', 1234567),
            ('vim', '8.2', 'Vi IMproved text editor', 3234567),
            ('nano', '5.8', 'Simple text editor', 523456),
            ('gcc', '11.2.0', 'GNU Compiler Collection', 45234567),
            ('python3', '3.9.7', 'Python programming language', 15234567),
            ('git', '2.33.0', 'Distributed version control system', 8234567),
            ('wget', '1.21.1', 'Network downloader', 1234567),
            ('curl', '7.79.1', 'Transfer data with URLs', 1534567),
            ('htop', '3.1.0', 'Interactive process viewer', 423456),
            ('tmux', '3.2a', 'Terminal multiplexer', 823456),
            ('openssh', '8.7', 'OpenSSH client and server', 2234567),
        ]
        
        for name, version, description, size in default_packages:
            pkg = Package(name, version, description, size)
            self.packages[name] = pkg
            if name in ['coreutils', 'bash']:
                pkg.installed = True
                pkg.install_date = time.time() - random.randint(86400, 864000)
                self.installed_packages[name] = pkg

    def search(self, query):
        results = []
        for name, pkg in self.packages.items():
            if query.lower() in name.lower() or query.lower() in pkg.description.lower():
                results.append(pkg)
        return results

    def install(self, package_name):
        if package_name not in self.packages:
            return False, f"Package '{package_name}' not found"
        
        pkg = self.packages[package_name]
        if pkg.installed:
            return False, f"Package '{package_name}' is already installed"
        
        pkg.installed = True
        pkg.install_date = time.time()
        self.installed_packages[package_name] = pkg
        return True, f"Successfully installed {package_name} {pkg.version}"

    def remove(self, package_name):
        if package_name not in self.installed_packages:
            return False, f"Package '{package_name}' is not installed"
        
        if package_name in ['coreutils', 'bash']:
            return False, f"Cannot remove essential package '{package_name}'"
        
        pkg = self.packages[package_name]
        pkg.installed = False
        pkg.install_date = None
        del self.installed_packages[package_name]
        return True, f"Successfully removed {package_name}"

    def list_installed(self):
        return list(self.installed_packages.values())

    def get_package_info(self, package_name):
        return self.packages.get(package_name)
