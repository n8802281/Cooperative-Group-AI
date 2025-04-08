import pygame
import os

GRID_SIZE = 30
CELL_SIZE = 20
UI_HEIGHT = 50
GAME_SPEED = 500

COLORS = {
    "empty": (200, 200, 200),
    "wall": (0, 0, 0),
    "mud": (139, 69, 19),
    "water": (30, 144, 255),
    "player": (0, 255, 0),
    "chaser": (255, 0, 0),
    "helper": (255, 165, 0),
    "blocker": (128, 0, 128),
    "chaser_delayed": (128, 0, 0),
    "helper_delayed": (128, 83, 0),
    "blocker_delayed": (64, 0, 64)
}
MOVES = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0)
}
MODIFY_KEYS = {
    pygame.K_w: (0, -1),
    pygame.K_s: (0, 1),
    pygame.K_a: (-1, 0),
    pygame.K_d: (1, 0)
}

def init_pygame():
    pygame.font.init()
    font = pygame.font.Font(None, 36)
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    pygame.init()
    screen = pygame.display.set_mode((GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE + UI_HEIGHT))
    return screen, font

SCREEN, FONT = init_pygame()

def handle_events():
    last_move = None
    modify_skill = False
    last_modify_move = None
    clear_skill = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, last_move, modify_skill, last_modify_move, clear_skill
        elif event.type == pygame.KEYDOWN and event.key in MOVES:
            last_move = event.key
        elif event.type == pygame.KEYDOWN and event.key in MODIFY_KEYS:
            modify_skill = True
            last_modify_move = event.key
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            clear_skill = True

    return True, last_move, modify_skill, last_modify_move, clear_skill

def update_screen(grid, player_pos, npc_positions, npc_clusters, enemy_delay, modify_cooldown, clear_cooldown, point, remaining_turns):
    draw(grid, player_pos, npc_positions, npc_clusters, enemy_delay, modify_cooldown, clear_cooldown, point, remaining_turns)
    pygame.display.flip()
    pygame.time.delay(GAME_SPEED)

def draw(grid, player_pos, npc_positions, npc_clusters, enemy_delay, modify_cooldown, clear_cooldown, point, remaining_turns):
    SCREEN.fill((255, 255, 255))
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            pygame.draw.rect(SCREEN, COLORS[grid[x, y]], (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(SCREEN, COLORS["player"], (player_pos[0] * CELL_SIZE, player_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for i, npc in enumerate(npc_positions):
        if npc in npc_clusters["chaser"]:
            color = COLORS["chaser_delayed"] if enemy_delay[i] > 0 else COLORS["chaser"]
        elif npc in npc_clusters["helper"]:
            color = COLORS["helper_delayed"] if enemy_delay[i] > 0 else COLORS["helper"]
        elif npc in npc_clusters["blocker"]:
            color = COLORS["blocker_delayed"] if enemy_delay[i] > 0 else COLORS["blocker"]
        else:
            color = COLORS["chaser_delayed"] if enemy_delay[i] > 0 else COLORS["chaser"]
        pygame.draw.rect(SCREEN, color, (npc[0] * CELL_SIZE, npc[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(SCREEN, (255, 0, 0), (10, GRID_SIZE * CELL_SIZE + 10, 120, 40), 2)
    pygame.draw.rect(SCREEN, (255, 0, 0), (140, GRID_SIZE * CELL_SIZE + 10, 120, 40), 2)
    SCREEN.blit(FONT.render(f"Mud: {modify_cooldown}", True, (255, 0, 0)), (20, GRID_SIZE * CELL_SIZE + 20))
    SCREEN.blit(FONT.render(f"Clear: {clear_cooldown}", True, (255, 0, 0)), (150, GRID_SIZE * CELL_SIZE + 20))
    SCREEN.blit(FONT.render(f"POINT: {point}", True, (255, 0, 0)), (270, GRID_SIZE * CELL_SIZE + 20))
    SCREEN.blit(FONT.render(f"Turns: {remaining_turns}", True, (255, 0, 0)), (450, GRID_SIZE * CELL_SIZE + 20))

def show_game_over_screen(score):
    game_over = True
    while game_over:
        SCREEN.fill((0, 0, 0))
        game_over_text = FONT.render(f"GAMEOVER", True, (255, 0, 0))
        score_text = FONT.render(f"SCORE: {score}", True, (255, 255, 255))
        retry_text = FONT.render("Y: RETRY / N: EXIT", True, (255, 255, 255))

        SCREEN.blit(game_over_text, (GRID_SIZE * CELL_SIZE // 2 - 80, GRID_SIZE * CELL_SIZE // 2 - 60))
        SCREEN.blit(score_text, (GRID_SIZE * CELL_SIZE // 2 - 50, GRID_SIZE * CELL_SIZE // 2 - 20))
        SCREEN.blit(retry_text, (GRID_SIZE * CELL_SIZE // 2 - 100, GRID_SIZE * CELL_SIZE // 2 + 40))

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_n:
                    return False

def quit_game():
    pygame.quit()
