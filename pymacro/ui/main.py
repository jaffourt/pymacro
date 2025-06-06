import tkinter as tk

from ui.toolbar import ToolbarPanel
from ui.canvas import GraphCanvas
from ui.properties import PropertyPanel


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Macro Graph Builder")
        self.geometry("900x600")

        # Toolbar at top
        self.toolbar = ToolbarPanel(self, None)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Main frame holds canvas and properties
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = GraphCanvas(main_frame, on_select=self.on_node_selected, width=700, height=500)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.properties = PropertyPanel(main_frame)
        self.properties.pack(side=tk.RIGHT, fill=tk.Y)

        self.toolbar.canvas = self.canvas  # now canvas exists

    def on_node_selected(self, node):
        self.properties.set_node(node)
