import pygame
from random import choice

pygame.font.init()

font = pygame.font.SysFont('Georgia', 20, bold=True)
surf = font.render('HINT', True, 'white')
button = pygame.Rect(650, 450, 80, 40)

# Creating grid cell
class Cell:
    def __init__(self, x, y, thickness):
        self.x, self.y = x, y
        self.thickness = thickness
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    # draw grid cell walls
    def draw(self, sc, tile):
        x, y = self.x * tile, self.y * tile
        if self.walls['top']:
            pygame.draw.line(sc, pygame.Color('white'), (x, y), (x + tile, y), self.thickness)
        if self.walls['right']:
            pygame.draw.line(sc, pygame.Color('white'), (x + tile, y), (x + tile, y + tile), self.thickness)
        if self.walls['bottom']:
            pygame.draw.line(sc, pygame.Color('white'), (x + tile, y + tile), (x , y + tile), self.thickness)
        if self.walls['left']:
            pygame.draw.line(sc, pygame.Color('white'), (x, y + tile), (x, y), self.thickness)


    # checks if cell does exist and returns it if it does
    def check_cell(self, x, y, cols, rows, grid_cells):
        find_index = lambda x, y: x + y * cols
        if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:
            return False
        return grid_cells[find_index(x, y)]

    # checking cell neighbors of current cell if visited (carved) or not
    def check_neighbors(self, cols, rows, grid_cells):
        neighbors = []
        top = self.check_cell(self.x, self.y - 1, cols, rows, grid_cells)
        right = self.check_cell(self.x + 1, self.y, cols, rows, grid_cells)
        bottom = self.check_cell(self.x, self.y + 1, cols, rows, grid_cells)
        left = self.check_cell(self.x - 1, self.y, cols, rows, grid_cells)
        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)
        return choice(neighbors) if neighbors else False
    


# Creating Maze
class Maze:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.thickness = 4
        self.grid_cells = [Cell(col, row, self.thickness) for row in range(self.rows) for col in range(self.cols)]

    

    # carve grid cell walls
    def remove_walls(self, current, next):
        dx = current.x - next.x
        if dx == 1:
            current.walls['left'] = False
            next.walls['right'] = False
        elif dx == -1:
            current.walls['right'] = False
            next.walls['left'] = False
        dy = current.y - next.y
        if dy == 1:
            current.walls['top'] = False
            next.walls['bottom'] = False
        elif dy == -1:
            current.walls['bottom'] = False
            next.walls['top'] = False



    def generate_maze(self):
        current_cell = self.grid_cells[0]
        array = []
        break_count = 1
        while break_count != len(self.grid_cells):
            current_cell.visited = True
            next_cell = current_cell.check_neighbors(self.cols, self.rows, self.grid_cells)
            if next_cell:
                next_cell.visited = True
                break_count += 1
                array.append(current_cell)
                self.remove_walls(current_cell, next_cell)
                current_cell = next_cell
            elif array:
                current_cell = array.pop()
        return self.grid_cells
    



# Creating Player
class Player:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
        self.player_size = 10
        self.rect = pygame.Rect(self.x, self.y, self.player_size, self.player_size)
        self.color = (250, 120, 60)
        self.velX = 0
        self.velY = 0
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.speed = 4


    # get current cell position of the player
    def get_current_cell(self, x, y, grid_cells):
        for cell in grid_cells:
            if cell.x == x and cell.y == y:
                return cell

    # stops player to pass through walls
    def check_move(self, tile, grid_cells, thickness):
        current_cell_x, current_cell_y = self.x // tile, self.y // tile
        current_cell = self.get_current_cell(current_cell_x, current_cell_y, grid_cells)
        current_cell_abs_x, current_cell_abs_y = current_cell_x * tile, current_cell_y * tile
        if self.left_pressed:
            if current_cell.walls['left']:
                if self.x <= current_cell_abs_x + thickness:
                    self.left_pressed = False
        if self.right_pressed:
            if current_cell.walls['right']:
                if self.x >= current_cell_abs_x + tile - (self.player_size + thickness):
                    self.right_pressed = False
        if self.up_pressed:
            if current_cell.walls['top']:
                if self.y <= current_cell_abs_y + thickness:
                    self.up_pressed = False
        if self.down_pressed:
            if current_cell.walls['bottom']:
                if self.y >= current_cell_abs_y + tile - (self.player_size + thickness):
                    self.down_pressed = False



    # drawing player to the screen
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    # updates player position while moving
    def update(self):
        self.velX = 0
        self.velY = 0
        if self.left_pressed and not self.right_pressed:
            self.velX = -self.speed
        if self.right_pressed and not self.left_pressed:
            self.velX = self.speed
        if self.up_pressed and not self.down_pressed:
            self.velY = -self.speed
        if self.down_pressed and not self.up_pressed:
            self.velY = self.speed
        self.x += self.velX
        self.y += self.velY
        self.rect = pygame.Rect(int(self.x), int(self.y), self.player_size, self.player_size)




