import re

class Parser:
    def __init__(self, input_file, data_file, reg_file, config_file):
        self.config = self.parse_config(config_file)
        self.program = self.parse_program(input_file)
        self.memory = self.read_memory(int("100",16), data_file)
        self.registers = self.read_registers(reg_file)

    def read_file(self, file):
        fp = open(file, "r")
        data = fp.read()
        fp.close()
        return data.lower()

    def read_registers(self, reg_file):
        data = self.read_data(reg_file)
        keys = list(map(lambda x: "r" + str(x), range(0,31)))
        return dict(zip(keys, data))

    def read_memory(self, base, data_file):
        data = self.read_data(data_file)
        keys = list(range(base, base + len(data)))
        return dict(zip(keys, data))

    def read_data(self, data_file):
        data = self.read_file(data_file).split("\n")
        return list(map(lambda x: int(x, 2), data))

    def parse_config(self, config_file):
        config_data = self.read_file(config_file).replace(" ","").split("\n")
        config = []
        for item in config_data:
            info = re.split("[:,]", item)
            config += [info]
        
        return config

    def parse_program(self, program_file):
        program_data = self.read_file(program_file).split("\n")
        program = []
        for instruction in program_data:
            info = list(filter(lambda x: x != "",re.split("[:  ,]", instruction)))
            program += [info]

        return program