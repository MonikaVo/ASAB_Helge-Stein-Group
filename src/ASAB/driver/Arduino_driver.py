import serial
import time

# Assign the correct Port on your PC
PORT = '<port>' # edited prior to publication

class Ardurelay():
    
    def __init__(self):
        self.ardu_port = PORT

    def connect_relay(self):
        print(f'initiating Arduino_Relay on PORT: {self.ardu_port}...')
        self.serialcomm = serial.Serial(port = self.ardu_port, baudrate = 9600, timeout = 1)
        time.sleep(0.05)
        print(f'Initiating Arduino_Relay complete')
    
    def read(self):
        read_val = ''
        for i in range(10):
            read_val = self.serialcomm.readline().decode('ascii')
            time.sleep(0.1)
            if read_val != '':
                break
            elif i == 10:
                read_val = "Read timeout"
        return read_val

    def operate_relay(self, relayNr, state):
        print(f'Relay_{relayNr} is {state}!')
        cmd = "{}_{}/n".format(str(relayNr),str(state))
        self.serialcomm.write(cmd.encode())
    
    def disconnect_relay(self):
        self.serialcomm.close()
        return 'Arduino_Relay disconnected!'
