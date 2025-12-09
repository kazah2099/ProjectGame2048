from anim.animation import AnimationType
import pygame
from typing import Tuple

class Renderer:
    def __init__(self, config_manager, board_manager):
        self.config = config_manager
        self.board = board_manager
        self.screen = None
        self.clock = None
        self.fonts = {}
        self.init_pygame()
    
    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.config.window_size)
        pygame.display.set_caption("2048")
        self.clock = pygame.time.Clock()
        try:
            self.fonts = {
                'small': pygame.font.Font(None, self.config.font_sizes['small']),
                'medium': pygame.font.Font(None, self.config.font_sizes['medium']),
                'large': pygame.font.Font(None, self.config.font_sizes['large'])
            }
        except:
            self.fonts = {
                'small': pygame.font.SysFont('Arial', self.config.font_sizes['small']),
                'medium': pygame.font.SysFont('Arial', self.config.font_sizes['medium']),
                'large': pygame.font.SysFont('Arial', self.config.font_sizes['large'])
            }
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def get_color(self, value: int) -> Tuple[int, int, int]:
        return self.hex_to_rgb(self.config.colors.get(str(value), self.config.colors["0"]))
    
    def get_font_color(self, value: int) -> Tuple[int, int, int]:
        color_name = 'light' if value > 4 else 'dark'
        return self.hex_to_rgb(self.config.font_colors[color_name])
    
    def draw_tile(self, value: int, x: int, y: int, scale: float = 1.0):
        color = self.get_color(value)
        font_color = self.get_font_color(value)
        width = int(self.config.tile_size * scale)
        height = int(self.config.tile_size * scale)
        offset_x = (self.config.tile_size - width) // 2
        offset_y = (self.config.tile_size - height) // 2
        
        pygame.draw.rect(self.screen, color, 
                        (x + offset_x, y + offset_y, width, height), 
                        border_radius=max(5, int(10 * scale)))
        
        if value != 0 and scale > 0.5:
            if value < 100:
                font = self.fonts['large']
            elif value < 1000:
                font = self.fonts['medium']
            else:
                font = self.fonts['small']
            
            text = font.render(str(value), True, font_color)
            text_rect = text.get_rect(center=(x + self.config.tile_size // 2, y + self.config.tile_size // 2))
            self.screen.blit(text, text_rect)
    
    def draw_animated_tiles(self):
        for anim in self.board.animations:
            if anim.anim_type == AnimationType.MERGE:
                scale = 1.0 + 0.2 * (1 - abs(anim.progress / anim.duration - 0.5) * 2)
                self.draw_tile(anim.value, anim.current_pos[0], anim.current_pos[1], scale)
            else:
                self.draw_tile(anim.value, anim.current_pos[0], anim.current_pos[1])
        for anim in self.board.new_tile_animations:
            if anim.anim_type == AnimationType.APPEAR:
                scale = anim.progress / anim.duration
                self.draw_tile(anim.value, anim.current_pos[0], anim.current_pos[1], scale)
    
    def draw_board(self):
        self.screen.fill(self.hex_to_rgb('#FAF8EF'))
        
        score_text = self.fonts['medium'].render(f'Score: {self.board.score}', True, self.hex_to_rgb('#776E65'))
        self.screen.blit(score_text, (20, 20))

        board_start_x, board_start_y = self.board.get_board_position()
        board_width = self.config.board_size * (self.config.tile_size + self.config.padding) + self.config.padding
        
        pygame.draw.rect(self.screen, self.hex_to_rgb('#BBADA0'), 
                        (board_start_x - self.config.padding, board_start_y - self.config.padding,
                         board_width, board_width), border_radius=10)

        for i in range(self.config.board_size):
            for j in range(self.config.board_size):
                is_animating = any(
                    anim.end_pos == self.board.get_tile_position(i, j) and 
                    anim.anim_type != AnimationType.MOVE
                    for anim in self.board.animations + self.board.new_tile_animations
                )
                
                if not is_animating and self.board.board[i][j] != 0:
                    x, y = self.board.get_tile_position(i, j)
                    self.draw_tile(self.board.board[i][j], x, y)

        self.draw_animated_tiles()
        if self.board.won:
            self.draw_message("You Win!", '#00F93A')
        elif self.board.game_over:
            self.draw_message("Game Over!", '#FF0000')
    
    def draw_message(self, text: str, color_hex: str):
        overlay = pygame.Surface(self.config.window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        font = self.fonts['large']
        color = self.hex_to_rgb(color_hex)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.config.window_size[0] // 2, self.config.window_size[1] // 2))
        self.screen.blit(text_surface, text_rect)
        
        restart_font = self.fonts['medium']
        restart_text = restart_font.render('Press R to Restart', True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(self.config.window_size[0] // 2, self.config.window_size[1] // 2 + 60))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.board.reset_game()
                    elif not self.board.game_over and not self.board.won and not self.board.animations:
                        if event.key == pygame.K_LEFT:
                            self.board.move('left')
                        elif event.key == pygame.K_RIGHT:
                            self.board.move('right')
                        elif event.key == pygame.K_UP:
                            self.board.move('up')
                        elif event.key == pygame.K_DOWN:
                            self.board.move('down')
            
            self.board.update_animations()
            self.draw_board()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
