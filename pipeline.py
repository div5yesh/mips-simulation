from constants import *
from functional_unit import FunctionalUnit

class Pipeline:
    instructions = []
    completed = []
    units = dict()
    stages = {
        Stage.IF: AVAILABLE, 
        Stage.ID: AVAILABLE, 
        # Stage.EX: AVAILABLE,
        Stage.MEM: AVAILABLE,
        Stage.WB: AVAILABLE,
        Stage.FIN : AVAILABLE
    }

    data_dep = dict()

    icache = [[None] * 4] * 4

    dcache = [[None] * 4] * 4

    def __init__(self):
        pass

    def set_unit_data(self, config):
        for item in config:
            self.units[item[0]] = FunctionalUnit(item)
        self.units["int"] = FunctionalUnit(["int",1,"no"])

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

    def check_next_stage(self, next_stage, inst):
        if next_stage == Stage.EX:
            unit = self.units[inst.itype]
            raw = inst.check_raw(self.data_dep)
            busy = unit.status == BUSY and not unit.pipelined
            if raw:
                return False
            elif not busy:
                return True
        else:
            return self.stages[next_stage]

    def update(self, clock):
        print("----------------------------")
        jump = None
        for inst in self.instructions:
            # print(inst)
            if inst.process_stage():
                next_stage = inst.get_next_stage()
                if self.check_next_stage(next_stage, inst):
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
                    else:
                        if next_stage == Stage.ID:
                            self.data_dep[inst.get_dest_register()] = inst
                        if next_stage == Stage.EX:
                            inst.execute(self.registers, self.memory)
                            self.units[inst.itype].status = BUSY
                        else:
                            self.stages[next_stage] = BUSY
                            if next_stage == Stage.WB:
                                inst.write_back(self.registers, self.memory)
                        inst.set_cycles(self.units, self.dcache, self.memory)
                            
            print(inst.opcode, inst.result)
        self.instructions = [e for e in self.instructions if e not in self.completed]
        return jump