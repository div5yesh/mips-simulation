from constants import *
from functional_unit import FunctionalUnit
from cache_manager import Cache

class Pipeline:
    instructions = []
    completed = []
    units = dict()
    stages = {
        Stage.IF: AVAILABLE, 
        Stage.ID: AVAILABLE, 
        Stage.MEM: AVAILABLE,
        Stage.WB: AVAILABLE,
        Stage.FIN : AVAILABLE
    }

    WB_cycle = 0

    data_dep = dict()

    bus = AVAILABLE
    icache = [[],[],[],[]]
    access_count = 0
    hit_count = 0

    dcache = None

    def __init__(self):
        pass

    def set_unit_data(self, config):
        for item in config:
            self.units[item[0]] = FunctionalUnit(item)
        self.units["int"] = FunctionalUnit(["int",1,"yes"])
        mem = self.units["mainmemory"].latency
        cache = self.units["d-cache"].latency
        self.dcache = Cache(mem,cache)

    def set_data(self, registers, memory):
        self.registers = registers
        self.memory = memory
        
    def schedule(self, inst, pc):
        self.stages[Stage.IF] = BUSY
        inst.stage = Stage.IF

        block = (int(pc / 4) % 4)
        base = block * 4

        self.access_count += 1
        if pc not in self.icache[block]:
            self.bus = BUSY
            inst.remaning_cycles = 2 * (self.units["mainmemory"].latency + self.units["i-cache"].latency)
            self.icache[block] = tuple(map(lambda x: x + base, range(0,4)))
        else:
            inst.remaning_cycles = self.units["i-cache"].latency
            self.hit_count += 1

        self.instructions += [inst]

    def check_next_stage(self, next_stage, inst, clock):

        waw = inst.check_waw(self.data_dep)
        if inst.stage == Stage.ID and waw:
            inst.hazards["waw"] = "Y"
            return False

        raw = inst.check_raw(self.data_dep)
        if inst.stage == Stage.ID and raw:
            inst.hazards["raw"] = "Y"
            return False

        if next_stage == Stage.EX:
            unit = self.units[inst.itype]
            busy = unit.status == BUSY and not unit.pipelined
            return not busy

        elif next_stage == Stage.WB:
            if clock > self.WB_cycle: #?? 83,84
                return True
            else:
                return self.stages[next_stage]

        elif next_stage == Stage.MEM:
            if inst.opcode in ["l.d","lw"]:
                if (self.bus == BUSY and not self.dcache.check_addr_in_block(inst.addr)) or self.stages[next_stage] == BUSY: #?? 15,16
                    inst.hazards["struct"] = "Y"
                    return False
            return self.stages[next_stage]
            
        else:
            return self.stages[next_stage]

    def update(self, clock):
        print("\n","-" * 15, "CLOCK:", clock, "-" * 15)
        jump = None
        hlt = False
        for inst in self.instructions:
            if inst.process_stage():
                next_stage = inst.get_next_stage()
                if self.check_next_stage(next_stage, inst, clock):
                    if inst.stage == Stage.EX:
                        self.units[inst.itype].status = AVAILABLE
                    else:
                        self.stages[inst.stage] = AVAILABLE
                        if inst.stage == Stage.ID:
                            if inst.itype == "ctrl":
                                jump = inst.execute_jmp(self.registers)
                            # if inst.itype == "hlt": hlt = True

                    inst.result[inst.stage.name] = int(clock)
                    inst.stage = next_stage

                    if next_stage == Stage.FIN:
                        self.completed += [inst]
                        self.data_dep[inst.get_dest_register()] = None
                    elif next_stage == Stage.EX:
                        self.data_dep[inst.get_dest_register()] = inst
                        inst.execute(self.registers, self.memory)
                        self.units[inst.itype].status = BUSY
                    else:
                        self.stages[next_stage] = BUSY
                        if next_stage == Stage.ID and self.bus == BUSY:
                            self.bus = AVAILABLE
                        elif next_stage == Stage.WB:
                            inst.write_back(self.registers, self.memory)
                            self.WB_cycle = clock

                    inst.set_cycles(self.units, self.dcache, self.memory)

            print(inst.opcode, inst.result)

        if jump or hlt:
            instruction = self.instructions[-1]
            self.completed += [instruction]
            self.stages[instruction.stage] = AVAILABLE

        self.instructions = [e for e in self.instructions if e not in self.completed]
        return jump