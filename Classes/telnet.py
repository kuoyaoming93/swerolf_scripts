import telnetlib

class Telnet:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.tn = []
     
    def connect(self):
        self.tn = telnetlib.Telnet(self.host,self.port)
        self.tn.read_until('\n')

    def reset(self):
        self.tn.write(b"reset halt\n")
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

    def resume(self):
        self.tn.write(b"resume\n")
        self.tn.read_until('\n')

    def exit(self):
        self.tn.write(b"exit\n")

    def run(self, path):
        self.reset()
        self.loadImage(path)
        self.init()
        self.resume()