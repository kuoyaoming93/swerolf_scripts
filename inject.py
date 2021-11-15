import time
import subprocess
import os
import sys
import signal
import filecmp
import RPi.GPIO as GPIO

my_lib_path = os.path.abspath('./Classes')
sys.path.append(my_lib_path)
from telnet import Telnet
from sem import SemIP

TESTS = 10000
#BREAKPOINT = "0x00001ea8"
BREAKPOINT = "0x00001e14"
PROGRAM_PATH = "/home/pi/gits/swervolf_scripts/elf/aes128.elf"
PC_IDX = 29
MCAUSE_IDX = 30
MCAUSE_VALUE = "0x00000000"

LOG_PATH = "rountine.log"
ORIGINAL_PATH = "original.txt"
INJECT_PATH = "inject.txt"
INJECT_FILE = "./exu.txt"
ERROR_EACH = 70

# Time out, 10 secs
TIMEOUT = 5      

# How many success and errors
errors = 0
success = 0
# Error type
faults = 0
hangs = 0
mismatch = 0

# Set GPIO to program 
GPIO.setmode(GPIO.BOARD)
GPIO.setup(40, GPIO.OUT)

log = open(LOG_PATH, "w")
injFile = open(INJECT_FILE, "r")
address = ""

timeout = 0
mcause = 0
for num in range(TESTS+1):

    # Reset board
    GPIO.output(40, False)
    time.sleep(0.5)
    GPIO.output(40, True)
    sem = SemIP('/dev/ttyUSB2',230400)
    sem.printOut()
    sem.injectState()
    time.sleep(2.5)
    if num==0:
        f = open(ORIGINAL_PATH, "w")
    else:
        f = open(INJECT_PATH, "w")
        for i in range(ERROR_EACH):
            address = injFile.readline().rstrip()
            #print(address)
        log.write("[TEST "+ str(num) + "] " +"Injection address: " + address + "\n")
        sem.injectError(address)

    # Print start time
    log.write("[TEST "+ str(num) + "] " +"Start time: " + str(time.asctime()) + "\n")
    log.flush()

    # OpenOCD server open
    proc = subprocess.Popen(["openocd","-f", "./swervolf_nexys_debug.cfg"])
    time.sleep(2.5)

    # If we can open
    if proc.poll()==None:
        # Connect and load the .elf file
        tn = Telnet("localhost", 4444)
        tn.connect()
        tn.run(PROGRAM_PATH)

        # Run the program until "BREAKPOINT"
        #if num==0:
        #    tn.firstStep()
        #else:
        #    tn.step()

        # Set timer
        time1 = time.time()
        timeout = 0

        tn.firstStep()
        tn.setBP(BREAKPOINT)
        try: 
            pc = tn.read_reg(PC_IDX).decode("utf-8")
        except:
            pc = BREAKPOINT
            timeout = 1
            print("ERROR: READ PC")
            log.write("ERROR: READ PC\n")

        try:
            mcause = tn.read_reg(MCAUSE_IDX).decode("utf-8")
        except:
            mcause = 1
            timeout = 1
            print("ERROR: READ MCAUSE")
            log.write("ERROR: READ MCAUSE\n")

    
        while ((pc.find(BREAKPOINT) == -1) and (mcause.find(MCAUSE_VALUE) != -1)) :
            tn.resume()
            time.sleep(0.1)
            tn.halt()
            try:
                pc = tn.read_reg(PC_IDX).decode("utf-8")
            except:
                pc = BREAKPOINT
                timeout = 1
                print("ERROR: READ PC")
                log.write("ERROR: READ PC\n")
                break
            
            try:
                mcause = tn.read_reg(MCAUSE_IDX).decode("utf-8")
            except:
                mcause = 1
                timeout = 1
                print("ERROR: READ MCAUSE")
                log.write("ERROR: READ MCAUSE\n")
                break
            time2 = time.time()
            if (time2-time1) > TIMEOUT:
                timeout = 1
                break

        # Read all registers
        aux = ""
        if timeout==0:
            for i in range(len(tn.regs)):
                try:
                    temporal_reg = tn.read_reg(i).decode("utf-8")
                except:
                    temporal_reg = ""
                    print("ERROR: READ ALL REGS")
                    log.write("ERROR: READ ALL REGS\n")
                    timeout = 1
                    break

                aux = aux + temporal_reg.rstrip() + ","

        # Write the registers in file
        f.write(aux + "\n")
        f.flush()

        tn.exit()
        # Close OpenOCD
        time.sleep(0.5)
        proc.terminate()
    else:
        timeout = 1

    # Print stop time
    log.write("[TEST "+ str(num) + "] " +"Stop time: " + str(time.asctime()) + "\n")
    log.flush()

    # Close file and connection
    f.close()

    # Reinject error
    if num!=0:
        sem.injectError(address)

    # Close SEM IP
    sem.close()

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
        log.write("Number of errors: " + str(errors) + " (" + str(100*errors/num) + "%)" + "\n")
        log.write("Faults: " + str(faults) + " (" + str(100*faults/num) + "%)" + "\n")
        log.write("Hangs: " + str(hangs) + " (" + str(100*hangs/num) + "%)" + "\n")
        log.write("Mismatches: " + str(mismatch) + " (" + str(100*mismatch/num) + "%)" + "\n")
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
injFile.close()
os.killpg(os.getpgid(proc.pid), signal.SIGTERM)






