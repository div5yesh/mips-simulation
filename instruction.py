from constants import InstructionType

class Instruction:
    stage = None
    remaning_cycles = 0

    def __init__(self, instruction):
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
        (dest, src1, src2) = (None, None, None)
        if self.itype != "hlt":
            (src1, src2) = (instruction[-2], instruction[-1])
            if self.itype != "data":
                dest = instruction[-3]
        (self.dest, self.src1, self.src2) = (dest, src1, src2)

    def __str__(self):
        inst = self.opcode + " " + str(self.dest) + " " + str(self.src1) + " " + str(self.src2)
        return inst + ": " + str(self.stage) + " - " + str(self.remaning_cycles)

    # def update(self):
    #     print(self)
    #     if self.remaning_cycles > 0:
    #         self.remaning_cycles -= 1
    #         self.stage += 1
