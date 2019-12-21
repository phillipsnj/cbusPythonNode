import json
import socket
import threading
import struct


class BasicNode(threading.Thread):
    def __init__(self, node_id, my_function):
        threading.Thread.__init__(self)
        self.function = my_function
        self.nodeId = node_id
        self.debug = False
        self.count = 0
        self.canId = 75
        self.priority1 = 2
        self.priority2 = 3
        self.manufId = 165
        self.moduleId = 255
        self.name = "PYTHON"
        self.minorVersion = "A"
        self.numEvents = 255
        self.numEventVariables = 0
        self.numNodeVariables = 0
        self.majorVersion = 1
        self.beta = 1  # 0  for normal version else beta version number
        self.consumer = False
        self.producer = True
        self.flim = False
        self.bootloader = False
        self.coe = False
        self.interface = 2  # 1 can, 2 ethernet
        self.events = {}
        self.variables = []
        self.parameters = []
        self.parameters.append(self.pad(20, 2))
        self.parameters.append(self.pad(self.manufId, 2))
        self.parameters.append(self.pad(ord(self.minorVersion), 2))  # Character
        self.parameters.append(self.pad(self.moduleId, 2))
        self.parameters.append(self.pad(self.numEvents, 2))
        self.parameters.append(self.pad(self.numNodeVariables, 2))
        self.parameters.append(self.pad(self.majorVersion, 2))
        self.parameters.append(self.pad(self.numNodeVariables, 2))
        self.parameters.append(self.pad(self.flags(), 2))
        self.parameters.append(self.pad(0, 2))
        self.parameters.append(self.pad(self.interface, 2))
        self.parameters.append(self.pad(0, 2))
        self.parameters.append(self.pad(0, 2))
        self.parameters.append(self.pad(0, 2))
        self.parameters.append(self.pad(0, 2))
        self.parameters.append(self.pad(0, 2))
        self.parameters.append(self.pad(0, 2))
        self.parameters.append(self.pad(0, 2))
        self.parameters.append(self.pad(0, 2))
        self.parameters.append(self.pad(self.manufId, 2))
        self.parameters.append(self.pad(self.beta, 2))

    @staticmethod
    def pad(num, length):
        return format(num, "0" + str(length) + "X")

    def get_header(self):
        return ":SB020N"

    @staticmethod
    def get_int(msg, start, length):
        return int(msg[start: start + length], 16)

    @staticmethod
    def get_str(msg, start, length):
        return msg[start: start + length]

    def get_op_code(self, msg):
        return self.get_str(msg, 7, 2)

    def get_node_id(self, msg):
        return int(self.get_str(msg, 9, 4), 16)

    def flags(self):
        flags = 0
        if self.consumer:
            flags += 1
        if self.producer:
            flags += 2
        if self.flim:
            flags += 4
        if self.bootloader:
            flags += 8
        if self.coe:
            flags += 16
        return flags

    def teach_long_event(self, node_id, event_id, variables):
        new_id = self.pad(node_id, 4) + self.pad(event_id, 4)
        self.events[new_id] = variables
        print(json.dumps(self.events, indent=4))

    def teach_short_event(self, event_id, variables):
        new_id = self.pad(0, 4) + self.pad(event_id, 4)
        self.events[new_id] = variables
        print(json.dumps(self.events, indent=4))

    def execute(self, msg):
        self.function(msg)

    def send(self, msg):
        print("Parent Send : " + msg)

    def acon(self, event_id):
        output = self.get_header() + "90" + self.pad(self.nodeId, 4) + self.pad(event_id, 4) + ";"
        self.send(output)

    def acof(self, event_id):
        output = self.get_header() + "91" + self.pad(self.nodeId, 4) + self.pad(event_id, 4) + ";"
        self.send(output)

    def ason(self, event_id):
        print("ASON :"+str(event_id))
        output = self.get_header() + "98" + self.pad(self.nodeId, 4) + self.pad(event_id, 4) + ";"
        self.send(output)

    def asof(self, event_id):
        output = self.get_header() + "99" + self.pad(self.nodeId, 4) + self.pad(event_id, 4) + ";"
        self.send(output)

    def pnn(self):
        flags = 0
        if self.consumer:
            flags += 1
        if self.producer:
            flags += 2
        if self.flim:
            flags += 4
        if self.bootloader:
            flags += 8
        if self.coe:
            flags += 16
        output = self.get_header() + "B6" + self.pad(self.nodeId, 4) + self.pad(self.manufId, 2) + self.pad(self.moduleId, 2) + self.pad(self.flags(), 2)+ ";"
        self.send(output)

    def parameter(self, param):
        if self.debug :
            print("parameter : " + str(self.nodeId) + " : " + str(param) + " : " + str(self.parameters[param]))
        output = self.get_header() + "9B" + self.pad(self.nodeId, 4) + self.pad(param, 2) + self.parameters[param] + ";"
        if self.debug :
            print("parameter output : " + output)
        return output

    def action_opcode(self, msg):
        def acc_on(msg):
            if self.debug :
                print("acc_on : " + msg + " Event : " + self.get_str(msg, 9, 8))
            if self.get_str(msg, 9, 8) in self.events:
                if self.debug :
                    print("Event is Known")
                self.execute({'task': 'on', 'variables': self.events[self.get_str(msg, 9, 8)]})
            else:
                if self.debug :
                    print("Event is Unknown")

        def acc_off(msg):
            if self.debug :
                print("acc_off : " + msg)
            if self.get_str(msg, 9, 8) in self.events:
                if self.debug :
                    print("Event is Known")
                self.execute({'task': 'off', 'variables': self.events[self.get_str(msg, 9, 8)]})
            else:
                if self.debug :
                    print("Event is Unknown")

        def asc_on(msg):
            event = "0000" + self.get_str(msg, 13, 4)
            if self.debug :
                print("asc_on : " + msg + " Event : " + event)
            if event in self.events:
                if self.debug :
                    print("Short Event is Known : 0000"+self.get_str(msg, 13, 8))
                self.execute({'task': 'on', 'variables': self.events[event]})
            else:
                if self.debug :
                    print("Event is Unknown")

        def asc_off(msg):
            event = "0000"+self.get_str(msg, 13, 4)
            if self.debug :
                print("asc_off : " + msg + " Event : " + event)
            if event in self.events:
                if self.debug :
                    print("Short Event is Known : 0000" + self.get_str(msg, 13, 8))
                self.execute({'task': 'off', 'variables': self.events[event]})
            else:
                if self.debug :
                    print("Event is Unknown")

        def paran(msg):
            parameter_id = self.get_int(msg, 13, 2)
            parameter_value = self.parameters[parameter_id]
            if self.debug :
                print("paran : " + msg + " nodeId : " + str(self.get_node_id(msg)))
            if self.get_node_id(msg) == self.nodeId:
                if self.debug :
                    print("paran for " + str(self.nodeId) +
                      " Parameter " + str(parameter_id) +
                      " Value : "+str(parameter_value))
                if self.debug :
                    print("Paran Output " + str(self.parameter(parameter_id)))
                # time.sleep(1)
                # self.parameter(parameter_id)
                self.send(str(self.parameter(parameter_id)))

        def qnn(msg):
            if self.debug :
                print("qnn : " + msg)
            self.pnn()

        opcode = self.get_op_code(msg)
        action = {
            "90": acc_on,
            "91": acc_off,
            "98": asc_on,
            "99": asc_off,
            "73": paran,
            "0D": qnn
        }
        self.count += 1
        if self.debug :
            print("Msg Count" + str(self.count))
        if opcode in action:
            if self.debug :
                print("Processing Opcode : " + opcode)
            action[opcode](msg)
        else:
            if self.debug :
                print("Unknown Opcode : " + opcode)


