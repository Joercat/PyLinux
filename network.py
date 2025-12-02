import socket
import time
import random
import psutil

class NetworkManager:
    def __init__(self):
        self.interfaces = {}
        self.routing_table = []
        self.arp_cache = {}
        self.dns_servers = ['8.8.8.8', '8.8.4.4', '1.1.1.1']

    def initialize(self):
        self.interfaces = {
            'lo': {
                'ipv4': '127.0.0.1',
                'netmask': '255.0.0.0',
                'ipv6': '::1',
                'mac': '00:00:00:00:00:00',
                'mtu': 65536,
                'state': 'UP',
                'rx_bytes': 0,
                'tx_bytes': 0,
                'rx_packets': 0,
                'tx_packets': 0
            },
            'eth0': {
                'ipv4': '10.0.2.15',
                'netmask': '255.255.255.0',
                'broadcast': '10.0.2.255',
                'ipv6': 'fe80::a00:27ff:fe8e:8aa8',
                'mac': '08:00:27:8e:8a:a8',
                'mtu': 1500,
                'state': 'UP',
                'rx_bytes': random.randint(1000000, 10000000),
                'tx_bytes': random.randint(500000, 5000000),
                'rx_packets': random.randint(1000, 10000),
                'tx_packets': random.randint(500, 5000)
            }
        }
        
        try:
            for iface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        if iface not in self.interfaces:
                            self.interfaces[iface] = {
                                'ipv4': addr.address,
                                'netmask': addr.netmask or '255.255.255.0',
                                'broadcast': addr.broadcast or '',
                                'mac': '00:00:00:00:00:00',
                                'mtu': 1500,
                                'state': 'UP',
                                'rx_bytes': 0,
                                'tx_bytes': 0,
                                'rx_packets': 0,
                                'tx_packets': 0
                            }
                        else:
                            self.interfaces[iface]['ipv4'] = addr.address
                            self.interfaces[iface]['netmask'] = addr.netmask or '255.255.255.0'
        except:
            pass
        
        self.routing_table = [
            {'destination': '0.0.0.0', 'gateway': '10.0.2.2', 'genmask': '0.0.0.0', 'flags': 'UG', 'metric': 100, 'iface': 'eth0'},
            {'destination': '10.0.2.0', 'gateway': '0.0.0.0', 'genmask': '255.255.255.0', 'flags': 'U', 'metric': 100, 'iface': 'eth0'},
            {'destination': '127.0.0.0', 'gateway': '0.0.0.0', 'genmask': '255.0.0.0', 'flags': 'U', 'metric': 0, 'iface': 'lo'}
        ]
        
        self.arp_cache = {
            '10.0.2.2': '52:54:00:12:35:02',
            '10.0.2.3': '52:54:00:12:35:03'
        }

    def ifconfig(self, args):
        if not args:
            output = []
            for name, iface in self.interfaces.items():
                output.append(self._format_interface(name, iface))
            return '\n'.join(output) + '\n'
        
        iface_name = args[0]
        if iface_name in self.interfaces:
            return self._format_interface(iface_name, self.interfaces[iface_name]) + '\n'
        
        return f"ifconfig: interface {iface_name} does not exist\n"

    def _format_interface(self, name, iface):
        flags = f"<{'UP,' if iface['state'] == 'UP' else ''}BROADCAST,RUNNING,MULTICAST>" if name != 'lo' else "<LOOPBACK,UP,RUNNING>"
        
        output = f"{name}: flags=4163{flags}  mtu {iface['mtu']}\n"
        output += f"        inet {iface['ipv4']}  netmask {iface['netmask']}"
        if 'broadcast' in iface and iface['broadcast']:
            output += f"  broadcast {iface['broadcast']}"
        output += "\n"
        if 'ipv6' in iface:
            output += f"        inet6 {iface['ipv6']}  prefixlen 64  scopeid 0x20<link>\n"
        if name != 'lo':
            output += f"        ether {iface['mac']}  txqueuelen 1000  (Ethernet)\n"
        else:
            output += "        loop  txqueuelen 1000  (Local Loopback)\n"
        output += f"        RX packets {iface['rx_packets']}  bytes {iface['rx_bytes']} ({iface['rx_bytes'] / 1024 / 1024:.1f} MiB)\n"
        output += f"        RX errors 0  dropped 0  overruns 0  frame 0\n"
        output += f"        TX packets {iface['tx_packets']}  bytes {iface['tx_bytes']} ({iface['tx_bytes'] / 1024 / 1024:.1f} MiB)\n"
        output += f"        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0\n"
        
        return output

    def ip_command(self, args):
        if not args:
            return "Usage: ip [ OPTIONS ] OBJECT { COMMAND | help }\n"
        
        obj = args[0]
        
        if obj == 'addr' or obj == 'a' or obj == 'address':
            return self._ip_addr(args[1:])
        elif obj == 'link' or obj == 'l':
            return self._ip_link(args[1:])
        elif obj == 'route' or obj == 'r':
            return self._ip_route(args[1:])
        elif obj == 'neigh' or obj == 'n' or obj == 'neighbor':
            return self._ip_neigh(args[1:])
        
        return f"ip: unknown object '{obj}'\n"

    def _ip_addr(self, args):
        output = []
        idx = 1
        for name, iface in self.interfaces.items():
            state = "UP" if iface['state'] == 'UP' else "DOWN"
            flags = f"<{'LOOPBACK,' if name == 'lo' else ''}{'UP,' if state == 'UP' else ''}LOWER_UP>"
            
            output.append(f"{idx}: {name}: {flags} mtu {iface['mtu']} qdisc noqueue state {state} group default qlen 1000")
            if name != 'lo':
                output.append(f"    link/ether {iface['mac']} brd ff:ff:ff:ff:ff:ff")
            else:
                output.append(f"    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00")
            output.append(f"    inet {iface['ipv4']}/{'8' if name == 'lo' else '24'} {'brd ' + iface.get('broadcast', '') if name != 'lo' else ''} scope {'host' if name == 'lo' else 'global'} {name}")
            output.append(f"       valid_lft forever preferred_lft forever")
            if 'ipv6' in iface:
                output.append(f"    inet6 {iface['ipv6']}/64 scope link")
                output.append(f"       valid_lft forever preferred_lft forever")
            idx += 1
        
        return '\n'.join(output) + '\n'

    def _ip_link(self, args):
        output = []
        idx = 1
        for name, iface in self.interfaces.items():
            state = "UP" if iface['state'] == 'UP' else "DOWN"
            flags = f"<{'LOOPBACK,' if name == 'lo' else ''}{'UP,' if state == 'UP' else ''}LOWER_UP>"
            
            output.append(f"{idx}: {name}: {flags} mtu {iface['mtu']} qdisc noqueue state {state} mode DEFAULT group default qlen 1000")
            if name != 'lo':
                output.append(f"    link/ether {iface['mac']} brd ff:ff:ff:ff:ff:ff")
            else:
                output.append(f"    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00")
            idx += 1
        
        return '\n'.join(output) + '\n'

    def _ip_route(self, args):
        output = []
        output.append("default via 10.0.2.2 dev eth0 proto dhcp metric 100")
        output.append("10.0.2.0/24 dev eth0 proto kernel scope link src 10.0.2.15 metric 100")
        output.append("127.0.0.0/8 dev lo proto kernel scope link src 127.0.0.1")
        return '\n'.join(output) + '\n'

    def _ip_neigh(self, args):
        output = []
        for ip, mac in self.arp_cache.items():
            output.append(f"{ip} dev eth0 lladdr {mac} REACHABLE")
        return '\n'.join(output) + '\n' if output else ''

    def ping(self, host, count=4):
        try:
            ip = socket.gethostbyname(host)
        except:
            ip = host if host.replace('.', '').isdigit() else '0.0.0.0'
        
        output = f"PING {host} ({ip}) 56(84) bytes of data.\n"
        
        times = []
        for i in range(count):
            t = random.uniform(0.5, 50.0)
            times.append(t)
            ttl = random.randint(48, 64)
            output += f"64 bytes from {ip}: icmp_seq={i+1} ttl={ttl} time={t:.1f} ms\n"
        
        output += f"\n--- {host} ping statistics ---\n"
        output += f"{count} packets transmitted, {count} received, 0% packet loss, time {int(sum(times))}ms\n"
        
        avg = sum(times) / len(times)
        mdev = (sum((t - avg) ** 2 for t in times) / len(times)) ** 0.5
        output += f"rtt min/avg/max/mdev = {min(times):.3f}/{avg:.3f}/{max(times):.3f}/{mdev:.3f} ms\n"
        
        return output

    def traceroute(self, host):
        try:
            ip = socket.gethostbyname(host)
        except:
            ip = host
        
        output = f"traceroute to {host} ({ip}), 30 hops max, 60 byte packets\n"
        
        hops = random.randint(8, 15)
        for i in range(1, hops + 1):
            if i == hops:
                hop_ip = ip
            else:
                hop_ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            
            t1 = random.uniform(1, 100)
            t2 = random.uniform(1, 100)
            t3 = random.uniform(1, 100)
            
            output += f" {i:2}  {hop_ip}  {t1:.3f} ms  {t2:.3f} ms  {t3:.3f} ms\n"
        
        return output

    def netstat(self, args):
        listen = '-l' in args
        tcp = '-t' in args
        udp = '-u' in args
        numeric = '-n' in args
        all_sockets = '-a' in args
        programs = '-p' in args
        
        if not tcp and not udp:
            tcp = udp = True
        
        output = "Active Internet connections"
        if listen:
            output += " (only servers)"
        elif all_sockets:
            output += " (servers and established)"
        else:
            output += " (w/o servers)"
        output += "\n"
        
        output += "Proto Recv-Q Send-Q Local Address           Foreign Address         State"
        if programs:
            output += "       PID/Program name"
        output += "\n"
        
        if tcp:
            if listen or all_sockets:
                output += "tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN"
                if programs:
                    output += "      106/sshd"
                output += "\n"
                output += "tcp        0      0 127.0.0.1:25            0.0.0.0:*               LISTEN"
                if programs:
                    output += "      -"
                output += "\n"
            
            if not listen or all_sockets:
                output += "tcp        0      0 10.0.2.15:22            10.0.2.2:54321          ESTABLISHED"
                if programs:
                    output += " 109/sshd"
                output += "\n"
        
        if udp:
            if listen or all_sockets:
                output += "udp        0      0 0.0.0.0:68              0.0.0.0:*"
                if programs:
                    output += "                           -"
                output += "\n"
        
        return output

    def ss(self, args):
        return self.netstat(args)

    def route(self, args):
        if '-n' in args or not args:
            output = "Kernel IP routing table\n"
            output += "Destination     Gateway         Genmask         Flags Metric Ref    Use Iface\n"
            
            for r in self.routing_table:
                output += f"{r['destination']:<16}{r['gateway']:<16}{r['genmask']:<16}{r['flags']:<6}{r['metric']:<7}0        0 {r['iface']}\n"
            
            return output
        
        return "route: command not supported\n"

    def arp(self, args):
        if '-n' in args or '-a' in args or not args:
            output = ""
            for ip, mac in self.arp_cache.items():
                output += f"? ({ip}) at {mac} [ether] on eth0\n"
            return output
        
        return "arp: command not supported\n"

    def nslookup(self, host):
        try:
            ip = socket.gethostbyname(host)
            return f"""Server:\t\t8.8.8.8
Address:\t8.8.8.8#53

Non-authoritative answer:
Name:\t{host}
Address: {ip}
"""
        except:
            return f"""Server:\t\t8.8.8.8
Address:\t8.8.8.8#53

** server can't find {host}: NXDOMAIN
"""

    def dig(self, host):
        try:
            ip = socket.gethostbyname(host)
            return f"""; <<>> DiG 9.16.1-Ubuntu <<>> {host}
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: {random.randint(10000, 65535)}
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 65494
;; QUESTION SECTION:
;{host}.\t\t\tIN\tA

;; ANSWER SECTION:
{host}.\t\t{random.randint(100, 3600)}\tIN\tA\t{ip}

;; Query time: {random.randint(1, 100)} msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: {time.strftime('%a %b %d %H:%M:%S %Z %Y')}
;; MSG SIZE  rcvd: {random.randint(50, 100)}
"""
        except:
            return f"""; <<>> DiG 9.16.1-Ubuntu <<>> {host}
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: {random.randint(10000, 65535)}
"""

    def host(self, hostname):
        try:
            ip = socket.gethostbyname(hostname)
            return f"{hostname} has address {ip}\n"
        except:
            return f"Host {hostname} not found: 3(NXDOMAIN)\n"

    def curl(self, url, method='GET', data=None, headers=None, include_headers=False, headers_only=False):
        try:
            import urllib.request
            import urllib.error
            
            req = urllib.request.Request(url, method=method)
            req.add_header('User-Agent', 'curl/7.68.0')
            
            if headers:
                for h in headers:
                    if ':' in h:
                        key, value = h.split(':', 1)
                        req.add_header(key.strip(), value.strip())
            
            if data:
                req.data = data.encode()
            
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    output = ''
                    
                    if include_headers or headers_only:
                        output += f"HTTP/1.1 {response.status} {response.reason}\n"
                        for key, value in response.headers.items():
                            output += f"{key}: {value}\n"
                        output += "\n"
                    
                    if not headers_only:
                        output += response.read().decode('utf-8', errors='replace')
                    
                    return output
            except urllib.error.HTTPError as e:
                output = f"HTTP/1.1 {e.code} {e.reason}\n"
                if include_headers:
                    for key, value in e.headers.items():
                        output += f"{key}: {value}\n"
                return output
            except urllib.error.URLError as e:
                return f"curl: (6) Could not resolve host: {e.reason}\n"
        except Exception as e:
            return f"curl: error: {str(e)}\n"

    def wget(self, url, output_file=None, quiet=False):
        try:
            import urllib.request
            
            if not quiet:
                output = f"--{time.strftime('%Y-%m-%d %H:%M:%S')}--  {url}\n"
                output += f"Resolving {url.split('/')[2]}... "
            else:
                output = ""
            
            try:
                with urllib.request.urlopen(url, timeout=10) as response:
                    content = response.read().decode('utf-8', errors='replace')
                    
                    if not quiet:
                        output += f"connected.\n"
                        output += f"HTTP request sent, awaiting response... {response.status} {response.reason}\n"
                        output += f"Length: {len(content)} ({len(content) / 1024:.1f}K)\n"
                        
                        if output_file:
                            output += f"Saving to: '{output_file}'\n\n"
                            output += f"'{output_file}' saved [{len(content)}/{len(content)}]\n"
                        else:
                            output += content
                    
                    return output
            except Exception as e:
                return f"wget: failed: {str(e)}\n"
        except Exception as e:
            return f"wget: error: {str(e)}\n"
