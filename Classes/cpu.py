import serial

class CPU: 
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.id = serial.Serial(port, baud, timeout=50)

    def close(self):
        self.id.close()

    def readUntil(self,pattern):
        buf = self.id.read_until(pattern.encode("utf-8"),100)
        return buf


    def printOut(self):
        buf = self.readUntil('>')
        #print(buf)
        return buf.decode("utf-8")





