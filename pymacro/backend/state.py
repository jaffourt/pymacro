import time
from dataclasses import dataclass
from typing import List, Optional

from macros.backend.observer import Observer
from macros.backend.action import Action


@dataclass
class GraphNode:
    observer: Observer
    actions: List[Action]
    next_node: Optional['GraphNode'] = None



class StateMachine:
    def __init__(self, start_node: GraphNode):
        self.current = start_node
        self.running = False

    def run(self):
        self.running = True
        while self.running and self.current:
            if self.current.observer.is_triggered():
                for action in self.current.actions:
                    action.execute()
                self.current = self.current.next_node
            else:
                time.sleep(0.1)

    def stop(self):
        self.running = False


