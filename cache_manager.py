class Cache:
    def __init__(self):
        self.cache_counter = -1
        self.cache = [[None] * 4] * 4

    def get_mem_cycles(self, memory, addresses):
        cycles = 0
        for addr in addresses:
            if self.check_addr_in_block(addr):
                #cache miss
                self.cache_miss(memory, addr)
                cycles += 6
            else:
                #cache hit
                cycles += 1
        
        return cycles

        # (256, 258), (260, 262), (264, 266), (268, 270)
        # 272, 276, 280, 284

        # if not self.cache[self.cache_counter][offset]:

    def is_block_empty(self):
        pass

    def check_addr_in_block(self, addr):
        flat = [item for subset in self.cache for item in subset]
        return addr not in flat

    def cache_miss(self, memory, addr):
        index = int(addr / 4)
        offset = addr % 4
        idx = list(map(lambda x: x + index * 4, range(0,4)))
        self.cache_counter = (self.cache_counter + 1) % 4
        self.cache[self.cache_counter] = idx #list(map(lambda x: memory[x], idx))