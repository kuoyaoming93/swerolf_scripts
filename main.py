import time
import subprocess 
import os
import signal 

from Classes.telnet import Telnet

breakpoint = "0x00001ea8"

f = open("registers.txt", "w")

proc = subprocess.Popen(["openocd","-f", "./swervolf_nexys_debug.cfg"])
time.sleep(5)

tn = Telnet("localhost", 4444)
tn.connect()
tn.run("/home/kuo/gits/Cores-SweRVolf/sw/baremetal_demo/aes.elf")

print("Start time: " + time.asctime())

tn.firstStep()

pc_idx = 29
aux = ""
temporal_reg = ""
pc = tn.read_reg(pc_idx).decode("utf-8")

while (pc.find(breakpoint) == -1) :
    for i in range(len(tn.regs)):
        #temporal_reg = tn.read_reg(i).decode("utf-8")
        if i != pc_idx:
            temporal_reg = tn.read_reg(i).decode("utf-8")
        else:
            temporal_reg = pc
        aux = aux + temporal_reg.rstrip() + ","
        #print(str(i) + ": " + tn.read_reg(i))
    f.write(aux + "\n")
    
    tn.step()
    aux = ""
    pc = tn.read_reg(pc_idx).decode("utf-8")

print("Stop time: " + time.asctime())

f.close()
tn.exit()

proc.terminate()
os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

