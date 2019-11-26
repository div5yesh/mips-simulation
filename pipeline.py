from constants import *
from functional_unit import FunctionalUnit

class Pipeline:
    instructions = []
    units = dict()
    stages = {
        Stage.IF: AVAILABLE, 
        Stage.ID: AVAILABLE, 
        Stage.EX: AVAILABLE, 
        Stage.WB: AVAILABLE,
        4: 1
    }

    def __init__(self):
        print(self.stages)

    def set_unit_data(self, config):
        for item in config:
            self.units[item[0]] = FunctionalUnit(item)

    def schedule(self, inst):
        self.stages[Stage.IF] = BUSY
        inst.stage = Stage.IF
        inst.remaning_cycles = self.units["i-cache"].latency
        self.instructions += [inst]

    def update(self):
        print("----------------------------")
        for inst in self.instructions:
            if inst.stage < 4:
                print(inst)
                if inst.remaning_cycles > 0:
                    inst.remaning_cycles -= 1
                else:
                    if self.stages[inst.stage + 1]:
                        self.stages[inst.stage] = AVAILABLE
                        inst.stage += 1
                        self.stages[inst.stage] = BUSY
                        inst.remaning_cycles = 3
                        # unit = inst.unit
                        # inst.remaning_cycles = self.units[unit].latency