class EthNode(BasicNode):
    def __init__(self, node_id, my_function, host, port):
        BasicNode.__init__(self, node_id, my_function)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
        self.host = host  # Get local machine name
        self.port = port  # Reserve a port for your service.
        self.s.connect((host, port))

    def run(self):
        try:
            while True:
                # print('receiving data...')
                data = self.s.recv(1024)
                output = data.decode()
                messages = output.split(';')
                del messages[-1]
                for msg in messages:
                    # self.action_opcode(data.decode())
                    self.action_opcode(msg + ";")
                # print(data.decode()+ " : " +mergCbus.getOpCode(data.decode()))
                # self.execute(data.decode())
                if not data:
                    break
        except KeyboardInterrupt:
            print('interrupted!')
            self.close()
        print('connection closed')

    def send(self, msg):
        # time.sleep(1)
        print("Child Send : " + msg)
        self.s.send(msg.encode())

class canNode(BasicNode):
    def __init__(self, node_id, my_function):
        BasicNode.__init__(self, node_id, my_function)
        self.can_frame_fmt = "=IB3x8s"
        self.can_frame_size = struct.calcsize(self.can_frame_fmt)
        self.s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        self.s.bind(('can0',))

    def dissect_can_frame(self, frame):
        can_id, can_dlc, data = struct.unpack(self.can_frame_fmt, frame)
        return (can_id, can_dlc, data[:can_dlc])

    def cbus_to_can(self, cbus_f):
        #    print('-cbus_to_can')
        #    print('--cbus_f:',cbus_f,cbus_f[2:6],cbus_f[7:])
        can_id = int(int(cbus_f[2:6], 16) / 32)
        data = bytes.fromhex(cbus_f[7:-1])
        can_dlc = len(data)
        data = data.ljust(8, b'\x00')
        return struct.pack(self.can_frame_fmt, can_id, can_dlc, data)
        #return (build_can_frame(can_id, data))

    def can_to_cbus(self, can_f):
        can_id, can_dlc, data = self.dissect_can_frame(can_f)
        t = ':S'
        t += ('0000' + format(can_id * 32, 'X'))[-4:]
        t += 'N'
        for d in data:
            t += ('00' + format(d, 'X'))[-2:]
        t += ';'
        return (t)

    def send(self, can_frame):
        try:
            can_f = self.cbus_to_can(can_frame)
            self.s.send(can_f)
            print('Sending CAN frame')
        except OSError:
            print('Error sending CAN frame')

    def run(self):
        try:
            while True:
                #print('-----------------------')
                cf, addr = self.s.recvfrom(self.can_frame_size)
        #    print('     ', cf)
        #    print('Received: can_id=%x, can_dlc=%x, data=%s' % dissect_can_frame(cf))
                cbus_frame = self.can_to_cbus(cf)
                #can_f = cbus_to_can(cbus_frame)
                #print("cbus_frame ", cbus_frame)
                self.action_opcode(cbus_frame + ";")
        except KeyboardInterrupt:
            print('interrupted!')
            self.close()
        print('connection closed')