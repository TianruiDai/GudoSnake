import math
import random
import sys
from pathlib import Path

import pygame


def resource_path(relative_path):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base / relative_path


pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 760
GRID_SIZE = 20
BOARD_SIZE = 640
GRID_WIDTH = BOARD_SIZE // GRID_SIZE
GRID_HEIGHT = BOARD_SIZE // GRID_SIZE
BOARD_X = 36
BOARD_Y = 84
PANEL_X = 714
PANEL_WIDTH = 330

BG = (11, 9, 24)
BOARD_BG = (18, 18, 38)
PANEL_BG = (22, 17, 42)
GRID = (39, 35, 70)
GRID_BRIGHT = (49, 44, 87)
INK = (236, 235, 255)
MUTED = (145, 140, 180)
CYAN = (65, 239, 224)
LIME = (183, 255, 74)
PINK = (255, 75, 166)
ORANGE = (255, 168, 76)
RED = (255, 80, 102)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("GUDO SNAKE // CURSED EDITION")
clock = pygame.time.Clock()
title_font = pygame.font.SysFont("consolas", 29, bold=True)
score_font = pygame.font.SysFont("consolas", 52, bold=True)
body_font = pygame.font.SysFont("consolas", 18, bold=True)
small_font = pygame.font.SysFont("consolas", 14)

monster_size = GRID_SIZE * 2
monster_image = pygame.image.load(resource_path("assets/monster.jpg")).convert()
monster_image = pygame.transform.scale(monster_image, (monster_size, monster_size))
monster_preview = pygame.transform.scale(monster_image, (92, 92))

sound_bank = []
sound_paths = sorted(resource_path("sounds").rglob("*.mp3"))
sound_volume = 0.75
if pygame.mixer.get_init():
    for sound_path in sound_paths:
        try:
            sound = pygame.mixer.Sound(str(sound_path))
            sound.set_volume(sound_volume)
            sound_bank.append(sound)
        except pygame.error:
            continue

snake = []
direction = (1, 0)
food = (0, 0)
monster = None
score = 0
high_score = 0
game_over = False
paused = False
move_accumulator = 0.0
monster_accumulator = 0.0
particles = []
eat_flash = 0.0
death_reason = ""


def cell_rect(cell, padding=2):
    x, y = cell
    return pygame.Rect(
        BOARD_X + x * GRID_SIZE + padding,
        BOARD_Y + y * GRID_SIZE + padding,
        GRID_SIZE - padding * 2,
        GRID_SIZE - padding * 2,
    )


def monster_cells_at(position):
    x, y = position
    return {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)}


def generate_monster():
    global monster
    while True:
        candidate = (
            random.randint(0, GRID_WIDTH - 2),
            random.randint(0, GRID_HEIGHT - 2),
        )
        if not (monster_cells_at(candidate) & set(snake)) and food not in monster_cells_at(candidate):
            monster = candidate
            return


def generate_food():
    global food
    blocked = set(snake)
    if monster:
        blocked |= monster_cells_at(monster)
    while True:
        candidate = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1),
        )
        if candidate not in blocked:
            food = candidate
            return


def reset_game():
    global snake, direction, score, game_over, paused
    global move_accumulator, monster_accumulator, particles, eat_flash, death_reason
    center = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
    snake = [(center[0] - i, center[1]) for i in range(4)]
    direction = (1, 0)
    score = 0
    game_over = False
    paused = False
    move_accumulator = 0.0
    monster_accumulator = 0.0
    particles = []
    eat_flash = 0.0
    death_reason = ""
    generate_monster()
    generate_food()


def play_snack_sound():
    if sound_bank:
        pygame.mixer.stop()
        random.choice(sound_bank).play()


def play_collision_sound():
    if sound_bank:
        pygame.mixer.stop()
        random.choice(sound_bank).play()


def spawn_particles(cell):
    px = BOARD_X + cell[0] * GRID_SIZE + GRID_SIZE / 2
    py = BOARD_Y + cell[1] * GRID_SIZE + GRID_SIZE / 2
    for _ in range(14):
        angle = random.random() * math.tau
        speed = random.uniform(35, 105)
        particles.append(
            {
                "x": px,
                "y": py,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.uniform(0.35, 0.75),
                "size": random.randint(2, 5),
            }
        )


def update_particles(dt):
    for particle in particles[:]:
        particle["life"] -= dt
        if particle["life"] <= 0:
            particles.remove(particle)
            continue
        particle["x"] += particle["vx"] * dt
        particle["y"] += particle["vy"] * dt
        particle["vy"] += 75 * dt


