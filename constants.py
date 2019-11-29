from enum import Enum

AVAILABLE = 1
BUSY = 0

# InstructionType = {
#     "data": ["lw","sw","l.d","s.d"],
#     "alu":  ["dadd", "daddi", "dsub", "dsubi", "and", "andi", "or", "ori", "add.d", "mul.d", "div.d", "sub.d"],
#     "ctrl": ["j", "beq", "bne"],
#     "hlt":  ["hlt"]
# }

InstructionType = {
    "int": ["dadd","daddi","dsub","dsubi","and","andi","or","ori","lw","sw","l.d","s.d"],
    "fpadder": ["add.d", "sub.d"],
    "fpmultiplier": ["mul.d"],
    "fpdivider": ["div.d"],
    # "mainmemory": ["lw","sw","l.d","s.d"],
    "ctrl": ["j", "bne", "beq"],
    "hlt": ["hlt"]
}

class Stage(Enum):
    IF = 0
    ID = 1
    EX = 2
    MEM = 3
    WB = 4
    FIN = 5