import time
import subprocess 
import os
import signal 

from Classes.telnet import Telnet


TESTS = 10
BREAKPOINT = "0x00001ea8"
PROGRAM_PATH = "/home/kuo/gits/Cores-SweRVolf/sw/baremetal_demo/aes.elf"
PC_IDX = 29
MCAUSE_IDX = 31
MCAUSE_VALUE = "0x00000000"

LOG_PATH = "rountine.log"
ORIGINAL_PATH = "original.txt"
INJECT_PATH = "inject.txt"

# How many success and errors
errors = 0
success = 0
# Error type
faults = 0
hangs = 0
mismatch = 0

# OpenOCD server open
proc = subprocess.Popen(["openocd","-f", "./swervolf_nexys_debug.cfg"])
time.sleep(2)

# Connect and load the .elf file
tn = Telnet("localhost", 4444)
tn.connect()
tn.run(PROGRAM_PATH)
tn.setBP(BREAKPOINT)
#print("pepe")
tn.resume()
time.sleep(2)
tn.halt()

mcause = tn.read_reg(MCAUSE_IDX).decode("utf-8")
print(mcause)

proc.terminate()
os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

