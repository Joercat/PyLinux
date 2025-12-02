import psutil


class MemoryManager:
    def __init__(self):
        self.allocations = {}
        self.page_size = 4096

    def get_stats(self):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'free': mem.free,
            'percent': mem.percent,
            'buffers': getattr(mem, 'buffers', 0),
            'cached': getattr(mem, 'cached', 0),
            'shared': getattr(mem, 'shared', 0),
            'active': getattr(mem, 'active', 0),
            'inactive': getattr(mem, 'inactive', 0),
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_free': swap.free,
            'swap_percent': swap.percent
        }

    def format_free_output(self, human_readable=True):
        stats = self.get_stats()
        
        if human_readable:
            def fmt(n):
                if n >= 1024**3:
                    return f"{n/1024**3:.1f}Gi"
                elif n >= 1024**2:
                    return f"{n/1024**2:.1f}Mi"
                elif n >= 1024:
                    return f"{n/1024:.1f}Ki"
                return f"{n}B"
            
            output = []
            output.append(f"{'':>15} {'total':>10} {'used':>10} {'free':>10} {'shared':>10} {'buff/cache':>12} {'available':>10}")
            output.append(f"{'Mem:':>15} {fmt(stats['total']):>10} {fmt(stats['used']):>10} {fmt(stats['free']):>10} {fmt(stats['shared']):>10} {fmt(stats['buffers'] + stats['cached']):>12} {fmt(stats['available']):>10}")
            output.append(f"{'Swap:':>15} {fmt(stats['swap_total']):>10} {fmt(stats['swap_used']):>10} {fmt(stats['swap_free']):>10}")
            return '\n'.join(output)
        else:
            output = []
            output.append(f"{'':>15} {'total':>15} {'used':>15} {'free':>15}")
            output.append(f"{'Mem:':>15} {stats['total']:>15} {stats['used']:>15} {stats['free']:>15}")
            output.append(f"{'Swap:':>15} {stats['swap_total']:>15} {stats['swap_used']:>15} {stats['swap_free']:>15}")
            return '\n'.join(output)

    def get_meminfo(self):
        stats = self.get_stats()
        output = []
        output.append(f"MemTotal:       {stats['total'] // 1024:>12} kB")
        output.append(f"MemFree:        {stats['free'] // 1024:>12} kB")
        output.append(f"MemAvailable:   {stats['available'] // 1024:>12} kB")
        output.append(f"Buffers:        {stats['buffers'] // 1024:>12} kB")
        output.append(f"Cached:         {stats['cached'] // 1024:>12} kB")
        output.append(f"SwapTotal:      {stats['swap_total'] // 1024:>12} kB")
        output.append(f"SwapFree:       {stats['swap_free'] // 1024:>12} kB")
        return '\n'.join(output)