pygame.font.init()

class Game:
    def __init__(self, goal_cell, tile):
        self.font = pygame.font.SysFont("impact", 35)
        self.message_color = pygame.Color("darkorange")
        self.goal_cell = goal_cell
        self.tile = tile
        self.hint_button = False

    # add goal point for player to reach
    def add_goal_point(self, screen):
        # adding gate for the goal point
        img_path = 'gate.jpg'
        img = pygame.image.load(img_path)
        img = pygame.transform.scale(img, (self.tile, self.tile))
        screen.blit(img, (self.goal_cell.x * self.tile, self.goal_cell.y * self.tile))

    # winning message
    def message(self):
        msg = self.font.render('You Win!!', True, self.message_color)
        return msg

    # checks if player reached the goal point
    def is_game_over(self, player):
        goal_cell_abs_x, goal_cell_abs_y = self.goal_cell.x * self.tile, self.goal_cell.y * self.tile
        if player.x >= goal_cell_abs_x and player.y >= goal_cell_abs_y:
            return True
        else:
            return False
        



import time

pygame.font.init()


# Adding Clock
class Clock:
    def __init__(self):
        self.start_time = None
        self.elapsed_time = 0
        self.font = pygame.font.SysFont("monospace", 35)
        self.message_color = pygame.Color("yellow")

    # Start the timer
    def start_timer(self):
        self.start_time = time.time()

    # Update the timer
    def update_timer(self):
        if self.start_time is not None:
            self.elapsed_time = time.time() - self.start_time

    # Display the timer
    def display_timer(self):
        secs = int(self.elapsed_time % 60)
        mins = int(self.elapsed_time / 60)
        my_time = self.font.render(f"{mins:02}:{secs:02}", True, self.message_color)
        return my_time

    # Stop the timer
    def stop_timer(self):
        self.start_time = None


import sys

pygame.init()
pygame.font.init()

from collections import deque

