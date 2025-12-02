import socket
import time
import random


class NetworkManager:
    def __init__(self):
        self.interfaces = {}

    def initialize(self):
        self.interfaces = {
            'lo': {'ipv4': '127.0.0.1', 'netmask': '255.0.0.0', 'mac': '00:00:00:00:00:00', 'state': 'UP'},
            'eth0': {'ipv4': '10.0.2.15', 'netmask': '255.255.255.0', 'mac': '08:00:27:8e:8a:a8', 'state': 'UP'}
        }

    def ifconfig(self, args):
        output = []
        for name, iface in self.interfaces.items():
            output.append(f"{name}: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500")
            output.append(f"        inet {iface['ipv4']}  netmask {iface['netmask']}")
            output.append(f"        ether {iface['mac']}")
            output.append("")
        return '\n'.join(output)

    def ip_command(self, args):
        if not args:
            return "Usage: ip [addr|link|route]\n"
        obj = args[0]
        if obj in ['addr', 'a', 'address']:
            return self._ip_addr()
        elif obj in ['link', 'l']:
            return self._ip_link()
        elif obj in ['route', 'r']:
            return self._ip_route()
        return f"ip: unknown object '{obj}'\n"

    def _ip_addr(self):
        output = []
        idx = 1
        for name, iface in self.interfaces.items():
            output.append(f"{idx}: {name}: <UP,LOWER_UP> mtu 1500 state UP")
            output.append(f"    link/ether {iface['mac']} brd ff:ff:ff:ff:ff:ff")
            output.append(f"    inet {iface['ipv4']}/24 scope global {name}")
            idx += 1
        return '\n'.join(output) + '\n'

    def _ip_link(self):
        output = []
        idx = 1
        for name, iface in self.interfaces.items():
            output.append(f"{idx}: {name}: <UP,LOWER_UP> mtu 1500 state UP")
            output.append(f"    link/ether {iface['mac']} brd ff:ff:ff:ff:ff:ff")
            idx += 1
        return '\n'.join(output) + '\n'

    def _ip_route(self):
        return "default via 10.0.2.2 dev eth0\n10.0.2.0/24 dev eth0 proto kernel scope link src 10.0.2.15\n"

    def ping(self, host, count=4):
        try:
            ip = socket.gethostbyname(host)
        except:
            ip = host
        output = f"PING {host} ({ip}) 56(84) bytes of data.\n"
        times = []
        for i in range(count):
            t = random.uniform(0.5, 50.0)
            times.append(t)
            output += f"64 bytes from {ip}: icmp_seq={i+1} ttl=64 time={t:.1f} ms\n"
        avg = sum(times) / len(times)
        output += f"\n--- {host} ping statistics ---\n"
        output += f"{count} packets transmitted, {count} received, 0% packet loss\n"
        output += f"rtt min/avg/max = {min(times):.3f}/{avg:.3f}/{max(times):.3f} ms\n"
        return output

    def netstat(self, args):
        output = "Active Internet connections\n"
        output += "Proto Recv-Q Send-Q Local Address           Foreign Address         State\n"
        output += "tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN\n"
        output += "tcp        0      0 127.0.0.1:25            0.0.0.0:*               LISTEN\n"
        return output

    def nslookup(self, host):
        try:
            ip = socket.gethostbyname(host)
            return f"Server:\t\t8.8.8.8\nAddress:\t8.8.8.8#53\n\nName:\t{host}\nAddress: {ip}\n"
        except:
            return f"** server can't find {host}: NXDOMAIN\n"

    def dig(self, host):
        try:
            ip = socket.gethostbyname(host)
            return f";; ANSWER SECTION:\n{host}.\t\t300\tIN\tA\t{ip}\n"
        except:
            return f";; Got answer: NXDOMAIN\n"

    def curl(self, url):
        try:
            import urllib.request
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.read().decode('utf-8', errors='replace')
        except Exception as e:
            return f"curl: (6) Could not resolve host: {str(e)}\n"

    def wget(self, url):
        try:
            import urllib.request
            output = f"--{time.strftime('%Y-%m-%d %H:%M:%S')}--  {url}\n"
            with urllib.request.urlopen(url, timeout=10) as response:
                content = response.read()
                output += f"Length: {len(content)}\nSaving to: 'index.html'\n\n'index.html' saved [{len(content)}]\n"
            return output
        except Exception as e:
            return f"wget: failed: {str(e)}\n"
