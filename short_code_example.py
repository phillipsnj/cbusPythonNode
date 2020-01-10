import cbus_node
import json

host = "192.168.8.200"  # Address of the cbus network interface
port = 5550             # Reserve a port for your service.

def main_func(msg):
    print("MESSAGE : "+json.dumps(msg, indent=4))
    if msg['task'] == "on":
        node.ason(msg['variables'])
    else:
        node.asof(msg['variables'])


node = cbus_node.EthNode(400, main_func, host, port)  # Create cbus module

node.teach_long_event(257, 4, 1)  # Teach a long event (nodeId, eventId, parameters)
node.teach_long_event(257, 32, 5)  # Teach a long event (nodeId, eventId, parameters)
node.teach_short_event(20, 2)  # Teach a short event (eventId, parameters)

node.run()


