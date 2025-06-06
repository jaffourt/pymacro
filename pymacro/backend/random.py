import random

# GLOBALS
# ----------------
JITTER_RADIUS = 3
DELAY_VARIATION = 0.05

def jitter(pos, radius=JITTER_RADIUS):
    if not pos:
        return None
    x, y = pos
    return (
        x + random.randint(-radius, radius),
        y + random.randint(-radius, radius)
    )


def random_delay(base):
    delta = base * DELAY_VARIATION
    return random.uniform(base - delta, base + delta)

