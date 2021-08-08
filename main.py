from Classes.telnet import Telnet

tn = Telnet("localhost", 4444)

tn.connect()
tn.run("/home/kuo/gits/Cores-SweRVolf/sw/hello_uart.elf")
tn.step()
print(tn.read_reg(32))
tn.exit()