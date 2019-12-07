from constants import *
import re

class Instruction:

    def __init__(self, instruction):
        self.stage = None
        self.jmp_label = None
        self.addr = 0
        self.accumulator = 0
        self.remaining_cycles = 0
        self.result = dict(zip(["IF","ID","EX","MEM","WB"], ["-"] * 5))
        self.set_props(instruction)
        self.read_operands(instruction)
        self.hazards = dict(zip(["raw","war","waw","struct"], ["N"] * 4))

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
        if self.opcode in ["s.d","sw","daddi","dsubi","andi","ori"]:
            srcs = [self.src1]
        if self.opcode in ["bne","beq"]:
            srcs = [self.dest, self.src1]
        if self.opcode in ["l.d","lw"]:
            srcs = []
        return srcs

    def get_dest_register(self):
        dest = self.dest
        if self.opcode in ["l.d","lw"]:
            dest = self.src1
        if self.opcode in ["sw","s.d","hlt"] or self.itype == "ctrl":
            return ""
        return dest

    def print(self):
        dest = str(self.dest if self.dest else "")
        if self.opcode in ["l.d","s.d","lw","sw"]: dest = ""
        inst = str(self.jmp_label + ": " if self.jmp_label else "").ljust(4) + self.opcode + " " + dest + " " + str(self.src1 if self.src1 else "") + " " + str(self.src2 if self.src2 else "")
        return inst

    def __str__(self):
        inst = self.opcode + " " + str(self.dest) + " " + str(self.src1) + " " + str(self.src2) + " " + str(self.itype)
        return inst + ": " + Stage(self.stage.value).name + " - " + str(self.remaining_cycles)

    def check_raw(self, data_dep):
        raw = False
        for src in self.get_src_registers():
            raw |= (src in data_dep and data_dep[src] != None and data_dep[src] != self and data_dep[src].stage != Stage.FIN)
        return raw

    def check_waw(self, data_dep):
        dest = self.get_dest_register()
        return dest in data_dep and data_dep[dest] != None and data_dep[dest] != self and data_dep[dest].stage != Stage.FIN

    def check_war(self, data_dep):
        arg_info = re.split("[()]", self.src2)
        st_src = arg_info[1]
        return st_src in data_dep and data_dep[st_src] != None and data_dep[st_src] != self and data_dep[st_src].stage != Stage.FIN

    def process_stage(self):
        self.remaining_cycles -= 1
        return self.remaining_cycles <= 0

    def execute_mem(self, registers, data):
        data[self.addr] = registers[self.src1]

    def execute_jmp(self, registers):
        label = None
        if self.opcode == "bne" and registers[self.dest] != registers[self.src1]:
            label = self.src2
        if self.opcode == "beq" and registers[self.dest] == registers[self.src1]:
            label = self.src2
        if self.opcode == "j":
            label = self.src2
        return label

    def execute(self, registers, data):
        if self.opcode == "daddi":
            self.accumulator = registers[self.src1] + int(self.src2)
        if self.opcode == "dsubi":
            self.accumulator = registers[self.src1] - int(self.src2)
        if self.opcode == "andi":
            self.accumulator = registers[self.src1] & int(self.src2)
        if self.opcode == "ori":
            self.accumulator = registers[self.src1] | int(self.src2)

        if self.opcode == "dadd":
            self.accumulator = registers[self.src1] + registers[self.src2]
        if self.opcode == "dsub":
            self.accumulator = registers[self.src1] - registers[self.src2]
        if self.opcode == "and":
            self.accumulator = registers[self.src1] & registers[self.src2]
        if self.opcode == "or":
            self.accumulator = registers[self.src1] | registers[self.src2]

        if self.opcode in ["lw","l.d","sw","s.d"]:
            arg_info = re.split("[()]", self.src2)
            register = arg_info[1]
            displacement = int(arg_info[0])
            self.addr = displacement + registers[register]
            if self.opcode in ["lw","l.d"]:
                self.accumulator = data[self.addr]
            if self.opcode == "sw":
                self.execute_mem(registers, data)

    def write_back(self, registers, data):
        if self.opcode not in ["s.d","sw"]:
            registers[self.get_dest_register()] = self.accumulator

    def set_cycles(self, units, cache, memory):
        if self.stage == Stage.EX and self.itype != "ctrl" and self.itype != "hlt":
            self.remaining_cycles = units[self.itype].latency
        elif self.stage == Stage.MEM:
            if self.opcode in ["lw","l.d"]:
                addresses = [self.addr]
                if self.opcode in ["l.d"]:
                    addresses += [self.addr + 4]

                self.remaining_cycles, _ = cache.get_mem_cycles(memory, addresses)

            elif self.opcode in ["sw","s.d"]:
                addresses = [self.addr]
                if self.opcode in ["s.d"]:
                    addresses += [self.addr + 4]

                _, hit = cache.get_mem_cycles(memory, addresses)

                if hit:
                    if self.opcode == "sw": self.remaining_cycles = cache.cache_t
                    if self.opcode == "s.d": self.remaining_cycles = 2 * cache.cache_t
                else:
                    if self.opcode == "sw": self.remaining_cycles = 2 * (cache.cache_t + cache.mem_t) + cache.cache_t
                    if self.opcode == "s.d": self.remaining_cycles = 2 * (cache.cache_t + cache.mem_t) + 2 * cache.cache_t
            else:
                self.remaining_cycles = 1
        else:
            self.remaining_cycles = 1

    def get_data_for_cache(self):
        pass

    def get_next_stage(self):
        if (self.itype == "ctrl" or self.itype == "hlt") and self.stage == Stage.ID:
            return Stage.FIN

        if self.stage == Stage.EX:
            if self.itype == "int":
                return Stage.MEM
            else:
                return Stage.WB
        return Stage(self.stage.value + 1)