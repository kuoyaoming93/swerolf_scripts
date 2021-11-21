from __future__ import division
import time
import subprocess
import os
import sys
import signal
import filecmp
#import RPi.GPIO as GPIO
from gpiozero import LED


my_lib_path = os.path.abspath('./Classes')
sys.path.append(my_lib_path)
from telnet import Telnet
from sem import SemIP
from cpu import CPU

# Configuration
SEM_PORT = '/dev/ttyUSB2'
SEM_BAUDRATE = 230400
CPU_PORT = '/dev/ttyUSB1'
CPU_BAUDRATE = 57600

TESTS = 10000
ERROR_EACH = 107
START_POSITION = 1

BREAKPOINT = "0x00001e90"
PROGRAM_PATH = "/home/pi/gits/swervolf_scripts/elf/aes.elf"
PC_IDX = 29
MCAUSE_IDX = 30
MCAUSE_VALUE = "0x00000000"

LOG_PATH = "routine.log"
ORIGINAL_PATH = "original.txt"
INJECT_PATH = "inject.txt"
INJECT_FILE = "./data/lsu.txt"


# Time out, 5 secs
TIMEOUT = 10      

# How many success and errors
errors = 0

# Error type
faults = 0
hangs = 0
mismatch = 0
result_mismatch = 0

# Set GPIO to program 
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(40, GPIO.OUT)
led = LED(21)

log = open(LOG_PATH, "w")
injFile = open(INJECT_FILE, "r")
address = ""

# Read addresses until start position
for i in range(START_POSITION):
    address = injFile.readline().rstrip()

