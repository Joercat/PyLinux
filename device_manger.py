import random

class Device:
    def __init__(self, name, device_type, major, minor):
        self.name = name
        self.device_type = device_type
        self.major = major
        self.minor = minor
        self.permissions = '660'
        self.owner = 'root'
        self.group = 'root'

class DeviceManager:
    def __init__(self):
        self.devices = {}
        self.block_devices = {}

    def initialize_devices(self):
        devices = [
            ('null', 'c', 1, 3),
            ('zero', 'c', 1, 5),
            ('random', 'c', 1, 8),
            ('urandom', 'c', 1, 9),
            ('tty', 'c', 5, 0),
            ('console', 'c', 5, 1),
            ('ptmx', 'c', 5, 2),
            ('sda', 'b', 8, 0),
            ('sda1', 'b', 8, 1),
            ('sda2', 'b', 8, 2),
        ]
        
        for name, dtype, major, minor in devices:
            self.devices[name] = Device(name, dtype, major, minor)
        
        self.block_devices['sda'] = {
            'size': 21474836480,
            'model': 'Virtual Disk',
            'partitions': {
                'sda1': {'size': 20474836480, 'filesystem': 'ext4', 'mountpoint': '/'},
                'sda2': {'size': 1000000000, 'filesystem': 'swap', 'mountpoint': '[SWAP]'}
            }
        }

    def list_devices(self):
        return list(self.devices.keys())

    def get_device(self, name):
        return self.devices.get(name)

    def list_block_devices(self):
        return self.block_devices

    def read_random(self, size):
        return bytes([random.randint(0, 255) for _ in range(size)])
