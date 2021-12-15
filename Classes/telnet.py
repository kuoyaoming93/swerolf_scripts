import telnetlib

class Telnet:
    def __init__(self, host, port):
        self.timeout = 5
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
                        "t5",   "t6",   "pc",   "mcause"
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
        self.tn.read_until(b'\n',timeout=self.timeout)

    def reset(self):
        self.tn.write(b"reset halt\n")
        self.tn.read_until(b'\n',timeout=self.timeout)
        self.tn.read_until(b'\n',timeout=self.timeout)

    def halt(self):
        self.tn.write(b"halt\n")
        self.tn.read_until(b'\n',timeout=self.timeout)
    
    def loadImage(self, path):
        command = "load_image " + path + "\n"
        self.tn.write(command.encode())
        self.tn.read_until(b'\n',timeout=self.timeout)
        self.tn.read_until(b'\n',timeout=self.timeout)
        self.tn.read_until(b'\n',timeout=self.timeout)
        self.tn.read_until(b'\n',timeout=self.timeout)
    
    def init(self):
        self.tn.write(b"reg pc 0\n")
        self.tn.read_until(b'\n',timeout=self.timeout)
        self.tn.read_until(b'\n',timeout=self.timeout)
        self.tn.read_until(b'\n',timeout=self.timeout)

    def cleanMcause(self):
        self.tn.write(b"reg mcause 0\n")
        self.tn.read_until(b'\n',timeout=self.timeout)
        self.tn.read_until(b'\n',timeout=self.timeout)
        self.tn.read_until(b'\n',timeout=self.timeout)

    def resume(self):
        self.tn.write(b"resume\n")
        self.tn.read_until(b'\n',timeout=self.timeout)

    def firstStep(self):
        self.tn.write(b"step\n")
        self.tn.read_until(b'\n',timeout=self.timeout)
        self.tn.read_until(b'\n',timeout=self.timeout)

    def step(self):
        self.tn.write(b"step\n")
        self.tn.read_until(b'\n',timeout=self.timeout)

    def setBP(self,address):
        command = "bp " + address + " 1 hw\n"
        self.tn.write(command.encode())
        self.tn.read_until(b'\n',timeout=self.timeout)
        self.tn.read_until(b'\n',timeout=self.timeout)
        self.tn.read_until(b'\n',timeout=self.timeout)
    
    def unsetBP(self):
        self.tn.write(b"rbp all\n")
        self.tn.read_until(b'\n',timeout=self.timeout)
        

    def read_reg(self, num):
        command = "reg " + self.regs[num] + " force\n"
        self.tn.write(command.encode())
        register = self.regs[num]+' (/32): '
        self.tn.read_until(register.encode(),timeout=self.timeout)
        cmd = self.tn.read_until(b'\n',timeout=self.timeout)
        return cmd.decode("utf-8").replace("\n","")
        #command = "reg " + self.regs[num] + " force\n"
        #self.tn.write(command)
        #self.tn.read_until('\n',timeout=self.timeout)
        #cmd = self.tn.read_until('\n',timeout=self.timeout)
        #cmdStr = cmd.split(' ')
        #self.tn.read_until('\n',timeout=self.timeout)
        #return cmdStr[2]

    def exit(self):
        self.tn.write(b"exit\n")

    def run(self, path):
        self.reset()
        self.loadImage(path)
        self.init()
        self.cleanMcause()
    
    def run2(self):
        self.reset()
        self.init()
        self.cleanMcause()