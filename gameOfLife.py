import pygame
import sys

# Stałe
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
FPS = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRID_COLOR = (200, 200, 200)

# Klory
COLOR_NAMES = ["RED", "GREEN", "BLUE", "CYAN", "YELLOW", "MAGENTA"]
COLORS = {
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "CYAN": (0, 255, 255),
    "YELLOW": (255, 255, 0),
    "MAGENTA": (255, 0, 255)
}

# Dostępne wzory startowe
PATTERNS = {
    "EMPTY": [],
    "GLIDER": [(0, 0), (1, 0), (2, 0), (0, 1), (1, 2)],
    "PULSAR": [(2, 4), (2, 5), (2, 6), (4, 2), (5, 2), (6, 2)],
    "ACORN": [(5, 3), (6, 3), (6, 1), (8, 2), (9, 3), (10, 3), (11, 3)],
}

# Ustawienia początkowe
selected_color_name = "RED"
selected_color = COLORS[selected_color_name]
selected_pattern = "EMPTY"
selected_grid_size = GRID_SIZE
simulation_mode = False
start_screen = True
history = []

# Inicjalizacja pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game of Life")
clock = pygame.time.Clock()

# Tworzy pustą siatkę
def create_empty_grid(rows, cols):
    return [[0 for _ in range(cols)] for _ in range(rows)]

# Rysuje siatkę oraz komórki
def draw_grid(grid, grid_size, alive_color):
    screen.fill(WHITE)
    rows, cols = len(grid), len(grid[0])
    for y in range(rows):
        for x in range(cols):
            rect = pygame.Rect(x * grid_size, y * grid_size, grid_size, grid_size)
            if grid[y][x] == 1:
                pygame.draw.rect(screen, alive_color, rect)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

# Umieszcza pattern na środku
def place_pattern(grid, pattern):
    rows, cols = len(grid), len(grid[0])

    if not pattern:
        return

    pattern_width = max(x for x, y in pattern) + 1
    pattern_height = max(y for x, y in pattern) + 1

    offset_x = (cols - pattern_width) // 2
    offset_y = (rows - pattern_height) // 2

    for dx, dy in pattern:
        x = offset_x + dx
        y = offset_y + dy
        if 0 <= x < cols and 0 <= y < rows:
            grid[y][x] = 1

# Logika aktualizacji komórek (reguły gry w życie)
def update_grid(grid):
    rows, cols = len(grid), len(grid[0])
    new_grid = create_empty_grid(rows, cols)
    for y in range(rows):
        for x in range(cols):
            alive_neighbors = sum(
                grid[(y + dy) % rows][(x + dx) % cols]
                for dy in [-1, 0, 1] for dx in [-1, 0, 1]
                if not (dx == 0 and dy == 0)
            )
            if grid[y][x] == 1 and alive_neighbors in [2, 3]:
                new_grid[y][x] = 1
            elif grid[y][x] == 0 and alive_neighbors == 3:
                new_grid[y][x] = 1
    return new_grid

# Rysuje przycisk
def draw_button(text, x, y, width, height, selected=False):
    bg_color = BLACK if selected else WHITE
    text_color = WHITE if selected else BLACK
    pygame.draw.rect(screen, bg_color, (x, y, width, height))
    pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
    font = pygame.font.SysFont('Arial', 20)
    label = font.render(text, True, text_color)
    screen.blit(label, (x + (width - label.get_width()) // 2, y + (height - label.get_height()) // 2))

# Rysuje panel sterujący
def draw_overlay(step_counter):
    panel_x = WIDTH - 200
    panel_y = HEIGHT - 150
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, 190, 140))
    pygame.draw.rect(screen, BLACK, (panel_x, panel_y, 190, 140), 2)
    font = pygame.font.SysFont('Arial', 20)
    step_label = font.render(f"STEP: {step_counter}", True, BLACK)
    screen.blit(step_label, (panel_x + 10, panel_y + 10))
    draw_button("<", panel_x + 10, panel_y + 40, 30, 30)
    draw_button(">", panel_x + 50, panel_y + 40, 30, 30)
    draw_button("CLEAR", panel_x + 100, panel_y + 40, 80, 30)
    draw_button("+", panel_x + 10, panel_y + 80, 30, 30)
    draw_button("-", panel_x + 50, panel_y + 80, 30, 30)
    draw_button("EXP" if not simulation_mode else "SIM", panel_x + 100, panel_y + 80, 80, 30)