def move_monster_randomly():
    global monster
    if not monster or not snake:
        return
    current_x, current_y = monster
    choices = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    random.shuffle(choices)
    valid_moves = []
    for dx, dy in choices:
        candidate = (current_x + dx, current_y + dy)
        if not (0 <= candidate[0] <= GRID_WIDTH - 2 and 0 <= candidate[1] <= GRID_HEIGHT - 2):
            continue
        if monster_cells_at(candidate) & set(snake):
            continue
        if food in monster_cells_at(candidate):
            continue
        head_x, head_y = snake[0]
        distance = abs(candidate[0] - head_x) + abs(candidate[1] - head_y)
        valid_moves.append((distance, candidate))

    if not valid_moves:
        return

    valid_moves.sort(key=lambda item: item[0])
    if random.random() < 0.72:
        best_distance = valid_moves[0][0]
        best_moves = [move for distance, move in valid_moves if distance <= best_distance + 1]
        monster = random.choice(best_moves)
    else:
        monster = random.choice(valid_moves)[1]


def move_snake():
    global score, game_over, high_score, eat_flash, death_reason
    head_x, head_y = snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])
    eating = new_head == food

    wall_hit = not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT)
    body_to_check = snake if eating else snake[:-1]
    self_hit = new_head in body_to_check
    monster_hit = monster and new_head in monster_cells_at(monster)
    if wall_hit or self_hit or monster_hit:
        if wall_hit:
            death_reason = "WALL IMPACT"
        elif monster_hit:
            death_reason = "GUDO GOT YOU"
        else:
            death_reason = "SELF DESTRUCT"
        play_collision_sound()
        game_over = True
        return

    snake.insert(0, new_head)
    if eating:
        score += 1
        high_score = max(high_score, score)
        eat_flash = 0.35
        spawn_particles(food)
        play_snack_sound()
        generate_food()
    else:
        snake.pop()


def draw_text(text, font, color, position, anchor="topleft"):
    surface = font.render(text, True, color)
    rect = surface.get_rect(**{anchor: position})
    screen.blit(surface, rect)


def draw_background(elapsed):
    screen.fill(BG)
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        color = (
            int(11 + ratio * 9),
            int(9 + ratio * 5),
            int(24 + ratio * 20),
        )
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

    haze = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for position, color, radius in [
        ((BOARD_X + 80, BOARD_Y + 40), (44, 210, 191, 25), 185),
        ((SCREEN_WIDTH - 60, SCREEN_HEIGHT - 60), (242, 49, 140, 22), 210),
    ]:
        pygame.draw.circle(haze, color, position, radius)
    screen.blit(haze, (0, 0))
    draw_text("UNAUTHORIZED SNAKE SIMULATION", small_font, MUTED, (36, 16))
    draw_text("GUDO SNAKE", title_font, INK, (36, 34))
    draw_text("CURSED EDITION", body_font, PINK, (262, 42))


def draw_board():
    shadow = pygame.Rect(BOARD_X - 8, BOARD_Y - 8, BOARD_SIZE + 16, BOARD_SIZE + 16)
    pygame.draw.rect(screen, (4, 3, 12), shadow, border_radius=18)
    board = pygame.Rect(BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE)
    pygame.draw.rect(screen, BOARD_BG, board, border_radius=12)
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if (x + y) % 2 == 0:
                pygame.draw.rect(screen, (21, 21, 44), cell_rect((x, y), 0))
    for x in range(GRID_WIDTH + 1):
        line_color = GRID_BRIGHT if x % 4 == 0 else GRID
        pygame.draw.line(
            screen,
            line_color,
            (BOARD_X + x * GRID_SIZE, BOARD_Y),
            (BOARD_X + x * GRID_SIZE, BOARD_Y + BOARD_SIZE),
        )
    for y in range(GRID_HEIGHT + 1):
        line_color = GRID_BRIGHT if y % 4 == 0 else GRID
        pygame.draw.line(
            screen,
            line_color,
            (BOARD_X, BOARD_Y + y * GRID_SIZE),
            (BOARD_X + BOARD_SIZE, BOARD_Y + y * GRID_SIZE),
        )
    pygame.draw.rect(screen, CYAN, board, width=2, border_radius=12)
    pygame.draw.rect(screen, (117, 82, 191), board.inflate(-8, -8), width=1, border_radius=10)


def draw_food(elapsed):
    rect = cell_rect(food, 0)
    center = rect.center
    pulse = 1.0 + math.sin(elapsed * 7) * 0.16
    glow = pygame.Surface((70, 70), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 54, 156, 42), (35, 35), int(26 * pulse))
    pygame.draw.circle(glow, (255, 145, 208, 34), (35, 35), int(18 * pulse))
    screen.blit(glow, (center[0] - 35, center[1] - 35))
    pygame.draw.circle(screen, PINK, center, int(7 * pulse))
    pygame.draw.circle(screen, (255, 210, 239), (center[0] - 2, center[1] - 2), 2)
    pygame.draw.line(screen, LIME, (center[0], center[1] - 7), (center[0] + 4, center[1] - 11), 2)


