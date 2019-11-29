from constants import *

class Instruction:
    def __init__(self, instruction):
        self.stage = None
        self.remaning_cycles = 0
        self.result = dict(zip(["IF","ID","EX","MEM","WB"], ["-"] * 5))
        self.set_props(instruction)
        self.read_operands(instruction)

    def set_props(self, instruction):
        (itype, opcode) = (None, None)
        for (key, value) in InstructionType.items():
            if instruction[0] in value:
                (itype, opcode) = (key, instruction[0])
            elif len(instruction) > 1 and instruction[1] in value:
                (itype, opcode) = (key, instruction[1])
        (self.itype, self.opcode) = (itype, opcode)

    def read_operands(self, instruction):
        dest, src1, src2 = (None, None, None)
        if self.itype != "hlt":
            src1, src2 = instruction[-2], instruction[-1]
            if self.itype != "mainmemory":
                dest = instruction[-3]
        self.dest, self.src1, self.src2 = dest, src1, src2

    def __str__(self):
        inst = self.opcode + " " + str(self.dest) + " " + str(self.src1) + " " + str(self.src2) + " " + str(self.itype)
        return inst + ": " + Stage(self.stage.value).name + " - " + str(self.remaning_cycles)

    def execute_stage(self):
        self.remaning_cycles -= 1
        return self.remaning_cycles <= 0

    def set_cycles(self, units):
        if self.stage == Stage.EX and self.itype != "ctrl" and self.itype != "hlt":
            self.remaning_cycles = units[self.itype].latency
        elif self.stage == Stage.MEM and self.opcode in ["l.d","s.d"]:
            self.remaning_cycles = 2
        else:
            self.remaning_cycles = 1

    def get_next_stage(self):
        if (self.itype == "ctrl" or self.itype == "hlt") and self.stage == Stage.ID:
            return Stage.FIN

        if self.stage == Stage.EX:
            if self.opcode in ["lw","sw","l.d","s.d"]:
                return Stage.MEM
            else:
                return Stage.WB

        return Stage(self.stage.value + 1)