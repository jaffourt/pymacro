import tkinter as tk
from tkinter import ttk, messagebox

class PropertyPanel(tk.LabelFrame):
    def __init__(self, master, canvas=None):
        super().__init__(master, text="Properties", padx=10, pady=10)
        self.node = None
        # Accept canvas explicitly or get from master if not provided
        self.canvas = canvas if canvas is not None else getattr(master, 'canvas', None)

    def clear_panel(self):
        for widget in self.winfo_children():
            widget.destroy()

    def set_node(self, node):
        self.node = node
        self.clear_panel()

        ttk.Label(self, text=f"{node.type} Node: {node.label}", font=(None, 10, 'bold')).pack(anchor=tk.W)

        ttk.Label(self, text="Label:").pack(anchor=tk.W, pady=(5, 0))
        self.label_var = tk.StringVar(value=node.label)
        ttk.Entry(self, textvariable=self.label_var).pack(fill=tk.X)
        ttk.Button(self, text="Apply Label", command=self.apply_label).pack(pady=(2, 10))

        # ------ INCOMING SECTION ------
        ttk.Label(self, text="Incoming:").pack(anchor=tk.W)
        if node.incoming:
            for src_node in node.incoming:
                frame = ttk.Frame(self)
                frame.pack(fill=tk.X, pady=1)

                # Show the source‐node label
                ttk.Label(frame, text=f"• {src_node.label}").pack(side=tk.LEFT, anchor=tk.W)
                # Button to remove the edge (src_node → this node)
                ttk.Button(frame,
                           text="delete",
                           width=5,
                           command=lambda s=src_node: self.remove_edge_pair(s, node)
                          ).pack(side=tk.RIGHT)
        else:
            ttk.Label(self, text="• None").pack(anchor=tk.W)

        # ------ OUTGOING SECTION ------
        ttk.Label(self, text="Outgoing:").pack(anchor=tk.W, pady=(5,0))
        if node.outgoing:
            for dst_node in node.outgoing:
                frame = ttk.Frame(self)
                frame.pack(fill=tk.X, pady=1)

                ttk.Label(frame, text=f"• {dst_node.label}").pack(side=tk.LEFT, anchor=tk.W)
                ttk.Button(frame,
                           text="delete",
                           width=5,
                           command=lambda d=dst_node: self.remove_edge_pair(node, d)
                          ).pack(side=tk.RIGHT)
        else:
            ttk.Label(self, text="• None").pack(anchor=tk.W)

        if node.type == "Action":
            self.build_action_properties(node)
        else:
            self.build_observer_properties(node)

        # ------ DELETE NODE BUTTON ------
        ttk.Separator(self, orient="horizontal").pack(fill=tk.X, pady=10)
        ttk.Button(self, text="Delete Node", command=self.delete_node).pack(pady=(0, 10))

    def apply_label(self):
        if self.node:
            self.node.label = self.label_var.get()
            self.node.update_label()
            self.set_node(self.node)

    def build_action_properties(self, node):
        self.loop_var = tk.BooleanVar(value=node.loop)
        ttk.Checkbutton(self, text="Loop", variable=self.loop_var, command=lambda: self.toggle_loop(node)).pack(anchor=tk.W, pady=(5,0))

        ttk.Label(self, text="Recorded Actions:").pack(anchor=tk.W)
        self.actions_listbox = tk.Listbox(self, height=5)
        self.actions_listbox.pack(fill=tk.BOTH, expand=True)
        for idx, action in enumerate(node.actions):
            self.actions_listbox.insert(tk.END, f"{idx+1}: {action}")

        ttk.Button(self, text="Record", command=lambda: self.record_actions(node)).pack(pady=(5, 0))

    def toggle_loop(self, node):
        node.loop = self.loop_var.get()
        node.refresh_appearance()

    def record_actions(self, node):
        messagebox.showinfo("Record", "Recording started... Press OK to stop.")
        node.actions = ["MoveTo (100,100)", "Click", "MoveTo (200,200)", "Click"]
        self.set_node(node)

    def build_observer_properties(self, node):
        self.interrupt_var = tk.BooleanVar(value=node.interrupt)
        ttk.Checkbutton(self, text="Interrupt", variable=self.interrupt_var, command=lambda: self.toggle_interrupt(node)).pack(anchor=tk.W, pady=(5,0))

        ttk.Label(self, text="On Trigger:").pack(anchor=tk.W, pady=(5,0))
        action_labels = [n.label for n in self.canvas.nodes if n.type == "Action"]
        options = action_labels if action_labels else [""]
        self.selected_action = tk.StringVar(value=node.outgoing[0].label if node.outgoing else options[0])
        self.action_menu = ttk.OptionMenu(self, self.selected_action, self.selected_action.get(), *options)
        self.action_menu.pack(fill=tk.X)
        ttk.Button(self, text="Apply", command=lambda: self.apply_trigger(node)).pack(pady=(5, 0))

    def toggle_interrupt(self, node):
        node.interrupt = self.interrupt_var.get()
        node.refresh_appearance()

    def apply_trigger(self, node):
        # Remove existing outgoing
        for dst in list(node.outgoing):
            # Find and remove edge
            for edge in list(self.canvas.edges):
                if edge.source == node and edge.target == dst:
                    self.canvas.remove_edge(edge)
        node.outgoing.clear()
        node.incoming.clear()
        # Find selected action node
        target_label = self.selected_action.get()
        for n in self.canvas.nodes:
            if n.label == target_label and n.type == "Action":
                self.canvas.add_edge(node, n)
                break
        self.set_node(node)

    def remove_edge(self, edge):
        self.canvas.remove_edge(edge)
        self.set_node(self.node)  # Refresh panel after change

    def delete_node(self):
        if self.node:
            self.node.delete()
            self.node = None
            self.clear_panel()

    def remove_edge_pair(self, source_node, target_node):
        """
        Find the EdgeWidget in canvas.edges such that
         edge.source == source_node and edge.target == target_node,
        then remove it.
        """
        for edge in list(self.canvas.edges):
            if edge.source == source_node and edge.target == target_node:
                self.canvas.remove_edge(edge)
                break
        if self.node:
            self.set_node(self.node)

    def delete_node(self):
        """
        Remove this.node entirely (including all its edges),
        then clear out the property panel.
        """
        if self.node:
            self.node.delete()
            self.node = None
            self.clear_panel()