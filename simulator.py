import sys
from constants import *
from data_parser import Parser
from pipeline import Pipeline
from instruction import Instruction

class Simulation:
    clock = 0
    program_counter = 0

    def __init__(self, output_file):
        # self.output = []
        self.jump_labels = dict()
        self.pipeline = Pipeline()

    def set_parser_data(self, parser_data):
        self.data = parser_data
        self.pipeline.set_unit_data(parser.config)
        self.pipeline.set_data(parser.registers, parser.memory)

    def next_tick(self):
        self.clock += 1
        instruction = None
        if self.program_counter < len(self.data.program):
            curr_inst = self.data.program[self.program_counter]
            instruction = Instruction(curr_inst)

            if instruction.jmp_label:
                self.jump_labels[instruction.jmp_label] = self.program_counter

            if self.pipeline.stages[Stage.IF]:
                self.pipeline.schedule(instruction, self.program_counter)
                self.program_counter += 1

        label = self.pipeline.update(self.clock)
        if label in self.jump_labels:
            self.program_counter = self.jump_labels[label]
            
        return instruction

    def run(self, cycles):
        inst = Instruction(["","",""])
        while self.clock < cycles:
        # while not (inst.opcode == "hlt" and inst.stage == Stage.ID): 
            # cmd = input()
            inst = self.next_tick()

        self.print_result()
        # self.print_final_result()

    def print_final_result(self):
        header = "instruction".ljust(20," ") + \
            "FT".ljust(10," ") + \
            "ID".ljust(10," ") + \
            "EX".ljust(10," ") + \
            "WB".ljust(10," ") + \
            "RAW".ljust(10," ") + \
            "WAR".ljust(10," ") + \
            "WAW".ljust(10," ") + \
            "Struct".ljust(10," ")
        print(header + "\n")

        final_inst = list(sorted(self.pipeline.completed, key=lambda x: x.result["IF"]))

        for inst in final_inst:
            excycles = inst.result["EX"]  if inst.result["MEM"] == "-" else inst.result["MEM"]
            result = inst.print().ljust(20," ") + \
                str(inst.result["IF"]).ljust(10," ") + \
                str(inst.result["ID"]).ljust(10," ") + \
                str(excycles).ljust(10," ") + \
                str(inst.result["WB"]).ljust(10," ") + \
                str(inst.hazards["raw"]).ljust(10," ") + \
                str(inst.hazards["war"]).ljust(10," ") + \
                str(inst.hazards["waw"]).ljust(10," ") + \
                str(inst.hazards["struct"]).ljust(10," ")
            print(result, "\n")

        print("Total number of access requests for instruction cache:", self.pipeline.access_count)
        print("Number of instruction cache hits:", self.pipeline.hit_count, "\n")
        print("Total number of access requests for data cache:", self.pipeline.dcache.access_count)
        print("Number of data cache hits:", self.pipeline.dcache.hit_count)

    def print_result(self):
        header = "instruction".ljust(20," ") + \
            "FT".ljust(10," ") + \
            "ID".ljust(10," ") + \
            "EX".ljust(10," ") + \
            "MEM".ljust(10," ") + \
            "WB".ljust(10," ") + \
            "RAW".ljust(10," ") + \
            "WAR".ljust(10," ") + \
            "WAW".ljust(10," ") + \
            "Struct".ljust(10," ")
        print(header + "\n")

        final_inst = list(sorted(self.pipeline.completed, key=lambda x: x.result["IF"]))

        for inst in final_inst:
            result = inst.print().ljust(20," ") + \
                str(inst.result["IF"]).ljust(10," ") + \
                str(inst.result["ID"]).ljust(10," ") + \
                str(inst.result["EX"]).ljust(10," ") + \
                str(inst.result["MEM"]).ljust(10," ") + \
                str(inst.result["WB"]).ljust(10," ") + \
                str(inst.hazards["raw"]).ljust(10," ") + \
                str(inst.hazards["war"]).ljust(10," ") + \
                str(inst.hazards["waw"]).ljust(10," ") + \
                str(inst.hazards["struct"]).ljust(10," ")
            print(result, "\n")

        print("Total number of access requests for instruction cache:", self.pipeline.access_count)
        print("Number of instruction cache hits:", self.pipeline.hit_count, "\n")
        print("Total number of access requests for data cache:", self.pipeline.dcache.access_count)
        print("Number of data cache hits:", self.pipeline.dcache.hit_count)

# parser = Parser(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
parser = Parser("inst.txt","data.txt","reg.txt","config.txt")
# parser = Parser("test_cases/test_case_1/inst.txt","test_cases/test_case_1/data.txt","test_cases/test_case_1/reg.txt","test_cases/test_case_1/config.txt")
# parser = Parser("test_cases/test_case_2/inst.txt","test_cases/test_case_2/data.txt","test_cases/test_case_2/reg.txt","test_cases/test_case_2/config.txt")
# parser = Parser("test_cases/test_case_3/inst.txt","test_cases/test_case_3/data.txt","test_cases/test_case_3/reg.txt","test_cases/test_case_3/config.txt")

mips_sim = Simulation("result.txt")
mips_sim.set_parser_data(parser)
mips_sim.run(300)