for num in range(TESTS+1):

    timeout = 0
    mcause = 0
    result_error = 0

    # Reset board
    #GPIO.output(40, False)
    led.off()
    time.sleep(0.5)
    #GPIO.output(40, True)
    led.on()

    # Connect SEM IP
    sem = SemIP(SEM_PORT,SEM_BAUDRATE)
    sem.printOut()
    sem.injectState()

    # Connect CPU UART
    cpu = CPU(CPU_PORT,CPU_BAUDRATE)

    time.sleep(2.5)
    if num==0:
        f = open(ORIGINAL_PATH, "w")
    else:
        f = open(INJECT_PATH, "w")
        if num!=1:
            for i in range(ERROR_EACH):
                address = injFile.readline().rstrip()
            #print(address)
        log.write("[TEST "+ str(num) + "] " +"Injection address: " + address + "\n")
        sem.injectError(address)

    # Print start time
    log.write("[TEST "+ str(num) + "] " +"Start time: " + str(time.asctime()) + "\n")
    log.flush()

    # OpenOCD server open
    proc = subprocess.Popen(["openocd","-f", "./board1.cfg"])
    time.sleep(3)

    # If we can open
    if proc.poll()==None:
        # Connect and load the .elf file
        tn = Telnet('localhost', 4444)

        status = 0
        try:
            tn.connect()
            print("TELNET CONNECT")
            status = 0
        except:
            timeout = 1
            print("ERROR: TELNET CONNECT")
            status = 1

        # If it is possible to connect, continue 
        if status == 0:
            try:
                tn.run(PROGRAM_PATH)
                print("TELNET LOADING PROGRAM")
            except:
                timeout = 1
                print("ERROR: TELNET LOADING PROGRAM")

            try:
                tn.firstStep()
                print("STEPPING PROGRAM")
            except:
                timeout = 1
                print("ERROR: STEPPING PROGRAM")

            try:
                tn.setBP(BREAKPOINT)
                print("SETTING BREAKPOINT")
            except:
                timeout = 1
                print("ERROR: SETTING BREAKPOINT")

            try: 
                pc = tn.read_reg(PC_IDX).decode("utf-8")
                print("READING PC")
                print(pc)
            except:
                pc = BREAKPOINT
                timeout = 1
                print("ERROR: READ PC")
                log.write("ERROR: READ PC\n")

            if "0x" in pc:
                try:
                    mcause = tn.read_reg(MCAUSE_IDX).decode("utf-8")
                    print("READING MCAUSE")
                except:
                    mcause = "0xFFFFFFFF"
                    timeout = 1
                    print("ERROR: READ MCAUSE")
                    log.write("ERROR: READ MCAUSE\n")
            else:
                mcause = "0xFFFFFFFF"
                timeout = 1

            # Set timer
            time1 = time.time()
            cpu_exit_status = "START"
            while ((pc.find(BREAKPOINT) == -1) and (mcause.find(MCAUSE_VALUE) != -1)) :
                if "0x" in pc:
                    print("RESUME")
                    tn.resume()
                else:
                    timeout = 1
                    break

                time2 = time.time()
                if (time2-time1) > TIMEOUT:
                    timeout = 1
                    break

                if "START" in cpu_exit_status:
                    try:
                        cpu_exit_status = cpu.printOut()
                        log.write("CPU OUTPUT: " + cpu_exit_status + "\n")
                    except:
                        result_error = 1
                time.sleep(0.1)

                if "0x" in pc:
                    print("HALT")
                    tn.halt()
                else:
                    timeout = 1
                    break

                if "FAIL" in cpu_exit_status:
                    result_error = 1
                    break

                try:
                    pc = tn.read_reg(PC_IDX).decode("utf-8")
                    print("READ PC")
                except:
                    pc = BREAKPOINT
                    timeout = 1
                    print("ERROR: READ PC")
                    log.write("ERROR: READ PC\n")
                    break
                
                if "0x" in pc:
                    try:
                        mcause = tn.read_reg(MCAUSE_IDX).decode("utf-8")
                        print("READ MCAUSE")
                    except:
                        mcause = "0xFFFFFFFF"
                        timeout = 1
                        print("ERROR: READ MCAUSE")
                        log.write("ERROR: READ MCAUSE\n")
                        break
                else: 
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
    #if num!=0:
    #    sem.injectError(address)

    # Close SEM IP
    sem.close()
    cpu.close()

    # Comparison between files
    if num!=0:
        if timeout ==1 :
            log.write("HANG error\n")
            hangs = hangs + 1
            errors = errors + 1
        elif mcause.find(MCAUSE_VALUE) == -1:
            log.write("FAULT error\n")
            faults = faults + 1
            errors = errors + 1
        elif result_error == 1:
            log.write("DATA mismatch error\n")
            result_mismatch = result_mismatch + 1
            errors = errors + 1
        elif (filecmp.cmp(ORIGINAL_PATH, INJECT_PATH) == False):
            log.write("REGISTER error\n")
            mismatch = mismatch + 1
            errors = errors + 1
        else:
            log.write("OK\n")
        
        log.write('\n')
        log.flush()

        # Print report
        number_errors = float(100*errors/num)
        number_errors_float = "{:.2f}".format(number_errors)
        number_faults = float(100*faults/num)
        number_faults_float = "{:.2f}".format(number_faults)
        number_hangs = float(100*hangs/num)
        number_hangs_float = "{:.2f}".format(number_hangs)
        number_mismatch = float(100*mismatch/num)
        number_mismatch_float = "{:.2f}".format(number_mismatch)
        number_result_error = float(100*result_mismatch/num)
        number_result_error_float = "{:.2f}".format(number_result_error)
        log.write("Total number of tests: " + str(num) + "\n")
        log.write("Total number of errors: " + str(errors) + " (" + str(number_errors_float) + "%)" + "\n")
        log.write("Number of exceptions: " + str(faults) + " (" + str(number_faults_float) + "%)" + "\n")
        log.write("Number of CPU Hangs: " + str(hangs) + " (" + str(number_hangs_float) + "%)" + "\n")
        log.write("Number of result mismatches: " + str(result_mismatch) + " (" + str(number_result_error_float) + "%)" + "\n")
        log.write("Number of internal reg mismatches: " + str(mismatch) + " (" + str(number_mismatch_float) + "%)" + "\n")
        log.flush()
        log.write('\n')
        log.flush()

    log.write('\n')
    log.flush()
            
# Print report
log.write("-------------------------------------\n")
log.write("--------------- Summary -------------\n")
log.write("-------------------------------------\n")
number_errors = float(100*errors/num)
number_errors_float = "{:.2f}".format(number_errors)
number_faults = float(100*faults/num)
number_faults_float = "{:.2f}".format(number_faults)
number_hangs = float(100*hangs/num)
number_hangs_float = "{:.2f}".format(number_hangs)
number_mismatch = float(100*mismatch/num)
number_mismatch_float = "{:.2f}".format(number_mismatch)
number_result_error = float(100*result_mismatch/num)
number_result_error_float = "{:.2f}".format(number_result_error)
log.write("Total number of tests: " + str(TESTS) + "\n")
log.write("Total number of errors: " + str(errors) + " (" + str(number_errors_float) + "%)" + "\n")
log.write("Number of exceptions: " + str(faults) + " (" + str(number_faults_float) + "%)" + "\n")
log.write("Number of CPU Hangs: " + str(hangs) + " (" + str(number_hangs_float) + "%)" + "\n")
log.write("Number of result mismatches: " + str(result_mismatch) + " (" + str(number_result_error_float) + "%)" + "\n")
log.write("Number of internal reg mismatches: " + str(mismatch) + " (" + str(number_mismatch_float) + "%)" + "\n")
log.flush()

log.close()
injFile.close()
os.killpg(os.getpgid(proc.pid), signal.SIGTERM)






