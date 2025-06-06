import tkinter as tk
from tkinter import ttk, messagebox

class ToolbarPanel(tk.Frame):
    def __init__(self, master, canvas):
        super().__init__(master)
        self.canvas = canvas
        ttk.Button(self, text="Add Observer", command=self.add_observer).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(self, text="Add Action", command=self.add_action).pack(side=tk.LEFT, padx=5, pady=5)
        # Help button on top-right
        self.help_btn = ttk.Button(self, text="?", width=2, command=self.show_help)
        self.help_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def add_observer(self):
        self.canvas.add_node(50, 50, f"obs_{len(self.canvas.nodes)}", "Observer")

    def add_action(self):
        self.canvas.add_node(200, 200, f"act_{len(self.canvas.nodes)}", "Action")

    def show_help(self):
        messagebox.showinfo("Help", "Left-click on a node to edit its properties.\nRight-click and drag from one node to another to connect.")
