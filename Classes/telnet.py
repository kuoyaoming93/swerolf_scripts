import telnetlib

class Telnet:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.tn = []
        self.regs = [
                        "ra",   "sp",   
                        "t0",   "t1",   "t2",   "fp",   "s1", 
                        "a0",   "a1",   "a2",   "a3",   "a4",
                        "a5",   "a6",   "a7",   "s2",   "s3",
                        "s4",   "s5",   "s6",   "s7",   "s8",
                        "s9",   "s10",  "s11",  "t3",   "t4",
                        "t5",   "t6",   "pc",   "minstret", "mcause"
                    ]
        #self.regs = [
        #                "zero", "ra",   "sp",   "gp",   "tp", 
        #                "t0",   "t1",   "t2",   "fp",   "s1", 
        #                "a0",   "a1",   "a2",   "a3",   "a4",
        #                "a5",   "a6",   "a7",   "s2",   "s3",
        #                "s4",   "s5",   "s6",   "s7",   "s8",
        #                "s9",   "s10",  "s11",  "t3",   "t4",
        #                "t5",   "t6",   "pc",   "minstret", "mcause"
        #            ]
     
    def connect(self):
        self.tn = telnetlib.Telnet(self.host,self.port)
        self.tn.read_until('\n')

    def reset(self):
        self.tn.write(b"reset halt\n")
        self.tn.read_until('\n')
        self.tn.read_until('\n')

    def halt(self):
        self.tn.write(b"halt\n")
        self.tn.read_until('\n')
        self.tn.read_until('\n')
    
    def loadImage(self, path):
        command = "load_image " + path + "\n"
        self.tn.write(command)
        self.tn.read_until('\n')
        self.tn.read_until('\n')
        self.tn.read_until('\n')
        self.tn.read_until('\n')
    
    def init(self):
        self.tn.write(b"reg pc 0\n")
        self.tn.read_until('\n')
        self.tn.read_until('\n')
        self.tn.read_until('\n')

    def cleanMcause(self):
        self.tn.write(b"reg mcause 0\n")
        self.tn.read_until('\n')
        self.tn.read_until('\n')
        self.tn.read_until('\n')

    def resume(self):
        self.tn.write(b"resume\n")
        self.tn.read_until('\n')
        self.tn.read_until('\n')

    def firstStep(self):
        self.tn.write(b"step\n")
        self.tn.read_until('\n')
        self.tn.read_until('\n')

    def step(self):
        self.tn.write(b"step\n")
        self.tn.read_until('\n')
        

    def read_reg(self, num):
        command = "reg " + self.regs[num] + " force\n"
        self.tn.write(command)
        self.tn.read_until('\n')
        cmd = self.tn.read_until('\n')
        cmdStr = cmd.split(' ')
        self.tn.read_until('\n')
        return cmdStr[2]

    def exit(self):
        self.tn.write(b"exit\n")

    def run(self, path):
        self.reset()
        self.loadImage(path)
        self.init()
        self.cleanMcause()