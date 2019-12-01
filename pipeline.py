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

    registers = dict()

    def __init__(self):
        print(self.stages)

    def set_unit_data(self, config):
        for item in config:
            self.units[item[0]] = FunctionalUnit(item)
        self.units["int"] = FunctionalUnit(["int",1,"no"])
        
    def schedule(self, inst):
        self.stages[Stage.IF] = BUSY
        inst.stage = Stage.IF
        inst.remaning_cycles = self.units["i-cache"].latency
        self.instructions += [inst]

    def check_next_stage(self, next_stage, inst):
        if next_stage == Stage.EX:
            unit = self.units[inst.itype]
            raw = inst.check_raw(self.registers)
            busy = unit.status == BUSY and not unit.pipelined
            if raw:
                return False
            elif not busy:
                return True
        else:
            return self.stages[next_stage]

    def update(self, clock):
        print("----------------------------")
        for inst in self.instructions:
            # print(inst)
            if inst.execute_stage():
                next_stage = inst.get_next_stage()
                if self.check_next_stage(next_stage, inst):
                    if inst.stage == Stage.EX:
                        self.units[inst.itype].status = AVAILABLE
                    else:
                        self.stages[inst.stage] = AVAILABLE

                    inst.result[inst.stage.name] = int(clock)
                    inst.stage = next_stage
                    if next_stage == Stage.FIN:
                        self.completed += [inst]
                        self.registers[inst.get_dest_register()] = None
                    else:
                        if next_stage == Stage.ID:
                            self.registers[inst.get_dest_register()] = inst
                        if next_stage == Stage.EX:
                            self.units[inst.itype].status = BUSY
                        else:
                            self.stages[next_stage] = BUSY
                        inst.set_cycles(self.units)
                            
            print(inst.opcode, inst.result)
        self.instructions = [e for e in self.instructions if e not in self.completed]