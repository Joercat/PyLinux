import random
import time

class NetworkInterface:
    def __init__(self, name, mac_address, ipv4=None, ipv6=None):
        self.name = name
        self.mac_address = mac_address
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.rx_bytes = 0
        self.tx_bytes = 0
        self.rx_packets = 0
        self.tx_packets = 0
        self.state = 'UP'
        self.mtu = 1500

    def update_stats(self):
        self.rx_bytes += random.randint(100, 10000)
        self.tx_bytes += random.randint(100, 10000)
        self.rx_packets += random.randint(1, 100)
        self.tx_packets += random.randint(1, 100)

class NetworkManager:
    def __init__(self):
        self.interfaces = {}
        self.routes = []
        self.dns_servers = ['8.8.8.8', '8.8.4.4', '1.1.1.1']
        self._initialize_interfaces()

    def _initialize_interfaces(self):
        lo = NetworkInterface('lo', '00:00:00:00:00:00', '127.0.0.1', '::1')
        eth0 = NetworkInterface(
            'eth0',
            self._generate_mac(),
            '192.168.1.100',
            'fe80::1'
        )
        
        self.interfaces['lo'] = lo
        self.interfaces['eth0'] = eth0
        
        self.routes = [
            {'destination': '0.0.0.0', 'gateway': '192.168.1.1', 'netmask': '0.0.0.0', 'interface': 'eth0'},
            {'destination': '192.168.1.0', 'gateway': '0.0.0.0', 'netmask': '255.255.255.0', 'interface': 'eth0'},
        ]

    def _generate_mac(self):
        return ':'.join([f'{random.randint(0, 255):02x}' for _ in range(6)])

    def start(self):
        for interface in self.interfaces.values():
            interface.state = 'UP'

    def stop(self):
        for interface in self.interfaces.values():
            interface.state = 'DOWN'

    def get_interface(self, name):
        return self.interfaces.get(name)

    def list_interfaces(self):
        return list(self.interfaces.keys())

    def get_interface_stats(self, name):
        interface = self.get_interface(name)
        if interface:
            interface.update_stats()
            return {
                'name': interface.name,
                'mac': interface.mac_address,
                'ipv4': interface.ipv4,
                'ipv6': interface.ipv6,
                'rx_bytes': interface.rx_bytes,
                'tx_bytes': interface.tx_bytes,
                'rx_packets': interface.rx_packets,
                'tx_packets': interface.tx_packets,
                'state': interface.state,
                'mtu': interface.mtu
            }
        return None

    def get_routes(self):
        return self.routes

    def ping(self, host, count=4):
        results = []
        for i in range(count):
            latency = random.uniform(10.0, 100.0)
            results.append({
                'seq': i + 1,
                'time': latency,
                'ttl': 64
            })
            time.sleep(0.1)
        return results
