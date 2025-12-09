import json
from typing import Dict

class GameConfigManager:
    def __init__(self):
        self.config = {}
        
    def load_config(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
    @property
    def board_size(self) -> int:
        return self.config.get('board_size', 4)
    
    @property
    def target_score(self) -> int:
        return self.config.get('target_score', 2048)
    
    @property
    def initial_tiles(self) -> int:
        return self.config.get('initial_tiles', 2)
    
    @property
    def probabilities(self) -> Dict[str, float]:
        return self.config.get('probabilities', {"2": 0.9, "4": 0.1})
    
    @property
    def colors(self) -> Dict[str, str]:
        return self.config.get('colors', {})
    
    @property
    def font_colors(self) -> Dict[str, str]:
        return self.config.get('font_colors', {'light': '#F9F6F2', 'dark': '#776E65'})
    
    @property
    def window_size(self) -> list:
        return self.config.get('window_size', [600, 700])
    
    @property
    def tile_size(self) -> int:
        return self.config.get('tile_size', 120)
    
    @property
    def padding(self) -> int:
        return self.config.get('padding', 15)
    
    @property
    def font_sizes(self) -> Dict[str, int]:
        return self.config.get('font_sizes', {'small': 36, 'medium': 48, 'large': 60})
    
    @property
    def animation_speed(self) -> int:
        return self.config.get('animation_speed', 10)
    
    @property
    def animation_duration(self) -> int:
        return self.config.get('animation_duration', 15)
