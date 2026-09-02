import os
import pygame
import sys
import random
from pathlib import Path
from color import color_list

DESIGN_W = 1080
DESIGN_H = 1920
CONTROL_RATIO = 0.28

Black = (0, 0, 0)
white = (200, 200, 200)
Red = (255, 0, 0)
panel_bg = (30, 30, 30)
btn_normal = (70, 70, 70)
btn_pressed = (120, 120, 120)
btn_border = (160, 160, 160)

IS_ANDROID = bool(os.environ.get("ANDROID_ARGUMENT") or os.environ.get("ANDROID_PRIVATE"))


def resource_path(relative_path):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base / relative_path


class VirtualButton:
    def __init__(self, rect, label, action):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action
        self.pressed = False
        self.touch_ids = set()

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def press(self, touch_id=None):
        self.pressed = True
        if touch_id is not None:
            self.touch_ids.add(touch_id)

    def release(self, touch_id=None):
        if touch_id is not None:
            self.touch_ids.discard(touch_id)
        if touch_id is None or not self.touch_ids:
            self.pressed = False

    def draw(self, surface, font):
        color = btn_pressed if self.pressed else btn_normal
        radius = max(12, self.rect.width // 8)
        pygame.draw.rect(surface, color, self.rect, border_radius=radius)
        pygame.draw.rect(surface, btn_border, self.rect, 3, border_radius=radius)
        text = font.render(self.label, True, white)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)


