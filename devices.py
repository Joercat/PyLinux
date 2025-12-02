import random
import time

class DeviceManager:
    def __init__(self):
        self.devices = {}
        self.block_devices = {}
        self.char_devices = {}

    def initialize(self):
        self.block_devices = {
            'sda': {
                'type': 'disk',
                'size': 20 * 1024 * 1024 * 1024,
                'model': 'Virtual Disk',
                'vendor': 'QEMU',
                'partitions': ['sda1', 'sda2']
            },
            'sda1': {
                'type': 'partition',
                'size': 19 * 1024 * 1024 * 1024,
                'fstype': 'ext4',
                'mountpoint': '/'
            },
            'sda2': {
                'type': 'partition',
                'size': 1024 * 1024 * 1024,
                'fstype': 'swap',
                'mountpoint': '[SWAP]'
            },
            'sr0': {
                'type': 'cdrom',
                'size': 1024 * 1024 * 1024,
                'model': 'Virtual CDROM',
                'vendor': 'QEMU'
            }
        }
        
        self.char_devices = {
            'null': {'major': 1, 'minor': 3, 'type': 'null'},
            'zero': {'major': 1, 'minor': 5, 'type': 'zero'},
            'full': {'major': 1, 'minor': 7, 'type': 'full'},
            'random': {'major': 1, 'minor': 8, 'type': 'random'},
            'urandom': {'major': 1, 'minor': 9, 'type': 'urandom'},
            'tty': {'major': 5, 'minor': 0, 'type': 'tty'},
            'console': {'major': 5, 'minor': 1, 'type': 'console'},
            'ptmx': {'major': 5, 'minor': 2, 'type': 'ptmx'}
        }
        
        for i in range(8):
            self.char_devices[f'tty{i}'] = {'major': 4, 'minor': i, 'type': 'tty'}
        
        self.devices = {
            'cpu': {
                'vendor': 'GenuineIntel',
                'model': 'Intel(R) Core(TM) Processor',
                'cores': 4,
                'threads': 8,
                'frequency': 2400.0
            },
            'memory': {
                'total': 8 * 1024 * 1024 * 1024,
                'type': 'DDR4',
                'speed': 2666
            },
            'pci': [
                {'id': '00:00.0', 'type': 'Host bridge', 'vendor': 'Intel Corporation'},
                {'id': '00:01.0', 'type': 'PCI bridge', 'vendor': 'Intel Corporation'},
                {'id': '00:02.0', 'type': 'VGA controller', 'vendor': 'Intel Corporation'},
                {'id': '00:14.0', 'type': 'USB controller', 'vendor': 'Intel Corporation'},
                {'id': '00:17.0', 'type': 'SATA controller', 'vendor': 'Intel Corporation'},
                {'id': '00:1f.0', 'type': 'ISA bridge', 'vendor': 'Intel Corporation'},
                {'id': '00:1f.3', 'type': 'Audio device', 'vendor': 'Intel Corporation'}
            ],
            'usb': [
                {'bus': 1, 'device': 1, 'id': '1d6b:0002', 'name': 'Linux Foundation 2.0 root hub'},
                {'bus': 2, 'device': 1, 'id': '1d6b:0003', 'name': 'Linux Foundation 3.0 root hub'},
                {'bus': 1, 'device': 2, 'id': '0627:0001', 'name': 'QEMU USB Keyboard'},
                {'bus': 1, 'device': 3, 'id': '0627:0001', 'name': 'QEMU USB Mouse'}
            ]
        }

    def read_device(self, device_name, size=1):
        if device_name == 'null':
            return ''
        elif device_name == 'zero':
            return '\x00' * size
        elif device_name == 'full':
            return '\x00' * size
        elif device_name == 'random' or device_name == 'urandom':
            return bytes(random.getrandbits(8) for _ in range(size)).decode('latin-1')
        return None

    def write_device(self, device_name, data):
        if device_name == 'null':
            return len(data)
        elif device_name == 'zero':
            return 0
        elif device_name == 'full':
            return -1
        return None

    def get_block_device_info(self, device_name):
        return self.block_devices.get(device_name)

    def get_char_device_info(self, device_name):
        return self.char_devices.get(device_name)
