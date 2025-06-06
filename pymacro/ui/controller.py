class EventController:
    def __init__(self, canvas):
        self.state = "idle"
        self.canvas = canvas
        self.connect_source = None
