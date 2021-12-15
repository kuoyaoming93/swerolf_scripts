import serial

class CPU: 
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.id = serial.Serial(port, baud, timeout=60)

    def close(self):
        self.id.close()

    def readUntil(self,pattern):
        buf = self.id.read_until(pattern,100)
        return buf


    def printOut(self):
        buf = self.readUntil('>').decode("utf-8")
        #print(buf)
        return buf





