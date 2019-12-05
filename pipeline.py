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

    icache = [[None] * 4] * 4

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
        index = int(pc / 4)
        offset = pc % 4
        if not self.icache[index][offset]:
            inst.remaning_cycles = 6
            self.icache[index] = [1] * 4
        else:
            inst.remaning_cycles = self.units["i-cache"].latency

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
        else:
            if next_stage == Stage.WB:
                if clock>= self.WB_cycle:
                    return True
                elif self.stages[next_stage]: inst.hazards["struct"] = "Y"
            return self.stages[next_stage]

    def update(self, clock):
        print("-" * 30)
        jump = None
        for inst in self.instructions:
            if inst.process_stage():
                next_stage = inst.get_next_stage()
                if self.check_next_stage(next_stage, inst, clock):
                    if inst.stage == Stage.EX:
                        self.units[inst.itype].status = AVAILABLE
                    else:
                        self.stages[inst.stage] = AVAILABLE
                        if inst.stage == Stage.ID and inst.itype == "ctrl":
                            jump = inst.execute_jmp(self.registers)

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
                        if next_stage == Stage.WB:
                            inst.write_back(self.registers, self.memory)
                            self.WB_cycle = clock

                    inst.set_cycles(self.units, self.dcache, self.memory)

            print(inst.opcode, inst.result)
        self.instructions = [e for e in self.instructions if e not in self.completed]
        return jump