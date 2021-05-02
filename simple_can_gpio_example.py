import cbus_node
from gpiozero import LED, Button

node_id = 252  # ID number for the new node.

redled = LED(22)
amberled = LED(23)
greenled = LED(24)
button = Button(17)


def main_func(msg):  # Define the function to perform processing.
    if msg["task"] == "on":
        if "redled" in msg["variables"]["LED"]:
            redled.on()
        if "amberled" in msg["variables"]["LED"]:
            amberled.on()
        if "greenled" in msg["variables"]["LED"]:
            greenled.on()
    else:
        if "redled" in msg["variables"]["LED"]:
            redled.off()
        if "amberled" in msg["variables"]["LED"]:
            amberled.off()
        if "greenled" in msg["variables"]["LED"]:
            greenled.off()


node = cbus_node.CanNode(node_id, main_func)  # Create the cbus node


def button_on():
    node.ason(2)


def button_off():
    node.asof(2)


button.when_pressed = button_on
button.when_released = button_off

node.teach_long_event(257, 4, {"id": 1, "LED": ["redled"]})  # Teach a long event (nodeId, eventId, parameters)
node.teach_long_event(257, 32, {"id": 1, "LED": ["greenled", "amberled"]})

# node.run()
node.start()
node.join()
