import random
from typing import List, Tuple
from enum import Enum

class AnimationType(Enum):
    MOVE = 1
    MERGE = 2
    APPEAR = 3

class TileAnimation:
    def __init__(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                 value: int, anim_type: AnimationType, duration: int):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = list(start_pos)
        self.value = value
        self.anim_type = anim_type
        self.duration = duration
        self.progress = 0
    
    def update(self) -> bool:
        self.progress += 1
        if self.progress >= self.duration:
            self.current_pos = list(self.end_pos)
            return True
        
        t = self.progress / self.duration
        if self.anim_type == AnimationType.MOVE:
            self.current_pos[0] = int(self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t)
            self.current_pos[1] = int(self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t)
        elif self.anim_type == AnimationType.MERGE:
            self.current_pos[0] = int(self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t)
            self.current_pos[1] = int(self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t)
        
        return False

class BoardManager:
    def __init__(self, config_manager):
        self.config = config_manager
        self.board = []
        self.score = 0
        self.game_over = False
        self.won = False
        self.animations: List[TileAnimation] = []
        self.new_tile_animations: List[TileAnimation] = []
        self.reset_game()
    
    def reset_game(self):
        self.board = [[0 for _ in range(self.config.board_size)] for _ in range(self.config.board_size)]
        self.score = 0
        self.game_over = False
        self.won = False
        self.animations = []
        self.new_tile_animations = []
        self.initialize_game()
    
    def initialize_game(self):
        for _ in range(self.config.initial_tiles):
            self.add_new_tile_with_animation()
    
    def add_new_tile_with_animation(self):
        empty_cells = [(i, j) for i in range(self.config.board_size) 
                      for j in range(self.config.board_size) if self.board[i][j] == 0]
        
        if empty_cells:
            i, j = random.choice(empty_cells)
            value = self.choose_tile_value()
            self.board[i][j] = value

            board_start_x, board_start_y = self.get_board_position()
            start_x = board_start_x + j * (self.config.tile_size + self.config.padding)
            start_y = board_start_y + i * (self.config.tile_size + self.config.padding)
        
            anim = TileAnimation(
                (start_x + self.config.tile_size // 2, start_y + self.config.tile_size // 2),
                (start_x, start_y),
                value,
                AnimationType.APPEAR,
                self.config.animation_duration
            )
            self.new_tile_animations.append(anim)
    
    def choose_tile_value(self) -> int:
        rand = random.random()
        cumulative = 0
        
        for value_str, prob in self.config.probabilities.items():
            cumulative += prob
            if rand <= cumulative:
                return int(value_str)
        
        return 2
    
    def move(self, direction: str) -> bool:
        if self.game_over or self.animations:
            return False
        
        old_board = [row[:] for row in self.board]
        moved = False
        
        if direction == 'up':
            moved = self.move_up()
        elif direction == 'down':
            moved = self.move_down()
        elif direction == 'left':
            moved = self.move_left()
        elif direction == 'right':
            moved = self.move_right()
        else:
            return False
        
        if moved:
            self.add_new_tile_with_animation()
            self.check_game_state()
            return True
        
        return False
    
    def move_left(self) -> bool:
        moved = False
        for i in range(self.config.board_size):
            original_row = self.board[i][:]
            non_zero = [cell for cell in original_row if cell != 0]
            new_row, score_add, animations = self.compress_with_animation(non_zero, i, 'left')
            self.score += score_add
            new_row.extend([0] * (self.config.board_size - len(new_row)))
            
            if original_row != new_row:
                moved = True
                self.board[i] = new_row
                self.animations.extend(animations)
        
        return moved
    
    def move_right(self) -> bool:
        moved = False
        for i in range(self.config.board_size):
            original_row = self.board[i][:]
            non_zero = [cell for cell in original_row if cell != 0][::-1]
            
            new_row, score_add, animations = self.compress_with_animation(non_zero, i, 'right')
            self.score += score_add
            
            new_row.extend([0] * (self.config.board_size - len(new_row)))
            new_row = new_row[::-1]
            
            if original_row != new_row:
                moved = True
                self.board[i] = new_row
                self.animations.extend(animations)
        
        return moved
    
    def move_up(self) -> bool:
        moved = False
        for j in range(self.config.board_size):
            original_col = [self.board[i][j] for i in range(self.config.board_size)]
            non_zero = [cell for cell in original_col if cell != 0]
            
            new_col, score_add, animations = self.compress_with_animation(non_zero, j, 'up')
            self.score += score_add
            
            new_col.extend([0] * (self.config.board_size - len(new_col)))
            
            if original_col != new_col:
                moved = True
                for i in range(self.config.board_size):
                    self.board[i][j] = new_col[i]
                self.animations.extend(animations)
        
        return moved
    
    def move_down(self) -> bool:
        moved = False
        for j in range(self.config.board_size):
            original_col = [self.board[i][j] for i in range(self.config.board_size)]
            non_zero = [cell for cell in original_col if cell != 0][::-1]
            
            new_col, score_add, animations = self.compress_with_animation(non_zero, j, 'down')
            self.score += score_add
            
            new_col.extend([0] * (self.config.board_size - len(new_col)))
            new_col = new_col[::-1]
            
            if original_col != new_col:
                moved = True
                for i in range(self.config.board_size):
                    self.board[i][j] = new_col[i]
                self.animations.extend(animations)
        
        return moved
    
    def compress_with_animation(self, line: List[int], index: int, direction: str) -> Tuple[List[int], int, List[TileAnimation]]:
        if not line:
            return [], 0, []
        
        result = []
        score_add = 0
        animations = []
        i = 0
        board_start_x, board_start_y = self.get_board_position()
        
        while i < len(line):
            if i + 1 < len(line) and line[i] == line[i + 1]:
                merged_value = line[i] * 2
                score_add += merged_value
                
                if direction in ['left', 'right']:
                    start_pos1 = self.get_tile_position(index, len(result) if direction == 'left' else self.config.board_size - len(result) - 1)
                    start_pos2 = self.get_tile_position(index, len(result) + 1 if direction == 'left' else self.config.board_size - len(result) - 2)
                    end_pos = self.get_tile_position(index, len(result) if direction == 'left' else self.config.board_size - len(result) - 1)
                else:
                    start_pos1 = self.get_tile_position(len(result), index if direction == 'up' else self.config.board_size - index - 1)
                    start_pos2 = self.get_tile_position(len(result) + 1, index if direction == 'up' else self.config.board_size - index - 1)
                    end_pos = self.get_tile_position(len(result), index if direction == 'up' else self.config.board_size - index - 1)
                
                anim1 = TileAnimation(start_pos1, end_pos, line[i], AnimationType.MERGE, self.config.animation_duration)
                anim2 = TileAnimation(start_pos2, end_pos, line[i + 1], AnimationType.MERGE, self.config.animation_duration)
                animations.extend([anim1, anim2])
                
                result.append(merged_value)
                i += 2
            else:
                if direction in ['left', 'right']:
                    start_pos = self.get_tile_position(index, i if direction == 'left' else self.config.board_size - i - 1)
                    end_pos = self.get_tile_position(index, len(result) if direction == 'left' else self.config.board_size - len(result) - 1)
                else:
                    start_pos = self.get_tile_position(i, index if direction == 'up' else self.config.board_size - index - 1)
                    end_pos = self.get_tile_position(len(result), index if direction == 'up' else self.config.board_size - index - 1)
                
                if start_pos != end_pos:
                    anim = TileAnimation(start_pos, end_pos, line[i], AnimationType.MOVE, self.config.animation_duration)
                    animations.append(anim)
                
                result.append(line[i])
                i += 1
        
        return result, score_add, animations
    
    def get_board_position(self) -> Tuple[int, int]:
        board_width = self.config.board_size * (self.config.tile_size + self.config.padding) + self.config.padding
        board_start_x = (self.config.window_size[0] - board_width) // 2
        board_start_y = 100
        return board_start_x, board_start_y
    
    def get_tile_position(self, row: int, col: int) -> Tuple[int, int]:
        board_start_x, board_start_y = self.get_board_position()
        x = board_start_x + col * (self.config.tile_size + self.config.padding)
        y = board_start_y + row * (self.config.tile_size + self.config.padding)
        return (x, y)
    
    def check_game_state(self):
        if any(any(cell >= self.config.target_score for cell in row) for row in self.board):
            self.won = True
        if not self.has_valid_moves():
            self.game_over = True
    
    def has_valid_moves(self) -> bool:
        if any(any(cell == 0 for cell in row) for row in self.board):
            return True
        for i in range(self.config.board_size):
            for j in range(self.config.board_size):
                current = self.board[i][j]
                if (j + 1 < self.config.board_size and self.board[i][j + 1] == current or
                    i + 1 < self.config.board_size and self.board[i + 1][j] == current):
                    return True
        
        return False
    
    def update_animations(self):
        self.animations = [anim for anim in self.animations if not anim.update()]
        self.new_tile_animations = [anim for anim in self.new_tile_animations if not anim.update()]