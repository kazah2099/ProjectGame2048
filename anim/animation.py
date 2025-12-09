from typing import Tuple
from enum import Enum

class AnimationType(Enum):
    MOVE = 1
    MERGE = 2
    APPEAR = 3

class TileAnimation:
    def __init__(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                 value: int, anim_type: AnimationType, duration: int = 10):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.value = value
        self.anim_type = anim_type
        self.duration = duration
        self.progress = 0
        self.current_pos = start_pos
        
    def update(self) -> bool:
        self.progress += 1
        if self.progress >= self.duration:
            self.current_pos = self.end_pos
            return True
        t = self.progress / self.duration
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t
        self.current_pos = (int(x), int(y))
        return False