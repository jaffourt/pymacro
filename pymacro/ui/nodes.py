import tkinter as tk
from tkinter import messagebox

class NodeWidget:
    WIDTH = 120
    HEIGHT = 60

    def __init__(self, canvas, x, y, label, node_type, on_select_callback):
        self.canvas = canvas
        self.x, self.y = x, y
        self.label = label
        self.type = node_type
        self.on_select_callback = on_select_callback

        # Data attributes for nodes
        if self.type == "Action":
            self.actions = []  # list of recorded actions
            self.loop = False
        else:  # Observer
            self.bbox = None   # (x1, y1, x2, y2)
            self.interrupt = False

        # Track connections
        self.incoming = []  # list of source NodeWidgets
        self.outgoing = []  # list of target NodeWidgets

        # Appearance: create shape and text
        self.create_shape()
        self.text_id = self.canvas.create_text(x + self.WIDTH/2, y + self.HEIGHT/2, text=f"{node_type}: {label}")

        self._drag_data = {"x": 0, "y": 0}
        self._edge_line = None

        # Bindings
        for item in [self.shape_id, self.text_id]:
            canvas.tag_bind(item, "<ButtonPress-1>", self.on_left_click)
            canvas.tag_bind(item, "<B1-Motion>", self.on_drag)
            canvas.tag_bind(item, "<ButtonRelease-1>", self.on_drop)
            canvas.tag_bind(item, "<ButtonPress-3>", self.on_right_press)
            canvas.tag_bind(item, "<B3-Motion>", self.on_right_drag)
            canvas.tag_bind(item, "<ButtonRelease-3>", self.on_right_release)

    def create_shape(self):
        # Remove existing if any
        if hasattr(self, 'shape_id'):
            self.canvas.delete(self.shape_id)
        x1, y1 = self.x, self.y
        x2, y2 = x1 + self.WIDTH, y1 + self.HEIGHT
        # Determine shape based on flags
        if self.type == "Action" and self.loop:
            self.shape_id = self.canvas.create_oval(x1, y1, x2, y2,
                                                    fill="lightgreen", outline="green", width=2)
        elif self.type == "Observer" and self.interrupt:
            # Create a diamond centered in bounding box
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            points = [cx, y1, x2, cy, cx, y2, x1, cy]
            self.shape_id = self.canvas.create_polygon(points,
                                                       fill="lightblue", outline="blue", width=2)
        else:
            # Default rectangle
            fill_color = "lightgreen" if self.type == "Action" else "lightblue"
            outline_color = "black"
            self.shape_id = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                          fill=fill_color, outline=outline_color, width=2)
        self.update_colors()

    def update_colors(self):
        # Update outline color if not redrawn
        if not hasattr(self, 'shape_id'):
            return
        if self.type == "Observer":
            self.canvas.itemconfig(self.shape_id, outline="blue" if self.interrupt else "black")
        else:
            self.canvas.itemconfig(self.shape_id, outline="green" if self.loop else "black")

    def refresh_appearance(self):
        coords = self.canvas.coords(self.shape_id)
        self.x, self.y = coords[0], coords[1]
        self.create_shape()
        self.canvas.delete(self.text_id)
        self.text_id = self.canvas.create_text(self.x + self.WIDTH/2, self.y + self.HEIGHT/2, text=f"{self.type}: {self.label}")
        for item in [self.shape_id, self.text_id]:
            self.canvas.tag_bind(item, "<ButtonPress-1>", self.on_left_click)
            self.canvas.tag_bind(item, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(item, "<ButtonRelease-1>", self.on_drop)
            self.canvas.tag_bind(item, "<ButtonPress-3>", self.on_right_press)
            self.canvas.tag_bind(item, "<B3-Motion>", self.on_right_drag)
            self.canvas.tag_bind(item, "<ButtonRelease-3>", self.on_right_release)

    def on_left_click(self, event):
        self.on_select_callback(self)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self.canvas.move(self.shape_id, dx, dy)
        self.canvas.move(self.text_id, dx, dy)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self.canvas.update_edges(self)

    def on_drop(self, event):
        pass

    def on_right_press(self, event):
        sx, sy = self.get_boundary_point_towards(event.x, event.y)
        self._edge_line = self.canvas.create_line(sx, sy, event.x, event.y, arrow=tk.LAST, dash=(4, 2), fill="gray")

    def on_right_drag(self, event):
        if self._edge_line:
            sx, sy = self.get_boundary_point_towards(event.x, event.y)
            self.canvas.coords(self._edge_line, sx, sy, event.x, event.y)

    def on_right_release(self, event):
        if not self._edge_line:
            return
        target = None
        for node in self.canvas.nodes:
            if node == self:
                continue
            x1, y1, x2, y2 = self.canvas.bbox(node.shape_id)
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                target = node
                break
        if target:
            if self.type == "Observer" and target.type == "Action":
                if self.outgoing:
                    messagebox.showwarning("Connection", "Observer can only link to one action.")
                else:
                    self.canvas.add_edge(self, target)
            elif self.type == "Action" and target.type == "Action":
                self.canvas.add_edge(self, target)
            else:
                messagebox.showwarning("Connection", "Invalid connection type.")
        self.canvas.delete(self._edge_line)
        self._edge_line = None

    def get_center(self):
        coords = self.canvas.coords(self.shape_id)
        xs = coords[::2]
        ys = coords[1::2]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def get_boundary_point_towards(self, tx, ty):
        x1, y1, x2, y2 = self.canvas.bbox(self.shape_id)
        cx, cy = self.get_center()
        dx = tx - cx
        dy = ty - cy
        if abs(dx) >= abs(dy):
            return (x2, cy) if dx > 0 else (x1, cy)
        else:
            return (cx, y2) if dy > 0 else (cx, y1)

    def update_label(self):
        self.canvas.itemconfig(self.text_id, text=f"{self.type}: {self.label}")

    def delete(self):
        # remove all incoming edges
        for src_node in list(self.incoming):
            for edge in list(self.canvas.edges):
                if edge.source == src_node and edge.target == self:
                    self.canvas.remove_edge(edge)
                    break
        # remove all outgoing edges
        for dst_node in list(self.outgoing):
            for edge in list(self.canvas.edges):
                if edge.source == self and edge.target == dst_node:
                    self.canvas.remove_edge(edge)
                    break
        # delete our shape & text
        self.canvas.delete(self.shape_id)
        self.canvas.delete(self.text_id)
        # remove self from canvas.nodes
        if self in self.canvas.nodes:
            self.canvas.nodes.remove(self)


class EdgeWidget:
    def __init__(self, canvas, source_node, target_node):
        self.canvas = canvas
        self.source = source_node
        self.target = target_node
        # Register connections on nodes
        source_node.outgoing.append(target_node)
        target_node.incoming.append(source_node)
        # Initial draw
        self.line_id = self.draw_edge()

    def draw_edge(self):
        # Compute multi-segment orthogonal path
        sx, sy = self.source.get_boundary_point_towards(*self.target.get_center())
        tx, ty = self.target.get_boundary_point_towards(*self.source.get_center())
        mx = (sx + tx) / 2
        points = [sx, sy, mx, sy, mx, ty, tx, ty]
        return self.canvas.create_line(*points, arrow=tk.LAST, dash=(4,2), fill="gray")

    def update_position(self):
        self.canvas.delete(self.line_id)
        self.line_id = self.draw_edge()
