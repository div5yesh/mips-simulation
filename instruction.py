from constants import *
import re

class Instruction:
    def __init__(self, instruction):
        self.stage = None
        self.jmp_label = None
        self.accumulator = 0
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
                self.jmp_label = instruction[0]
                (itype, opcode) = (key, instruction[1])
        (self.itype, self.opcode) = (itype, opcode)

    def read_operands(self, instruction):
        dest, src1, src2 = (None, None, None)
        if self.itype != "hlt":
            src1, src2 = instruction[-2], instruction[-1]
            if self.itype != "mainmemory":
                dest = instruction[-3]
        self.dest, self.src1, self.src2 = dest, src1, src2

    def get_src_registers(self):
        srcs = [self.src1, self.src2]
        if self.opcode in ["s.d","s.w","daddi","dsubi","andi","ori"]:
            srcs = [self.src1]
        if self.opcode in ["l.d","l.w"]:
            srcs = []
        return srcs

    def get_dest_register(self):
        dest = self.dest
        if self.opcode in ["l.d","l.w"]:
            dest = self.src1
        if self.opcode in ["s.w","s.d","hlt"]:
            return ""
        return dest

    def __str__(self):
        inst = self.opcode + " " + str(self.dest) + " " + str(self.src1) + " " + str(self.src2) + " " + str(self.itype)
        return inst + ": " + Stage(self.stage.value).name + " - " + str(self.remaning_cycles)

    def check_raw(self, data_dep):
        raw = False
        for src in self.get_src_registers():
            raw |= (src in data_dep and (data_dep[src] != None and data_dep[src] != self) and data_dep[src].stage != Stage.FIN)
        return raw

    def check_waw(self, data_dep):
        pass

    def process_stage(self):
        self.remaning_cycles -= 1
        return self.remaning_cycles <= 0

    def execute(self, registers, data):
        if self.opcode == "daddi":
            self.accumulator = registers[self.src1] + int(self.src2)
        if self.opcode == "dsubi":
            self.accumulator = registers[self.src1] - int(self.src2)
        if self.opcode == "andi":
            self.accumulator = registers[self.src1] & int(self.src2)
        if self.opcode == "or1":
            self.accumulator = registers[self.src1] | int(self.src2)

        if self.opcode == "dadd":
            self.accumulator = registers[self.src1] + registers[self.src2]
        if self.opcode == "dsub":
            self.accumulator = registers[self.src1] - registers[self.src2]
        if self.opcode == "and":
            self.accumulator = registers[self.src1] & registers[self.src2]
        if self.opcode == "or":
            self.accumulator = registers[self.src1] | registers[self.src2]

        if self.opcode in ["l.d","l.w"]:
            arg_info = re.split("[()]", self.src2)
            register = arg_info[1]
            displacement = int(arg_info[0])
            self.accumulator = data[displacement + registers[register]]

    def write_back(self, registers, data):
        registers[self.get_dest_register()] = self.accumulator

    def set_cycles(self, units):
        if self.stage == Stage.EX and self.itype != "ctrl" and self.itype != "hlt":
            self.remaning_cycles = units[self.itype].latency
            if self.opcode in ["dadd","daddi","dsub","dsubi","and","andi","or","ori"]:
                self.remaning_cycles += 1
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