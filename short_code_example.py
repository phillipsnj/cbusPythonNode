import cbus_node
import json

host = "localhost"  # Address of the cbus network interface
port = 5550             # Reserve a port for your service.
nodeId = 400            # Node Id

def main_func(msg):
    print("MESSAGE : "+json.dumps(msg, indent=4))
    if msg['task'] == "on":
        node.ason(msg['variables']) # Broadcast a Short Event
    else:
        node.asof(msg['variables']) # Broadcast a Long Event


node = cbus_node.EthNode(nodeId, main_func, host, port)  # Create cbus module

node.teach_long_event(802, 8, 1)  # Teach a long event (nodeId, eventId, parameters)
node.teach_long_event(802, 1, 5)  # Teach a long event (nodeId, eventId, parameters)
node.teach_short_event(20, 2)  # Teach a short event (eventId, parameters)

node.run()


