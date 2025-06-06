import tkinter as tk

from ui.toolbar import ToolbarPanel
from ui.canvas import GraphCanvas
from ui.properties import PropertyPanel


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Macro Graph Builder")
        self.geometry("900x600")

        self.toolbar = ToolbarPanel(self, None)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = GraphCanvas(main_frame, self.on_node_selected, width=700, height=500)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Update toolbar's canvas reference now that canvas is created
        self.toolbar.canvas = self.canvas

        self.properties = PropertyPanel(main_frame, self.canvas)
        self.properties.pack(side=tk.RIGHT, fill=tk.Y)

    def on_node_selected(self, node):
        self.properties.set_node(node)