class Main():
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("impact", 30)
        self.message_color = pygame.Color("cyan")
        self.running = True
        self.game_over = False
        self.hint_button = False
        self.FPS = pygame.time.Clock()
        self.button = pygame.Rect(650, 450, 80, 40)
        self.hint_path = []


    def instructions(self):
        instructions1 = self.font.render('Use', True, self.message_color)
        instructions2 = self.font.render('Arrow Keys', True, self.message_color)
        instructions3 = self.font.render('to Move', True, self.message_color)
        self.screen.blit(instructions1,(655,300))
        self.screen.blit(instructions2,(610,331))
        self.screen.blit(instructions3,(630,362))


    # draws all configs; maze, player, instructions, and time
    def _draw(self, maze, tile, player, game, clock):
        # draw maze
        [cell.draw(self.screen, tile) for cell in maze.grid_cells]
        # add a goal point to reach
        game.add_goal_point(self.screen)
        # draw every player movement
        player.draw(self.screen)
        player.update()

        # Draw the hint path if it is enabled.
   
        if self.hint_path:
            self.draw_hint_path()
        
        # instructions, clock, winning message
        self.instructions()
        if self.game_over:
            clock.stop_timer()
            self.screen.blit(game.message(),(610,120))
        else:
            clock.update_timer()
        self.screen.blit(clock.display_timer(), (625,200))
        pygame.display.flip()


    def draw_hint_path(self):
        if self.hint_path:
            for i in range(1, len(self.hint_path)):
                current_cell = self.hint_path[i-1]
                next_cell = self.hint_path[i]
                pygame.draw.line(self.screen, pygame.Color("blue"),
                                (current_cell.x * self.tile + self.tile // 2, current_cell.y * self.tile + self.tile // 2),
                                (next_cell.x * self.tile + self.tile // 2, next_cell.y * self.tile + self.tile // 2), 3)


                
    def find_path_bfs(self, maze, start_cell, end_cell):
        visited = set()
        queue = deque()
        path = {start_cell: None}
    
        queue.append(start_cell)
        visited.add(start_cell)
    
        while queue:
            current_cell = queue.popleft()
        
            if current_cell == end_cell:
                break
        
            neighbors = current_cell.check_neighbors(maze.cols, maze.rows, maze.grid_cells)
            if neighbors is False:
                continue  # Skip if there are no valid neighbors
        
            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)
                    path[neighbor] = current_cell
    
        if end_cell not in path:
            return None
    
    # Reconstruct the path from end to start
        path_list = []
        while end_cell is not None:
            path_list.append(end_cell)
            end_cell = path[end_cell]
    
        return list(reversed(path_list))



    # main game loop
    def main(self, frame_size, tile):
        cols, rows = frame_size[0] // tile, frame_size[-1] // tile
        maze = Maze(cols, rows)
        game = Game(maze.grid_cells[-1], tile)
        player = Player(tile // 3, tile // 3)
        clock = Clock()
        maze.generate_maze()
        clock.start_timer()
        while self.running:
            self.screen.fill("black")
            self.screen.fill( pygame.Color("darkslategray"), (603, 0, 752, 752))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            # if keys were pressed still
            if event.type == pygame.KEYDOWN:
                if not self.game_over:
                    if event.key == pygame.K_LEFT:
                        player.left_pressed = True
                    if event.key == pygame.K_RIGHT:
                        player.right_pressed = True
                    if event.key == pygame.K_UP:
                        player.up_pressed = True
                    if event.key == pygame.K_DOWN:
                        player.down_pressed = True
                    player.check_move(tile, maze.grid_cells, maze.thickness)
            # if pressed key released
            if event.type == pygame.KEYUP:
                if not self.game_over:
                    if event.key == pygame.K_LEFT:
                        player.left_pressed = False
                    if event.key == pygame.K_RIGHT:
                        player.right_pressed = False
                    if event.key == pygame.K_UP:
                        player.up_pressed = False
                    if event.key == pygame.K_DOWN:
                        player.down_pressed = False
                    player.check_move(tile, maze.grid_cells, maze.thickness)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.button.collidepoint(event.pos):
                    self.hint_button = not self.hint_button
                    if self.hint_button:
                            # Calculate the hint path
                            start_cell = maze.grid_cells[0]
                            end_cell = maze.grid_cells[-1]
                            self.hint_path = self.find_path_bfs(maze, start_cell, end_cell)
                            self.draw_hint_path()
                    else:
                        self.hint_path = []

            a, b = pygame.mouse.get_pos()

            if button.x <= a <= button.x + 70 and button.y <= b <= button.y + 50:
                pygame.draw.rect(self.screen, (180, 180, 180), button)
            else:
                pygame.draw.rect(self.screen, (110, 110, 110), button)

            self.screen.blit(surf, (button.x + 5, button.y + 5))


                

            if game.is_game_over(player):
                self.game_over = True
                player.left_pressed = False
                player.right_pressed = False
                player.up_pressed = False
                player.down_pressed = False
            self._draw(maze, tile, player, game, clock)
            self.FPS.tick(60)



if __name__ == "__main__":
    n = int(input("Enter the number of tiles for maze dimensions: "))
    window_size = (602, 602)
    screen = (window_size[0] + 150, window_size[-1])
    tile_size = window_size[0]//n
    screen = pygame.display.set_mode(screen)
    pygame.display.set_caption("Maze Game")

    game = Main(screen)
    game.main(window_size, tile_size)