# cbusPythonNode
Python class to create a cbus module.

The class requires a network connection such as the canEther or the cbusServer.

The following code is a simple example that will print to the console parameters for any taught cbus message:

```javascript
import cbus_node
import json

host = "192.168.0.102"  # Address of the cbus network interface
port = 5550             # Reserve a port for your service.
node_id = 25            # Cbus Node ID


def main_func(msg): # Fuction executed when a recognised message is received.
    print("MESSAGE : "+json.dumps(msg, indent=4))


node = cbus_node.EthNode(node_id, main_func, host, port)  # Create the cbus module

node.add_long_event(400, 1, 1)  # Teach a long event (nodeId, eventId, parameters)
node.add_short_event(20, 2)     # Teach a short event (eventId, parameters)

node.run() 
```
