import tkinter as tk
from tkinter import ttk, messagebox



class PropertyPanel(tk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="Properties", padx=10, pady=10)
        self.node = None

    def clear_panel(self):
        for widget in self.winfo_children():
            widget.destroy()

    def set_node(self, node):
        self.node = node
        self.clear_panel()
        ttk.Label(self, text=f"{node.type} Node: {node.label}", font=(None, 10, 'bold')).pack(anchor=tk.W)

        # Common: label editing
        ttk.Label(self, text="Label:").pack(anchor=tk.W, pady=(5, 0))
        self.label_var = tk.StringVar(value=node.label)
        ttk.Entry(self, textvariable=self.label_var).pack(fill=tk.X)
        ttk.Button(self, text="Apply Label", command=self.apply_label).pack(pady=(2, 10))

        if node.type == "Action":
            self.build_action_properties(node)
        else:
            self.build_observer_properties(node)

    def apply_label(self):
        if self.node:
            self.node.label = self.label_var.get()
            self.node.update_label()

    def build_action_properties(self, node):
        # List of recorded actions
        ttk.Label(self, text="Recorded Actions:").pack(anchor=tk.W)
        self.actions_listbox = tk.Listbox(self, height=5)
        self.actions_listbox.pack(fill=tk.BOTH, expand=True)
        for idx, action in enumerate(node.actions):
            self.actions_listbox.insert(tk.END, f"{idx+1}: {action}")

        ttk.Button(self, text="Record", command=lambda: self.record_actions(node)).pack(pady=(5, 0))

    def record_actions(self, node):
        messagebox.showinfo("Record", "Recording started... Press OK to stop.")
        # Stub: In a real implementation, start a separate thread to capture events
        # Here, we simulate a recorded action list
        node.actions = ["MoveTo (100,100)", "Click", "MoveTo (200,200)", "Click"]
        self.set_node(node)

    def build_observer_properties(self, node):
        # Display current bounding box
        ttk.Label(self, text="Bounding Box:").pack(anchor=tk.W)
        bbox_text = f"{node.bbox}" if node.bbox else "None"
        self.bbox_label = ttk.Label(self, text=bbox_text)
        self.bbox_label.pack(anchor=tk.W)

        ttk.Button(self, text="Select Bounding Box", command=lambda: self.select_bbox(node)).pack(pady=(5, 2))
        ttk.Button(self, text="Visualize Bounding Box", command=lambda: self.visualize_bbox(node)).pack()

    def select_bbox(self, node):
        messagebox.showinfo("Select BBox", "Click and drag on screen to select bounding box.")
        # Stub: In a real implementation, hide this window and overlay a fullscreen capture for user to drag
        # Here, we simulate
        node.bbox = (100, 100, 300, 300)
        self.set_node(node)

    def visualize_bbox(self, node):
        if not node.bbox:
            messagebox.showwarning("No BBox", "No bounding box set.")
            return
        x1, y1, x2, y2 = node.bbox
        overlay = tk.Toplevel(self)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-alpha', 0.3)
        overlay.attributes('-topmost', True)
        c = tk.Canvas(overlay, bg='red', highlightthickness=0)
        c.pack(fill=tk.BOTH, expand=True)
        c.create_rectangle(x1, y1, x2, y2, outline='blue', width=3)
        ttk.Button(overlay, text="Close", command=overlay.destroy).place(x=10, y=10)
