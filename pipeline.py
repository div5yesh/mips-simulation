from constants import *
from functional_unit import FunctionalUnit

class Pipeline:
    instructions = []
    completed = []
    units = dict()
    stages = {
        Stage.IF: AVAILABLE, 
        Stage.ID: AVAILABLE, 
        Stage.EX: AVAILABLE,
        Stage.MEM: AVAILABLE,
        Stage.WB: AVAILABLE,
        Stage.FIN : AVAILABLE
    }

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

    def check_next_stage(self, next_stage, unit):
        # if next_stage == Stage.EX:
            # self.stages[]
        #     return self.units[unit].pipelined

        return self.stages[next_stage]

    def update(self, clock):
        print("----------------------------")
        for inst in self.instructions:
            # print(inst)
            if inst.execute_stage():
                next_stage = inst.get_next_stage()
                unit = inst.itype
                if self.check_next_stage(next_stage, unit):
                    self.stages[inst.stage] = AVAILABLE
                    inst.result[inst.stage.name] = int(clock)
                    inst.stage = next_stage
                    if next_stage == Stage.FIN:
                        self.completed += [inst]
                    else:
                        self.stages[next_stage] = BUSY
                        inst.set_cycles(self.units)

            print(inst.opcode, inst.result)
        self.instructions = [e for e in self.instructions if e not in self.completed]