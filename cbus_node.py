import json
import socket
import threading


class BasicNode(threading.Thread):
    def __init__(self, node_id, my_function):
        threading.Thread.__init__(self)
        self.function = my_function
        self.nodeId = node_id
        self.canId = 75
        self.priority1 = 2
        self.priority2 = 3
        self.manufId = 165
        self.moduleId = 255
        self.name = "PYTHON"
        self.minorVersion = "A"
        self.numEvents = 255
        self.numEventVariables = 3
        self.numNodeVariables = 2
        self.majorVersion = 2
        self.beta = 1  # 0  for normal version else beta version number
        self.consumer = True
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

    def add_long_event(self, node_id, event_id, variables):
        new_id = self.pad(node_id, 4) + self.pad(event_id, 4)
        self.events[new_id] = variables
        print(json.dumps(self.events, indent=4))

    def add_short_event(self, event_id, variables):
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
        output = self.get_header() + "B6" + self.pad(self.node_id, 4) + self.pad(self.manuf_id, 2) + self.pad(self.module_id, 2) + self.pad(self.flags(), 2)
        self.send(output)

    def parameter(self, param):
        print("parameter : " + str(self.nodeId) + " : " + str(param) + " : " + str(self.parameters[param]))
        output = self.get_header() + "9B" + self.pad(self.nodeId, 4) + self.pad(param, 2) + self.parameters[param] + ";"
        print("parameter output : " + output)
        return output

    def action_opcode(self, msg):
        def acc_on(msg):
            print("acc_on : " + msg + " Event : " + self.get_str(msg, 9, 8))
            if self.get_str(msg, 9, 8) in self.events:
                print("Event is Known")
                self.execute({'task': 'on', 'variables': self.events[self.get_str(msg, 9, 8)]})
            else:
                print("Event is Unknown")

        def acc_off(msg):
            print("acc_off : " + msg)
            if self.get_str(msg, 9, 8) in self.events:
                print("Event is Known")
                self.execute({'task': 'off', 'variables': self.events[self.get_str(msg, 9, 8)]})
            else:
                print("Event is Unknown")

        def asc_on(msg):
            event = "0000" + self.get_str(msg, 13, 4)
            print("asc_on : " + msg + " Event : " + event)
            if event in self.events:
                print("Short Event is Known : 0000"+self.get_str(msg, 13, 8))
                self.execute({'task': 'on', 'variables': self.events[event]})
            else:
                print("Event is Unknown")

        def asc_off(msg):
            event = "0000"+self.get_str(msg, 13, 4)
            print("asc_off : " + msg + " Event : " + event)
            if event in self.events:
                print("Short Event is Known : 0000" + self.get_str(msg, 13, 8))
                self.execute({'task': 'off', 'variables': self.events[event]})
            else:
                print("Event is Unknown")

        def paran(msg):
            parameter_id = self.get_int(msg, 13, 2)
            parameter_value = self.parameters[parameter_id]
            print("paran : " + msg + " nodeId : " + str(self.get_node_id(msg)))
            if self.get_node_id(msg) == self.nodeId:
                print("paran for " + str(self.nodeId) +
                      " Parameter " + str(parameter_id) +
                      " Value : "+str(parameter_value))
                print("Paran Output " + str(self.parameter(parameter_id)))
                # time.sleep(1)
                # self.parameter(parameter_id)
                self.send(str(self.parameter(parameter_id)))

        opcode = self.get_op_code(msg)
        action = {
            "90": acc_on,
            "91": acc_off,
            "98": asc_on,
            "99": asc_off,
            "73": paran
        }
        if opcode in action:
            print("Processing Opcode : " + opcode)
            action[opcode](msg)
        else:
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
                # print(data.decode()+ " : " +mergCbus.getOpCode(data.decode()))
                self.action_opcode(data.decode())
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
