import tkinter as tk
from ui.nodes import NodeWidget, EdgeWidget

class GraphCanvas(tk.Canvas):
    def __init__(self, master, on_select, **kwargs):
        super().__init__(master, bg="white", **kwargs)
        self.nodes = []
        self.edges = []
        self.on_select = on_select

    def add_node(self, x, y, label, node_type):
        node = NodeWidget(self, x, y, label, node_type, self.on_select)
        self.nodes.append(node)

    def add_edge(self, source_node, target_node):
        edge = EdgeWidget(self, source_node, target_node)
        self.edges.append(edge)

    def update_edges(self, moved_node):
        for edge in self.edges:
            if edge.source == moved_node or edge.target == moved_node:
                edge.update_position()

    def remove_edge(self, edge):
        """
        Remove the given EdgeWidget from the canvas and deregister it from
        source/target node's incoming/outgoing lists.
        """
        # 1) Erase the line itself:
        self.delete(edge.line_id)

        # 2) Remove the connection record from NodeWidget.incoming/outgoing:
        if edge.source in self.nodes and edge.target in self.nodes:
            if edge.target in edge.source.outgoing:
                edge.source.outgoing.remove(edge.target)
            if edge.source in edge.target.incoming:
                edge.target.incoming.remove(edge.source)

        # 3) Remove the EdgeWidget object from our list:
        if edge in self.edges:
            self.edges.remove(edge)