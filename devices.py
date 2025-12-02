import random


class DeviceManager:
    def __init__(self):
        self.block_devices = {}
        self.char_devices = {}

    def initialize(self):
        self.block_devices = {
            'sda': {'type': 'disk', 'size': 20 * 1024**3},
            'sda1': {'type': 'partition', 'size': 19 * 1024**3, 'fstype': 'ext4'},
            'sda2': {'type': 'partition', 'size': 1024**3, 'fstype': 'swap'},
        }
        self.char_devices = {
            'null': {'major': 1, 'minor': 3},
            'zero': {'major': 1, 'minor': 5},
            'random': {'major': 1, 'minor': 8},
            'urandom': {'major': 1, 'minor': 9},
            'tty': {'major': 5, 'minor': 0},
        }

    def read_device(self, name, size=1):
        if name == 'null':
            return ''
        elif name == 'zero':
            return '\x00' * size
        elif name in ['random', 'urandom']:
            return bytes(random.getrandbits(8) for _ in range(size)).decode('latin-1')
        return None
