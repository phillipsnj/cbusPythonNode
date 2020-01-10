import tkinter as tk
from tkinter import ttk
import cbus_node
import json

host = "192.168.8.200"  # Get local machine name
port = 5550  # Reserve a port for your service.


class MERGGUI(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("MERG Gui Test")
        self.geometry("800x480")
        self.resizable(width=False, height=False)
        self.mergnode = cbus_node.EthNode(260, self.main_func, host, port)
        self.mergnode.start()
        self.mergnode.teach_long_event(257, 4, ["red", "green"])
        self.mergnode.teach_long_event(257, 32, ["green", "red"])
        self.nodeFrame = tk.LabelFrame(self, text=" Simple CBus Node: ")
        self.nodeFrame.grid(row=0, columnspan=7, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
        self.label = ttk.Label(self.nodeFrame, text="Simple GUI Example")
        self.button = ttk.Button(self.nodeFrame, text="On", command=lambda: self.button_press(1,0))
        self.button2 = ttk.Button(self.nodeFrame, text="Off", command=lambda: self.button_press(1,1))
        self.label.grid(row=1, column=1, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
        self.button.grid(row=2, column=1, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
        self.button2.grid(row=3, column=1, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)

    def main_func(self, msg):
        print("ACTION :: " + json.dumps(msg, indent=4))
        self.label.config(background=msg['variables'][0])

    def button_press(self, button_id, type):
        print("Button : " + str(button_id) + " "+str(type))
        if type == 0:
            self.mergnode.acon(button_id)
        else:
            self.mergnode.acof(button_id)


if __name__ == '__main__':
    app = MERGGUI()
    app.mainloop()