def draw_snake():
    glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for index, cell in enumerate(snake):
        rect = cell_rect(cell, 2)
        is_head = index == 0
        if is_head:
            color = LIME
            pygame.draw.circle(glow, (183, 255, 74, 35), rect.center, 17)
        else:
            fade = max(0.35, 1 - index / max(10, len(snake) * 1.3))
            color = (int(45 * fade), int(216 * fade + 20), int(184 * fade + 25))
        pygame.draw.rect(screen, color, rect, border_radius=6)
        pygame.draw.rect(
            screen,
            (235, 255, 185) if is_head else (92, 255, 221),
            rect,
            width=1,
            border_radius=6,
        )
        if is_head:
            eye_x, eye_y = rect.center
            if direction[0] > 0:
                eye_x += 4
            elif direction[0] < 0:
                eye_x -= 4
            if direction[1] > 0:
                eye_y += 4
            elif direction[1] < 0:
                eye_y -= 4
            pygame.draw.circle(screen, (8, 8, 18), (eye_x, eye_y), 2)
    screen.blit(glow, (0, 0))


def draw_monster(elapsed):
    if not monster:
        return
    x, y = monster
    rect = pygame.Rect(
        BOARD_X + x * GRID_SIZE,
        BOARD_Y + y * GRID_SIZE,
        monster_size,
        monster_size,
    )
    jitter = int(math.sin(elapsed * 19) * 2)
    frame = rect.inflate(8, 8)
    pygame.draw.rect(screen, (6, 3, 16), frame, border_radius=8)
    pygame.draw.rect(screen, ORANGE, frame, width=2, border_radius=8)
    screen.blit(monster_image, (rect.x + jitter, rect.y))
    pygame.draw.line(screen, PINK, frame.topleft, frame.bottomright, 2)
    pygame.draw.line(screen, PINK, frame.topright, frame.bottomleft, 2)


def draw_particles():
    for particle in particles:
        alpha = max(0, min(255, int(particle["life"] * 360)))
        particle_surface = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (*PINK, alpha), (6, 6), particle["size"])
        screen.blit(particle_surface, (particle["x"] - 6, particle["y"] - 6))


def draw_card(rect, fill=(29, 22, 52), border=(75, 60, 112), accent=None):
    pygame.draw.rect(screen, (7, 5, 17), rect.move(4, 5), border_radius=13)
    pygame.draw.rect(screen, fill, rect, border_radius=13)
    pygame.draw.rect(screen, border, rect, width=1, border_radius=13)
    if accent:
        pygame.draw.line(
            screen,
            accent,
            (rect.x + 16, rect.y + 14),
            (rect.x + 56, rect.y + 14),
            3,
        )


