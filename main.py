from config.config_manager import GameConfigManager
from render.board_manager import BoardManager
from render.renderer import Renderer

class Game2048:
    def __init__(self, config_path: str = "config.json"):
        self.config_manager = GameConfigManager()
        self.config_manager.load_config(config_path)
        self.board_manager = BoardManager(self.config_manager)
        self.renderer = Renderer(self.config_manager, self.board_manager)
    
    def run(self):
        self.renderer.run()

if __name__ == "__main__":
    game = Game2048('config/config.json')
    game.run()
