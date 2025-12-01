import time
import random

class MemoryBlock:
    def __init__(self, size, name=''):
        self.size = size
        self.name = name
        self.allocated_at = time.time()

class MemoryManager:
    def __init__(self, total_memory=2048 * 1024 * 1024):
        self.total_memory = total_memory
        self.allocated_blocks = {}
        self.free_memory = total_memory
        self.cached_memory = 0
        self.buffer_memory = 0
        self.swap_total = 1024 * 1024 * 1024
        self.swap_used = 0
        self._initialize_system_memory()

    def _initialize_system_memory(self):
        system_allocations = [
            (50 * 1024 * 1024, 'kernel'),
            (20 * 1024 * 1024, 'filesystem_cache'),
            (10 * 1024 * 1024, 'network_buffers'),
            (30 * 1024 * 1024, 'device_drivers'),
        ]
        
        for size, name in system_allocations:
            self.allocate(size, name)
        
        self.cached_memory = 100 * 1024 * 1024
        self.buffer_memory = 50 * 1024 * 1024

    def allocate(self, size, name=''):
        if size <= self.free_memory:
            block_id = f"{name}_{time.time()}_{random.randint(1000, 9999)}"
            self.allocated_blocks[block_id] = MemoryBlock(size, name)
            self.free_memory -= size
            return block_id
        return None

    def free(self, block_id):
        if block_id in self.allocated_blocks:
            block = self.allocated_blocks[block_id]
            self.free_memory += block.size
            del self.allocated_blocks[block_id]
            return True
        return False

    def get_stats(self):
        total_allocated = sum(block.size for block in self.allocated_blocks.values())
        
        return {
            'total': self.total_memory,
            'used': total_allocated,
            'free': self.free_memory,
            'shared': random.randint(10 * 1024 * 1024, 50 * 1024 * 1024),
            'buffers': self.buffer_memory,
            'cached': self.cached_memory,
            'available': self.free_memory + self.cached_memory,
            'swap_total': self.swap_total,
            'swap_used': self.swap_used,
            'swap_free': self.swap_total - self.swap_used,
        }

    def get_detailed_stats(self):
        stats = self.get_stats()
        stats['blocks'] = [
            {
                'name': block.name,
                'size': block.size,
                'age': time.time() - block.allocated_at
            }
            for block in self.allocated_blocks.values()
        ]
        return stats

    def format_bytes(self, bytes_val):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f}PB"