# Ekran startowy
def handle_start_screen():
    global selected_color_name, selected_color, selected_pattern, start_screen

    while start_screen:
        screen.fill(WHITE)
        font = pygame.font.SysFont('Arial', 40)
        label = font.render("GAME OF LIFE", True, BLACK)
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 50))

        font_small = pygame.font.SysFont('Arial', 24)
        screen.blit(font_small.render("COLOR OF LIFE:", True, BLACK), (100, 120))

        color_btns = []
        for i, name in enumerate(COLOR_NAMES):
            x, y, w, h = 100 + i * 95, 150, 90, 35
            draw_button(name, x, y, w, h, selected=(name == selected_color_name))
            color_btns.append((name, pygame.Rect(x, y, w, h)))

        screen.blit(font_small.render("STARTING PATTERN:", True, BLACK), (100, 200))

        pattern_btns = []
        for i, pattern in enumerate(PATTERNS.keys()):
            x, y, w, h = 100 + i * 120, 230, 110, 35
            draw_button(pattern, x, y, w, h, selected=(pattern == selected_pattern))
            pattern_btns.append((pattern, pygame.Rect(x, y, w, h)))

        draw_button("START", WIDTH // 2 - 60, 300, 120, 40)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                for name, rect in color_btns:
                    if rect.collidepoint(x, y):
                        selected_color_name = name
                        selected_color = COLORS[name]
                for pattern, rect in pattern_btns:
                    if rect.collidepoint(x, y):
                        selected_pattern = pattern
                if pygame.Rect(WIDTH // 2 - 60, 300, 120, 40).collidepoint(x, y):
                    start_screen = False

# Główna pętla gry
def game_loop():
    global selected_grid_size, history, simulation_mode

    rows = HEIGHT // selected_grid_size
    cols = WIDTH // selected_grid_size
    grid = create_empty_grid(rows, cols)
    history = [grid]

    if selected_pattern != "EMPTY":
        place_pattern(grid, PATTERNS[selected_pattern])

    step_counter = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                grid_x, grid_y = x // selected_grid_size, y // selected_grid_size

                if 0 <= grid_x < cols and 0 <= grid_y < rows:
                    grid[grid_y][grid_x] = 1 - grid[grid_y][grid_x]

                # Obsługa przycisków w panelu
                panel_x, panel_y = WIDTH - 200, HEIGHT - 150
                if panel_x <= x <= panel_x + 190 and panel_y <= y <= panel_y + 140:
                    if panel_x + 10 <= x <= panel_x + 40 and panel_y + 40 <= y <= panel_y + 70:
                        if len(history) > 1:
                            history.pop()
                            grid = history[-1]
                            step_counter -= 1
                    elif panel_x + 50 <= x <= panel_x + 80 and panel_y + 40 <= y <= panel_y + 70:
                        grid = update_grid(grid)
                        history.append(grid)
                        step_counter += 1
                    elif panel_x + 100 <= x <= panel_x + 180 and panel_y + 40 <= y <= panel_y + 70:
                        grid = create_empty_grid(rows, cols)
                        history = [grid]
                        step_counter = 0
                    elif panel_x + 10 <= x <= panel_x + 40 and panel_y + 80 <= y <= panel_y + 110:
                        selected_grid_size = min(selected_grid_size + 10, 40)
                        rows, cols = HEIGHT // selected_grid_size, WIDTH // selected_grid_size
                        grid = create_empty_grid(rows, cols)
                        history = [grid]
                        step_counter = 0
                    elif panel_x + 50 <= x <= panel_x + 80 and panel_y + 80 <= y <= panel_y + 110:
                        selected_grid_size = max(selected_grid_size - 10, 10)
                        rows, cols = HEIGHT // selected_grid_size, WIDTH // selected_grid_size
                        grid = create_empty_grid(rows, cols)
                        history = [grid]
                        step_counter = 0
                    elif panel_x + 100 <= x <= panel_x + 180 and panel_y + 80 <= y <= panel_y + 110:
                        simulation_mode = not simulation_mode

        if simulation_mode:
            grid = update_grid(grid)
            history.append(grid)
            step_counter += 1

        draw_grid(grid, selected_grid_size, selected_color)
        draw_overlay(step_counter)
        pygame.display.flip()
        clock.tick(FPS)

# Uruchomienie gry
def main():
    handle_start_screen()
    game_loop()

if __name__ == "__main__":
    main()

