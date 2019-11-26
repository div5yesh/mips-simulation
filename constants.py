AVAILABLE = 1
BUSY = 0

InstructionType = {
    "data": ["lw","sw","l.d","s.d"],
    "alu":  ["dadd", "daddi", "dsub", "dsubi", "and", "andi", "or", "ori", "add.d", "mul.d", "div.d", "sub.d"],
    "ctrl": ["j", "beq", "bne"],
    "hlt":  ["hlt"]
}

class Stage:
    IF = 0
    ID = 1
    EX = 2
    WB = 3