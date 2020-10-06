import json
import sys
from bluepy import btle
from parser import Parser, ParseException


MAX_BUFFER_SIZE = 100

class HandleNotification(btle.DefaultDelegate):
    def __init__(self,params):
        btle.DefaultDelegate.__init__(self)
        
        self.parser = Parser()
        self.buffer = bytearray()

    def handleNotification(self, cHandle, data):
        self.buffer.extend(data)
        assert(len(self.buffer) < MAX_BUFFER_SIZE)
        
        result = True

        while result is not None:
            try:
                result = self.process_buffer()
            except ParseException as error:
                continue

            if result:
                print(json.dumps(result))
                
    def process_buffer(self):
        msg_len = 0

        # try to find start of valid message
        for i in range(len(self.buffer)):
            msg_len = self.parser.calc_msg_len(self.buffer[i:])

            if msg_len:
                break
        else:
            # no possible message found
            self.buffer.clear() 

            return

        # delete stuff before start
        del self.buffer[:i]

        # check if we have enough data
        if len(self.buffer) < msg_len:
            return

        # pull out message from buffer 
        msg = self.buffer[:msg_len]
        del self.buffer[:msg_len]

        # parse message
        res = self.parser.parse(msg)
        
        return res

def start(mac_addr):
	while True:
		try:
		    p = btle.Peripheral(mac_addr)
		    p.setDelegate(HandleNotification(0))
		
		    while True:
		        if p.waitForNotifications(1.0):
		            continue
		except KeyboardInterrupt:
			break
		except:
			pass 

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('missing MAC address')
        sys.exit()

    start(sys.argv[1])