def build_virtual_buttons(game_height, control_height):
    btn = 140
    gap = 24
    pad_x = 80
    pad_y = game_height + (control_height - (btn * 2 + gap)) // 2
    center_x = pad_x + btn + gap + btn // 2

    shift_w = 180
    shift_h = min(control_height - 60, 280)
    r_size = 140

    return {
        "w": VirtualButton((center_x - btn // 2, pad_y, btn, btn), "W", "w"),
        "a": VirtualButton((pad_x, pad_y + btn + gap, btn, btn), "A", "a"),
        "s": VirtualButton((center_x - btn // 2, pad_y + btn + gap, btn, btn), "S", "s"),
        "d": VirtualButton((pad_x + (btn + gap) * 2, pad_y + btn + gap, btn, btn), "D", "d"),
        "shift": VirtualButton(
            (DESIGN_W - shift_w - r_size - 100, game_height + (control_height - shift_h) // 2, shift_w, shift_h),
            "Shift",
            "shift",
        ),
        "r": VirtualButton(
            (DESIGN_W - r_size - 60, game_height + (control_height - r_size) // 2, r_size, r_size),
            "R",
            "r",
        ),
    }


def find_button_at(pos, buttons):
    for button in buttons.values():
        if button.contains(pos):
            return button
    return None


class GameLogic:
    def __init__(self, grid_width, grid_height, fps):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.fps = fps
        self.snake = []
        self.direction = (1, 0)
        self.food = (0, 0)
        self.monster = None
        self.game_over = False
        self.score = 0
        self.monster_move_timer = 0
        self.monster_move_interval = 3

    def reset_game(self):
        init_head = (
            random.randint(0, self.grid_width - 1),
            random.randint(0, self.grid_height - 1),
        )
        self.snake = [init_head]
        self.direction = (1, 0)
        self.score = 0
        self.game_over = False
        self.generate_monster()
        self.generate_food()

    def generate_food(self):
        mx, my = self.monster
        monster_cells = [(mx, my), (mx + 1, my), (mx, my + 1), (mx + 1, my + 1)]
        while True:
            pos = (
                random.randint(0, self.grid_width - 1),
                random.randint(0, self.grid_height - 1),
            )
            if pos not in self.snake and pos not in monster_cells:
                self.food = pos
                break

    def generate_monster(self):
        while True:
            x = random.randint(0, self.grid_width - 2)
            y = random.randint(0, self.grid_height - 2)
            monster_cells = [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
            overlap = any(cell in self.snake or cell == self.food for cell in monster_cells)
            if not overlap:
                self.monster = (x, y)
                break

    def check_wall(self, head):
        return (
            head[0] < 0
            or head[0] >= self.grid_width
            or head[1] < 0
            or head[1] >= self.grid_height
        )

    def check_eatself(self, head):
        return head in self.snake[1:]

    def check_monster(self, head):
        if not self.monster:
            return False
        mx, my = self.monster
        return (mx <= head[0] <= mx + 1) and (my <= head[1] <= my + 1)

    def move_monster_randomly(self):
        if not self.monster:
            return
        mx, my = self.monster
        dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            new_x, new_y = mx + dx, my + dy
            if 0 <= new_x <= self.grid_width - 2 and 0 <= new_y <= self.grid_height - 2:
                new_cells = [
                    (new_x, new_y),
                    (new_x + 1, new_y),
                    (new_x, new_y + 1),
                    (new_x + 1, new_y + 1),
                ]
                overlap = any(cell in self.snake or cell == self.food for cell in new_cells)
                if not overlap:
                    self.monster = (new_x, new_y)
                    return

    def apply_direction(self, action):
        if action == "w" and self.direction != (0, 1):
            self.direction = (0, -1)
        elif action == "s" and self.direction != (0, -1):
            self.direction = (0, 1)
        elif action == "a" and self.direction != (1, 0):
            self.direction = (-1, 0)
        elif action == "d" and self.direction != (-1, 0):
            self.direction = (1, 0)

    def handle_virtual_input(self, action):
        if action == "r":
            if self.game_over:
                self.reset_game()
            return
        if self.game_over:
            return
        if action in ("w", "a", "s", "d"):
            self.apply_direction(action)

    def step(self):
        new_head = self.snake[0]
        self.monster_move_timer += 1
        if self.monster_move_timer >= self.monster_move_interval:
            self.monster_move_timer = 0
            self.move_monster_randomly()

        if not self.game_over:
            head_x, head_y = self.snake[0]
            new_head = (head_x + self.direction[0], head_y + self.direction[1])
            self.snake.insert(0, new_head)
            if new_head == self.food:
                self.generate_food()
                self.score += 1
            else:
                self.snake.pop()

        if self.check_wall(new_head) or self.check_eatself(new_head) or self.check_monster(new_head):
            self.game_over = True

        return new_head

    def draw_snake(self, surface, grid_size):
        for x, y in self.snake:
            count = random.randint(0, len(color_list) - 1)
            pygame.draw.rect(
                surface,
                color_list[count],
                (x * grid_size, y * grid_size, grid_size, grid_size),
            )


def create_display():
    if IS_ANDROID:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        display_w, display_h = screen.get_size()
    else:
        display_w, display_h = DESIGN_W // 2, DESIGN_H // 2
        screen = pygame.display.set_mode((display_w, display_h))
    return screen, display_w, display_h


def logical_pos(event, display_w, display_h):
    if event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
        x = int(event.x * display_w)
        y = int(event.y * display_h)
    else:
        x, y = event.pos
    scale_x = display_w / DESIGN_W
    scale_y = display_h / DESIGN_H
    return int(x / scale_x), int(y / scale_y)


def run():
    pygame.init()

    control_height = int(DESIGN_H * CONTROL_RATIO)
    game_height = DESIGN_H - control_height
    grid_size = DESIGN_W // 30
    grid_width = DESIGN_W // grid_size
    grid_height = game_height // grid_size

    screen, display_w, display_h = create_display()
    pygame.display.set_caption("Gudo Snake")
    clock = pygame.time.Clock()

    canvas = pygame.Surface((DESIGN_W, DESIGN_H))
    standard_font = pygame.font.Font(None, 72)
    remind_font = pygame.font.Font(None, 48)
    button_font = pygame.font.Font(None, 56)

    monster_size = grid_size * 2
    monster_image = pygame.image.load(resource_path("assets/monster.jpg")).convert()
    monster_image = pygame.transform.scale(monster_image, (monster_size, monster_size))

    game = GameLogic(grid_width, grid_height, fps=10)
    game.reset_game()
    virtual_buttons = build_virtual_buttons(game_height, control_height)
    active_touches = {}

    def draw_control_panel():
        panel_rect = pygame.Rect(0, game_height, DESIGN_W, control_height)
        pygame.draw.rect(canvas, panel_bg, panel_rect)
        pygame.draw.line(canvas, btn_border, (0, game_height), (DESIGN_W, game_height), 3)
        for button in virtual_buttons.values():
            button.draw(canvas, button_font)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game.game_over and event.key == pygame.K_r:
                    game.reset_game()
                    continue
                if event.key == pygame.K_ESCAPE and not IS_ANDROID:
                    running = False
                if not game.game_over:
                    if event.key == pygame.K_w:
                        game.apply_direction("w")
                    elif event.key == pygame.K_s:
                        game.apply_direction("s")
                    elif event.key == pygame.K_a:
                        game.apply_direction("a")
                    elif event.key == pygame.K_d:
                        game.apply_direction("d")

            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                pos = logical_pos(event, display_w, display_h)
                touch_id = getattr(event, "finger_id", None)
                if touch_id is None:
                    touch_id = f"mouse_{event.button}"
                button = find_button_at(pos, virtual_buttons)
                if button:
                    button.press(touch_id)
                    active_touches[touch_id] = button
                    if button.action != "shift":
                        game.handle_virtual_input(button.action)

            if event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
                touch_id = getattr(event, "finger_id", None)
                if touch_id is None:
                    touch_id = f"mouse_{getattr(event, 'button', 1)}"
                button = active_touches.pop(touch_id, None)
                if button:
                    button.release(touch_id)

        game.step()

        canvas.fill(Black)
        game.draw_snake(canvas, grid_size)
        pygame.draw.rect(
            canvas,
            Red,
            (game.food[0] * grid_size, game.food[1] * grid_size, grid_size, grid_size),
        )

        if game.monster:
            mx, my = game.monster
            canvas.blit(monster_image, (mx * grid_size, my * grid_size))

        if game.game_over:
            over_text = standard_font.render("Game over", True, white)
            over_rect = over_text.get_rect(center=(DESIGN_W // 2, game_height // 2 - 60))
            remind_text = remind_font.render("Tap R to continue", True, white)
            remind_rect = remind_text.get_rect(center=(DESIGN_W // 2, game_height // 2))
            score_text = remind_font.render(f"Your final score is {game.score}", True, white)
            score_rect = score_text.get_rect(center=(DESIGN_W // 2, game_height // 2 + 60))
            canvas.blit(over_text, over_rect)
            canvas.blit(remind_text, remind_rect)
            canvas.blit(score_text, score_rect)

        draw_control_panel()

        scaled = pygame.transform.smoothscale(canvas, (display_w, display_h))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

        keys = pygame.key.get_pressed()
        shift_held = keys[pygame.K_LSHIFT] or virtual_buttons["shift"].pressed
        fps = game.fps * 3 if shift_held else game.fps
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    run()
