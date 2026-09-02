import pygame
import sys
import random
from pathlib import Path
from color import color_list


def resource_path(relative_path):
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
    return base / relative_path


pygame.init()

screen_width = 600
screen_height = 600
grid_size = 20

gride_width = screen_width // grid_size
gride_height = screen_height // grid_size



Black = (0, 0, 0)
white = (200, 200, 200)
Red = (255, 0, 0)



screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Snake')
clock = pygame.time.Clock()
standard_font = pygame.font.Font(None, 36)
remind_font = pygame.font.Font(None, 24)

food = (0,0)
monster = None
monster_move_timer = 0
monster_move_interval = 3

monster_size = grid_size * 2
monster_image = pygame.image.load(resource_path("assets/monster.jpg")).convert()
monster_image = pygame.transform.scale(monster_image, (monster_size, monster_size))

class option():
    def __init__(self, x):
        self.FPS =x

    def reset_game(self):
        global snake, direction, food, game_over, score, monster
        init_head = (random.randint(0, gride_width-1), random.randint(0, gride_height-1))
        snake = [init_head] 
        direction = (1, 0)
        score = 0
        game_over = False
        game.generate_monster()
        game.generate_food()

    def generate_food(self):
        global food
        mx,my = monster
        monster_cells = [(mx, my), (mx+1, my), (mx, my+1), (mx+1, my+1)]
        while True:
            pos = (random.randint(0, gride_width-1), random.randint(0, gride_height-1))
            if pos not in snake and pos not in monster_cells:
                food = pos
                break

    def generate_monster(self):
        global monster
        while True:
            x = random.randint(0, gride_width - 2)
            y = random.randint(0, gride_height - 2)
            monster_cells = [(x, y), (x+1, y), (x, y+1), (x+1, y+1)]
            overlap = False
            for cell in monster_cells:
                if cell in snake or cell == food:
                    overlap = True
                    break
            if not overlap:
                monster = (x, y)  # 只存储左上角坐标
                break

    def check_wall(self,x):
        if x[0]<0 or x[0]>=gride_width or x[1]<0 or x[1]>=gride_height:
            return True
        else:
            return False

    def check_eatself(self,x,y):
        if x in y[1:]:
            return True
        else:
            return False

    def check_monster(self, snake, monster):
        if not snake or not monster:
            return False
    
        head = snake[0]          
        mx, my = monster         
    
        if (mx <= head[0] <= mx + 1) and (my <= head[1] <= my + 1):
            return True
        return False

    def make_snake(self,some_snake):
        for x, y in some_snake:
            count = random.randint(0,len(color_list)-1)
            pygame.draw.rect(screen, color_list[count], (x * grid_size, y * grid_size, grid_size, grid_size))

game = option(10)
game.reset_game()
new_head = snake[0]

def move_monster_randomly():
    global monster
    if not monster:
        return
    mx, my = monster
    dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    random.shuffle(dirs)
    for dx, dy in dirs:
        new_x, new_y = mx + dx, my + dy
        if 0 <= new_x <= gride_width - 2 and 0 <= new_y <= gride_height - 2:
            new_cells = [(new_x, new_y), (new_x+1, new_y), (new_x, new_y+1), (new_x+1, new_y+1)]
            overlap = False
            for cell in new_cells:
                if cell in snake or cell == food:
                    overlap = True
                    break
            if not overlap:
                monster = (new_x, new_y)
                return

while True:

    for event in pygame.event.get():  

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:


            if game_over and event.key == pygame.K_r:
                game.reset_game()
                continue 
                
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if not game_over:

                if event.key == pygame.K_w and direction != (0, 1):
                    direction = (0, -1)
                    
                if event.key == pygame.K_s and direction != (0, -1):
                    direction = (0, 1)
                    
                if event.key == pygame.K_a and direction != (1, 0):
                    direction = (-1, 0)
                    
                if event.key == pygame.K_d and direction != (-1, 0):
                    direction = (1, 0)

    monster_move_timer += 1
    if monster_move_timer >= monster_move_interval:
        monster_move_timer = 0
        move_monster_randomly()
                    
    if not game_over:
        head_x, head_y = snake[0]
        new_head = (head_x + direction[0], head_y + direction[1])
        snake.insert(0, new_head)
        if new_head == food:
            game.generate_food()
            score += 1
        else:
            snake.pop()
         
    wall_hit = game.check_wall(new_head)
    self_hit = game.check_eatself(new_head, snake)
    monster_hit = game.check_monster(snake, monster)

    if wall_hit:
        game_over = True
    
    if self_hit:
        game_over = True
    
    if monster_hit:
        game_over = True

    
    screen.fill(Black)

    game.make_snake(snake)

    pygame.draw.rect(screen, Red, (food[0]*grid_size, food[1]*grid_size, grid_size, grid_size))
    
    if monster:
        mx, my = monster
        screen.blit(monster_image, (mx * grid_size, my * grid_size))

    if game_over:
        over_text = standard_font.render('Game over', True, white)
        over_rect = over_text.get_rect(center=(screen_width//2, screen_height//2 - 30))
        remind_text = remind_font.render('Press R to continue; Press esc to quit', True, white)
        remind_rect = remind_text.get_rect(center = (screen_width//2, screen_height//2  ) )
        score_text = remind_font.render(f'Your final score is {score}', True, white)
        score_rect = score_text.get_rect(center = (screen_width//2, screen_height//2 + 30) )
        screen.blit(over_text, over_rect)
        screen.blit(remind_text, remind_rect)
        screen.blit(score_text, score_rect)


    pygame.display.flip()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LSHIFT]:
        FPS = game.FPS * 3
    else:
        FPS = game.FPS

    clock.tick(FPS)
