import tkinter as tk

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
        else:  # Observer
            self.bbox = None   # (x1, y1, x2, y2)

        self.bg = "lightblue" if node_type == "Observer" else "lightgreen"
        self.rect_id = canvas.create_rectangle(x, y, x + self.WIDTH, y + self.HEIGHT, fill=self.bg)
        self.text_id = canvas.create_text(x + self.WIDTH // 2, y + self.HEIGHT // 2, text=f"{node_type}: {label}")

        self._drag_data = {"x": 0, "y": 0}
        self._edge_line = None
        self._edge_source = None

        # Bindings
        for item in [self.rect_id, self.text_id]:
            canvas.tag_bind(item, "<ButtonPress-1>", self.on_left_click)
            canvas.tag_bind(item, "<ButtonPress-3>", self.on_right_press)
            canvas.tag_bind(item, "<B3-Motion>", self.on_right_drag)
            canvas.tag_bind(item, "<ButtonRelease-3>", self.on_right_release)
            canvas.tag_bind(item, "<B1-Motion>", self.on_drag)
            canvas.tag_bind(item, "<ButtonRelease-1>", self.on_drop)

    def on_left_click(self, event):
        # Select this node and show its properties
        self.on_select_callback(self)
        # Prepare for dragging
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_right_press(self, event):
        # Start edge drawing
        self._edge_source = self
        sx, sy = self.get_center()
        self._edge_line = self.canvas.create_line(sx, sy, event.x, event.y, arrow=tk.LAST, dash=(4, 2))

    def on_right_drag(self, event):
        if self._edge_line:
            sx, sy = self.get_center()
            self.canvas.coords(self._edge_line, sx, sy, event.x, event.y)

    def on_right_release(self, event):
        if not self._edge_line:
            return
        # Determine target node under cursor
        target = None
        for node in self.canvas.nodes:
            if node == self:
                continue
            x1, y1, x2, y2 = self.canvas.coords(node.rect_id)
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                target = node
                break
        # If valid target, add edge
        if target:
            self.canvas.add_edge(self, target)
        # Remove temporary line
        self.canvas.delete(self._edge_line)
        self._edge_line = None
        self._edge_source = None

    def on_drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self.canvas.move(self.rect_id, dx, dy)
        self.canvas.move(self.text_id, dx, dy)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self.canvas.update_edges(self)

    def on_drop(self, event):
        pass

    def update_label(self):
        self.canvas.itemconfig(self.text_id, text=f"{self.type}: {self.label}")

    def get_center(self):
        x1, y1, x2, y2 = self.canvas.coords(self.rect_id)
        return ((x1 + x2) / 2, (y1 + y2) / 2)

class EdgeWidget:
    def __init__(self, canvas, source_node, target_node):
        self.canvas = canvas
        self.source = source_node
        self.target = target_node
        sx, sy = self.source.get_center()
        tx, ty = self.target.get_center()
        self.line_id = canvas.create_line(sx, sy, tx, ty, arrow=tk.LAST, width=2)

    def update_position(self):
        sx, sy = self.source.get_center()
        tx, ty = self.target.get_center()
        self.canvas.coords(self.line_id, sx, sy, tx, ty)
