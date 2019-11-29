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
        self.pipeline = Pipeline()

    def set_parser_data(self, parser_data):
        self.data = parser_data
        self.pipeline.set_unit_data(parser.config)

    def next_tick(self):
        self.clock += 1
        curr_inst = self.data.program[self.program_counter]
        instruction = Instruction(curr_inst)
        if self.pipeline.stages[Stage.IF]:
            self.pipeline.schedule(instruction)
            self.program_counter += 1

        self.pipeline.update(self.clock)
        return curr_inst

    def run(self, cycles):
        inst = [""]
        # while self.clock < cycles:
        while inst[0] != "hlt": 
            # cmd = input()
            inst = self.next_tick()

        self.print_result()

    def print_result(self):
        header = "opcode".rjust(15," ") + \
            "IF".rjust(10," ") + \
            "ID".rjust(10," ") + \
            "EX".rjust(10," ") + \
            "MEM".rjust(10," ") + \
            "WB".rjust(10," ")
        print(header)

        for inst in self.pipeline.completed:
            result = inst.opcode.rjust(15," ") + \
                str(inst.result["IF"]).rjust(10," ") + \
                str(inst.result["ID"]).rjust(10," ") + \
                str(inst.result["EX"]).rjust(10," ") + \
                str(inst.result["MEM"]).rjust(10," ") + \
                str(inst.result["WB"]).rjust(10," ")
            print(result, "\n")

parser = Parser("inst.txt","data.txt","reg.txt","config.txt")
mips_sim = Simulation("result.txt")
mips_sim.set_parser_data(parser)
mips_sim.run(25)

# mips_sim = Simulation(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])