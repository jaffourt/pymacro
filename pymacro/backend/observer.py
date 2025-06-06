
from dataclasses import dataclass
from typing import Tuple, Optional
from pynput import mouse
from PIL import ImageGrab
import numpy as np

def select_screen_region():
    """Let user click and drag to define a rectangular screen region."""
    print("[*] Drag to select region...")

    positions = []

    def on_click(x, y, button, pressed):
        if pressed:
            positions.clear()
            positions.append((x, y))
        else:
            positions.append((x, y))
            return False  # stop listener

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    (x1, y1), (x2, y2) = positions
    return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))


def grab_box_region(box):
    """Return a NumPy array of the screen region."""
    x1, y1, x2, y2 = map(int, box)
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2)).convert('RGB')
    return np.array(img)


def has_region_changed(prev, curr, threshold=10):
    """Check if the image has changed enough to be considered a trigger."""
    diff = np.abs(prev.astype(int) - curr.astype(int))
    changed_pixels = np.sum(diff > 20)
    return changed_pixels > threshold


class Observer:
    def is_triggered(self) -> bool:
        raise NotImplementedError

@dataclass
class RegionObserver(Observer):
    region: Tuple[int, int, int, int]
    threshold: int = 10
    last_state: Optional[np.ndarray] = None

    def is_triggered(self) -> bool:
        current = grab_box_region(self.region)
        if self.last_state is None:
            self.last_state = current
            return False
        changed = has_region_changed(self.last_state, current, self.threshold)
        self.last_state = current
        return changed


