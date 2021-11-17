import serial

class SemIP: 
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.id = serial.Serial(port, baud,timeout=15)

    def close(self):
        self.id.close()
        
    def readLine(self):
        buf = ""
        while '\r' not in buf:
            buf += self.id.read(1)
        return buf

    def read(self, num):
        buf = self.id.read(num)
        return buf

    def readUntil(self,pattern):
        buf = self.id.read_until(pattern,100)
        return buf

    def write(self, command):
        num = self.id.write(command + "\r")
        return num

    def printOut(self):
        buf = self.readUntil('>').replace("\r","\r\n")
        print(buf)
        return buf

    def injectState(self):
        self.write("I")
        return self.printOut()

    def observeState(self):
        self.write("O")
        return self.printOut()
    
    def injectError(self,address):
        self.write("N " + address)
        return self.printOut()

    def queryAddr(self,address):
        self.write("Q " + address)
        return self.printOut()