def draw_panel():
    panel = pygame.Rect(PANEL_X, BOARD_Y, PANEL_WIDTH, BOARD_SIZE)
    pygame.draw.rect(screen, (8, 6, 19), panel.move(5, 7), border_radius=18)
    pygame.draw.rect(screen, PANEL_BG, panel, border_radius=18)
    pygame.draw.rect(screen, (109, 72, 166), panel, width=2, border_radius=18)
    draw_text("LIVE CONTROL DECK", small_font, MUTED, (PANEL_X + 22, BOARD_Y + 22))

    score_card = pygame.Rect(PANEL_X + 20, BOARD_Y + 50, PANEL_WIDTH - 40, 122)
    draw_card(score_card, fill=(31, 34, 54), border=(62, 103, 105), accent=LIME)
    draw_text("CURRENT SCORE", small_font, MUTED, (score_card.x + 18, score_card.y + 18))
    draw_text(f"{score:03d}", score_font, LIME, (score_card.x + 18, score_card.y + 40))
    draw_text(f"BEST {high_score:03d}", body_font, CYAN, (score_card.right - 18, score_card.y + 78), "topright")

    sound_card = pygame.Rect(PANEL_X + 20, BOARD_Y + 188, PANEL_WIDTH - 40, 146)
    draw_card(sound_card, fill=(49, 24, 55), border=(128, 55, 111), accent=PINK)
    draw_text("SOUND SYSTEM", small_font, (255, 166, 216), (sound_card.x + 18, sound_card.y + 18))
    draw_text(f"{len(sound_bank):02d}", score_font, PINK, (sound_card.x + 18, sound_card.y + 38))
    draw_text("TRACKS LOADED", small_font, INK, (sound_card.x + 104, sound_card.y + 58))
    draw_text("EAT + IMPACT = RANDOM", small_font, (255, 194, 224), (sound_card.x + 104, sound_card.y + 80))
    draw_text("VOLUME 75%", body_font, INK, (sound_card.x + 18, sound_card.y + 108))
    volume_bar = pygame.Rect(sound_card.x + 145, sound_card.y + 112, 118, 8)
    pygame.draw.rect(screen, (31, 15, 38), volume_bar, border_radius=4)
    pygame.draw.rect(screen, PINK, volume_bar.inflate(-30, 0), border_radius=4)

    gudo_card = pygame.Rect(PANEL_X + 20, BOARD_Y + 350, PANEL_WIDTH - 40, 144)
    draw_card(gudo_card, fill=(37, 31, 47), border=(125, 96, 62), accent=ORANGE)
    portrait_rect = pygame.Rect(gudo_card.x + 16, gudo_card.y + 26, 92, 92)
    screen.blit(monster_preview, portrait_rect)
    pygame.draw.rect(screen, ORANGE, portrait_rect, width=2, border_radius=8)
    draw_text("GUDO", title_font, ORANGE, (gudo_card.x + 128, gudo_card.y + 36))
    draw_text("DO NOT TOUCH", body_font, INK, (gudo_card.x + 128, gudo_card.y + 77))
    draw_text("SLOW PURSUIT ACTIVE", small_font, PINK, (gudo_card.x + 128, gudo_card.y + 103))

    controls_card = pygame.Rect(PANEL_X + 20, BOARD_Y + 510, PANEL_WIDTH - 40, 104)
    draw_card(controls_card, fill=(27, 23, 49), border=(75, 60, 112), accent=CYAN)
    draw_text("WASD / ARROWS  MOVE", small_font, INK, (controls_card.x + 18, controls_card.y + 22))
    draw_text("SPACE  PAUSE     R  RESTART", small_font, MUTED, (controls_card.x + 18, controls_card.y + 50))
    draw_text("SHIFT  TURBO     ESC  EXIT", small_font, (185, 150, 232), (controls_card.x + 18, controls_card.y + 76))
    draw_text("RANDOM AUDIO PROTOCOL ONLINE", small_font, CYAN, (PANEL_X + 22, BOARD_Y + 620))


def draw_overlay():
    if not (game_over or paused):
        return
    overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
    overlay.fill((8, 5, 22, 188))
    screen.blit(overlay, (BOARD_X, BOARD_Y))
    if game_over:
        draw_text(death_reason, title_font, RED, (BOARD_X + BOARD_SIZE // 2, BOARD_Y + 245), "center")
        draw_text(f"SCORE {score:03d}", body_font, INK, (BOARD_X + BOARD_SIZE // 2, BOARD_Y + 300), "center")
        draw_text("PRESS R TO REBOOT", body_font, LIME, (BOARD_X + BOARD_SIZE // 2, BOARD_Y + 340), "center")
    else:
        draw_text("PAUSED", title_font, CYAN, (BOARD_X + BOARD_SIZE // 2, BOARD_Y + 290), "center")
        draw_text("PRESS SPACE TO RESUME", body_font, INK, (BOARD_X + BOARD_SIZE // 2, BOARD_Y + 337), "center")


reset_game()
running = True
elapsed = 0.0
while running:
    dt = clock.tick(60) / 1000.0
    elapsed += dt
    eat_flash = max(0.0, eat_flash - dt)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_SPACE and not game_over:
                paused = not paused
            elif not game_over and not paused:
                requested_direction = {
                    pygame.K_w: (0, -1),
                    pygame.K_UP: (0, -1),
                    pygame.K_s: (0, 1),
                    pygame.K_DOWN: (0, 1),
                    pygame.K_a: (-1, 0),
                    pygame.K_LEFT: (-1, 0),
                    pygame.K_d: (1, 0),
                    pygame.K_RIGHT: (1, 0),
                }.get(event.key)
                if requested_direction and requested_direction != (-direction[0], -direction[1]):
                    direction = requested_direction

    if not game_over and not paused:
        speed = 0.065 if pygame.key.get_pressed()[pygame.K_LSHIFT] else 0.11
        move_accumulator += dt
        monster_accumulator += dt
        while move_accumulator >= speed:
            move_accumulator -= speed
            move_snake()
            if game_over:
                break
        if monster_accumulator >= 0.42:
            monster_accumulator = 0.0
            move_monster_randomly()
        update_particles(dt)

    draw_background(elapsed)
    draw_board()
    draw_food(elapsed)
    draw_monster(elapsed)
    draw_snake()
    draw_particles()
    draw_panel()
    draw_overlay()
    if eat_flash > 0:
        flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        flash.fill((255, 80, 167, int(eat_flash * 55)))
        screen.blit(flash, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()
