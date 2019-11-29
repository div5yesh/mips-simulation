class FunctionalUnit():
    def __init__(self, info):
        self.unit = info[0]
        self.latency = int(info[1])
        self.pipelined = True if len(info) > 2 and info[2] == "yes" else False

    def __str__(self):
        return self.unit + ":" + str(self.latency) + "," + str(self.pipelined)

    def set_execute_data(self):
        self.instruction = None
        self.ri = False
        self.rj = False
        self.rk = False