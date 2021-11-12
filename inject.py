import time
import subprocess
import os
import sys
import signal
import filecmp

my_lib_path = os.path.abspath('./Classes')
sys.path.append(my_lib_path)
from telnet import Telnet

TESTS = 10
BREAKPOINT = "0x00001ea8"
PROGRAM_PATH = "/home/pi/aes.elf"
PC_IDX = 29
MCAUSE_IDX = 30
MCAUSE_VALUE = "0x00000000"

LOG_PATH = "rountine.log"
ORIGINAL_PATH = "original.txt"
INJECT_PATH = "inject.txt"

# Time out, 10 secs
TIMEOUT = 10      

# How many success and errors
errors = 0
success = 0
# Error type
faults = 0
hangs = 0
mismatch = 0
timeout = 0

log = open(LOG_PATH, "w")

for num in range(TESTS+1):
    if num==0:
        f = open(ORIGINAL_PATH, "w")
    else:
        f = open(INJECT_PATH, "w")

    # OpenOCD server open
    proc = subprocess.Popen(["openocd","-f", "./swervolf_nexys_debug.cfg"])
    time.sleep(2.5)

    # Connect and load the .elf file
    tn = Telnet("localhost", 4444)
    tn.connect()
    tn.run(PROGRAM_PATH)

    # Print start time
    log.write("[TEST "+ str(num) + "] " +"Start time: " + str(time.asctime()) + "\n")
    log.flush()

    # Run the program until "BREAKPOINT"
    if num==0:
        tn.firstStep()
    else:
        tn.step()
    tn.setBP(BREAKPOINT)
    pc = tn.read_reg(PC_IDX).decode("utf-8")
    mcause = tn.read_reg(MCAUSE_IDX).decode("utf-8")

    # Set timer
    time1 = time.time()
    timeout = 0

    while ((pc.find(BREAKPOINT) == -1) and (mcause.find(MCAUSE_VALUE) != -1)) :
        tn.resume()
        time.sleep(0.5)
        tn.halt()
        pc = tn.read_reg(PC_IDX).decode("utf-8")
        mcause = tn.read_reg(MCAUSE_IDX).decode("utf-8")
        time2 = time.time()
        if (time2-time1) > TIMEOUT:
            timeout = 1
            break

    # Read all registers
    aux = ""
    for i in range(len(tn.regs)):
        temporal_reg = tn.read_reg(i).decode("utf-8")
        aux = aux + temporal_reg.rstrip() + ","

    # Write the registers in file
    f.write(aux + "\n")
    f.flush()

    # Unset BP
    #tn.unsetBP()

    # Print stop time
    log.write("[TEST "+ str(num) + "] " +"Stop time: " + str(time.asctime()) + "\n")
    log.flush()

    # Close file and connection
    f.close()
    tn.exit()

    # Close OpenOCD
    time.sleep(0.5)
    proc.terminate()

    # Comparison between files
    if num!=0:
        if(filecmp.cmp(ORIGINAL_PATH, INJECT_PATH)):
            success = success + 1
            log.write("OK\n")
        else:
            errors = errors + 1
            if timeout ==1 :
                log.write("HANG error\n")
                hangs = hangs + 1
            elif mcause.find(MCAUSE_VALUE) == -1:
                log.write("FAULT error\n")
                faults = faults + 1
            else:
                log.write("DATA error\n")
                mismatch = mismatch + 1
        
        log.write('\n')
        log.flush()

        # Print report
        log.write("Number of tests: " + str(num) + "\n")
        log.write("Number of errors: " + str(errors) + "\n")
        log.write("Hangs: " + str(hangs) + "\n")
        log.write("Faults: " + str(faults) + "\n")
        log.write("Mismatches: " + str(mismatch) + "\n")
        log.flush()
        log.write('\n')
        log.flush()

    log.write('\n')
    log.flush()
            
# Print report
log.write("-------------------------------------\n")
log.write("--------------- Summary -------------\n")
log.write("-------------------------------------\n")
log.write("Total tests: " + str(TESTS) + "\n")
log.write("Number of errors: " + str(errors) + " (" + str(100*errors/TESTS) + "%)" + "\n")
log.write("Faults: " + str(faults) + " (" + str(100*faults/TESTS) + "%)" + "\n")
log.write("Hangs: " + str(hangs) + " (" + str(100*hangs/TESTS) + "%)" + "\n")
log.write("Mismatches: " + str(mismatch) + " (" + str(100*mismatch/TESTS) + "%)" + "\n")
log.flush()

log.close()
os.killpg(os.getpgid(proc.pid), signal.SIGTERM)






