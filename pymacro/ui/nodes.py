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

        # Track connections
        self.incoming = []  # list of source NodeWidgets
        self.outgoing = []  # list of target NodeWidgets

        self.bg = "lightblue" if node_type == "Observer" else "lightgreen"
        self.rect_id = canvas.create_rectangle(x, y, x + self.WIDTH, y + self.HEIGHT, fill=self.bg)
        self.text_id = canvas.create_text(x + self.WIDTH // 2, y + self.HEIGHT // 2, text=f"{node_type}: {label}")

        self._drag_data = {"x": 0, "y": 0}
        self._edge_line = None

        # Bindings
        for item in [self.rect_id, self.text_id]:
            canvas.tag_bind(item, "<ButtonPress-1>", self.on_left_click)
            canvas.tag_bind(item, "<B1-Motion>", self.on_drag)
            canvas.tag_bind(item, "<ButtonRelease-1>", self.on_drop)
            canvas.tag_bind(item, "<ButtonPress-3>", self.on_right_press)
            canvas.tag_bind(item, "<B3-Motion>", self.on_right_drag)
            canvas.tag_bind(item, "<ButtonRelease-3>", self.on_right_release)

    def on_left_click(self, event):
        # Select this node and show its properties
        self.on_select_callback(self)
        # Prepare for dragging
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

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

    def on_right_press(self, event):
        # Start drawing a temporary dashed edge
        self._edge_line = self.canvas.create_line(
            *self.get_boundary_point_towards(event.x, event.y),
            event.x, event.y,
            arrow=tk.LAST, dash=(4, 2), fill="gray"
        )

    def on_right_drag(self, event):
        if self._edge_line:
            sx, sy = self.get_boundary_point_towards(event.x, event.y)
            self.canvas.coords(self._edge_line, sx, sy, event.x, event.y)

    def on_right_release(self, event):
        if not self._edge_line:
            return
        # Find target node under cursor
        target = None
        for node in self.canvas.nodes:
            if node == self:
                continue
            x1, y1, x2, y2 = self.canvas.coords(node.rect_id)
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                target = node
                break
        if target:
            self.canvas.add_edge(self, target)
        # Clean up temp line
        self.canvas.delete(self._edge_line)
        self._edge_line = None

    def get_center(self):
        x1, y1, x2, y2 = self.canvas.coords(self.rect_id)
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def get_boundary_point_towards(self, tx, ty):
        # Compute boundary point on rectangle edge towards (tx, ty)
        x1, y1, x2, y2 = self.canvas.coords(self.rect_id)
        cx, cy = self.get_center()
        dx = tx - cx
        dy = ty - cy
        if abs(dx) >= abs(dy):
            # closer to horizontal edge
            if dx > 0:
                return (x2, cy)
            else:
                return (x1, cy)
        else:
            # closer to vertical edge
            if dy > 0:
                return (cx, y2)
            else:
                return (cx, y1)

    def update_label(self):
        self.canvas.itemconfig(self.text_id, text=f"{self.type}: {self.label}")


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
