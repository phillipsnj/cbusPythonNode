import tkinter as tk
from tkinter import ttk
import cbus_node
import json

host = "192.168.0.102"  # Get local machine name
port = 5550  # Reserve a port for your service.


class MergView(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.mergnode = cbus_node.EthNode(260, self.main_func, host, port)
        self.mergnode.start()
        self.mergnode.add_long_event(400, 1, ["red", "green"])
        self.mergnode.add_long_event(400, 29, ["green", "red"])
        self.label = ttk.Label(self, text="Simple GUI Example")
        self.button = ttk.Button(self, text="Button", command=lambda: self.button_press(1))
        self.label.grid(row=1, column=1)
        self.button.grid(row=2, column=1)

    def main_func(self, msg):
        print("ACTION :: " + json.dumps(msg, indent=4))
        self.label.config(background=msg['variables'][0])

    def button_press(self, id):
        print("Button : " + str(id))
        self.mergnode.acon(id)


class MyApplication(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("MERG Gui Test")
        self.geometry("800x480")
        self.resizable(width=False, height=False)
        MergView(self).grid(sticky=(tk.E + tk.W + tk.N + tk.S))
        self.columnconfigure(0, weight=1)


if __name__ == '__main__':
    app = MyApplication()
    app.mainloop()
