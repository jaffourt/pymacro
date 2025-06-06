import pyautogui
from dataclasses import dataclass

class Action:
    def execute(self):
        raise NotImplementedError("Subclasses must implement execute()")

@dataclass
class MouseClick(Action):
    x: int
    y: int
    button: str = "left"

    def execute(self):
        # Use pyobjc or pyautogui (mac-compatible)
        pyautogui.click(x=self.x, y=self.y, button=self.button)

