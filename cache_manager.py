class Cache:
    def __init__(self, mem_time, cache_time):
        self.cache_counter = -1
        self.set = 2
        self.blocks = 4
        self.words = 4
        self.mem_t = mem_time
        self.cache_t = cache_time
        self.cache = [[]] * self.set
        self.lru = [0] * self.set

    def get_mem_cycles(self, memory, addresses):
        cycles = 0
        for addr in addresses:
            if self.check_addr_in_block(addr):
                self.cache_hit(memory, addr)
                cycles += 1
            else:
                self.cache_miss(memory, addr)
                cycles += 2 * (self.mem_t + self.cache_t)
        
        return cycles

    def cache_hit(self, memory, addr):
        pass

    def check_addr_in_block(self, addr):
        block = int(addr / (self.blocks * self.words))
        bset = block % self.set

        addr_set = self.cache[bset]

        hit = False
        for item in addr_set:
            hit |= addr in item
        return hit

    def cache_miss(self, memory, addr):
        block = int(addr / (self.blocks * self.words))
        bset = block % self.set
        base = block * self.blocks * self.words

        indices = tuple(map(lambda x: base + x, range(0,self.blocks * self.words, self.words)))

        addr_set = self.cache[bset]
        if len(addr_set) < self.set:
            self.cache[bset].append(indices)
        else:
            lru = self.lru[bset]
            self.cache[bset][lru] = indices
            lru = (lru + 1) % self.set
            self.lru[bset] = lru