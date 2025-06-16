import pygame
import random
import mysql.connector
import sys

pygame.font.init()
pygame.init()

# MySQL Config
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="tetris_scores"
)
cursor = db.cursor()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
PLAY_WIDTH = 300  # 10 cột * 30px
PLAY_HEIGHT = 600  # 20 hàng * 30px
BLOCK_SIZE = 30
TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT

# Colors
WHITE = (255, 255, 255)
GRID_COLOR = (128, 128, 128)
RED = (255, 0, 0)  
LIGHT_YELLOW = (255, 255, 153)     
LIME_GREEN = (50, 205, 50)
BRIGHT_PURPLE = (186, 85, 211)
BRIGHT_ORANGE = (255, 140, 0)
BRIGHT_BLUE = (0, 191, 255)
BRIGHT_RED = (255, 69, 0)
LIGHT_PINK = (255, 182, 193)
DEEP_PURPLE = (148, 0, 211)
LIGHT_ORANGE = (255, 160, 122)   
NEON_DEEP_RED = (255, 0, 127)    
NEON_BRIGHT_GREEN = (0, 255, 127) 
NEON_GOLD = (255, 215, 0)         
ULTRA_CYAN = (0, 255, 255)    


# Load background images
background_images = [
    pygame.transform.scale(pygame.image.load("1.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    pygame.transform.scale(pygame.image.load("2.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    pygame.transform.scale(pygame.image.load("3.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    pygame.transform.scale(pygame.image.load("4.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT))
]

grid_backgrounds = [
    pygame.transform.scale(pygame.image.load("5.jpg"), (PLAY_WIDTH, PLAY_HEIGHT)),
    pygame.transform.scale(pygame.image.load("6.jpg"), (PLAY_WIDTH, PLAY_HEIGHT)),
    pygame.transform.scale(pygame.image.load("7.jpg"), (PLAY_WIDTH, PLAY_HEIGHT))
]

current_background = 0  # Chỉ số ảnh nền hiện tại
current_grid_backgrounds = 0  # Chỉ số ảnh nền lưới hiện tại

# Shapes
S = [['.....', '.....', '..00.', '.00..', '.....'],
     ['.....', '..0..', '..00.', '...0.', '.....']]
Z = [['.....', '.....', '.00..', '..00.', '.....'],
     ['.....', '..0..', '.00..', '.0...', '.....']]
I = [['..0..', '..0..', '..0..', '..0..', '.....'],
     ['.....', '0000.', '.....', '.....', '.....']]
O = [['.....', '.....', '.00..', '.00..', '.....']]
J = [['.....', '.0...', '.000.', '.....', '.....'],
     ['.....', '..00.', '..0..', '..0..', '.....'],
     ['.....', '.....', '.000.', '...0.', '.....'],
     ['.....', '..0..', '..0..', '.00..', '.....']]
L = [['.....', '...0.', '.000.', '.....', '.....'],
     ['.....', '..0..', '..0..', '..00.', '.....'],
     ['.....', '.....', '.000.', '.0...', '.....'],
     ['.....', '.00..', '..0..', '..0..', '.....']]
T = [['.....', '..0..', '.000.', '.....', '.....'],
     ['.....', '..0..', '..00.', '..0..', '.....'],
     ['.....', '.....', '.000.', '..0..', '.....'],
     ['.....', '..0..', '.00..', '..0..', '.....']]

SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = [(0, 255, 0), (255, 0, 0), (0, 255, 255),
                (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

def create_grid(locked_pos={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j, i)]
                grid[i][j] = c
    return grid

def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)
    return positions

def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]
    formatted = convert_shape_format(shape)
    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True

def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    return Piece(5, 0, random.choice(SHAPES))

def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 36)
    label = font.render('Next Shape', 1, BRIGHT_ORANGE)
    sx = TOP_LEFT_X + PLAY_WIDTH + 35
    sy = TOP_LEFT_Y + 120  # Vị trí của "Next Shape"

    # Lấy định dạng của khối
    format = shape.shape[shape.rotation % len(shape.shape)]

    # Tính kích thước khu vực cần vẽ (dựa trên kích thước của khối)
    shape_width = len(format[0]) * BLOCK_SIZE  # Chiều rộng của khối
    shape_height = len(format) * BLOCK_SIZE    # Chiều cao của khối

    # Vẽ các ô của khối "Next Shape" trước
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j * BLOCK_SIZE, sy + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    # Vẽ nhãn "Next Shape"
    surface.blit(label, (sx - 10, sy - 60))

def draw_grid(surface, grid):
    sx = TOP_LEFT_X
    sy = TOP_LEFT_Y
    
    # Vẽ hình ảnh nền cho lưới
    surface.blit(grid_backgrounds[2], (sx, sy))
    
    # Vẽ các ô (chỉ vẽ khối có màu, bỏ qua ô trống)
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] != (0, 0, 0):  # Chỉ vẽ nếu không phải màu đen
                pygame.draw.rect(surface, grid[i][j], (sx + j * BLOCK_SIZE, sy + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    # Vẽ các đường lưới
    for i in range(len(grid) + 1):
        pygame.draw.line(surface, GRID_COLOR, (sx, sy + i * BLOCK_SIZE), (sx + PLAY_WIDTH, sy + i * BLOCK_SIZE))
    for j in range(len(grid[0]) + 1):
        pygame.draw.line(surface, GRID_COLOR, (sx + j * BLOCK_SIZE, sy), (sx + j * BLOCK_SIZE, sy + PLAY_HEIGHT))

    # Vẽ viền đỏ xung quanh lưới
    pygame.draw.rect(surface, RED, (sx, sy, PLAY_WIDTH, PLAY_HEIGHT), 2)

def draw_text_middle(surface, text, size, color, y_offset=0):
    font = pygame.font.SysFont("calibri", size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), TOP_LEFT_Y + PLAY_HEIGHT / 2 - label.get_height() / 2 + y_offset))

def draw_text(win, text, x, y, size, color):
    font = pygame.font.SysFont('calibri', size, bold=True)  
    text_surface = font.render(text, True, color)
    win.blit(text_surface, (x - text_surface.get_width() // 2, y - text_surface.get_height() // 2))

def draw_button(win, text, x, y, width, height, color):
    pygame.draw.rect(win, color, (x, y, width, height))
    draw_text(win, text, x + width // 2, y + height // 2, 30, WHITE)

def draw_window(surface, grid, score=0, player_name=""):
    surface.blit(background_images[2], (0, 0))
    font = pygame.font.SysFont('Open Sans', 52)
    label = font.render('TETRIS', True, RED)
    surface.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, 30))

    font = pygame.font.SysFont('comicsans', 36)

    # Vị trí "Player" căn lề trái và "Score" căn lề phải
    player_label = font.render("Player:", True, LIME_GREEN)
    score_label = font.render(f'Score: {score}', True, LIME_GREEN)
    surface.blit(player_label, (TOP_LEFT_X - 180, TOP_LEFT_Y + PLAY_HEIGHT - 180))  # Kéo "Player" qua trái
    surface.blit(score_label, (TOP_LEFT_X + PLAY_WIDTH + 50, TOP_LEFT_Y + PLAY_HEIGHT - 180))

    # Giới hạn chiều rộng cho tên người chơi
    max_width = 200  # Chiều rộng tối đa cho tên người chơi, cần phải đủ để không vượt qua khu vực game

    # Xử lý tên người chơi xuống dòng nếu quá dài
    lines = []
    words = player_name.split(' ')
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        test_surface = font.render(test_line, True, BRIGHT_PURPLE)
        if test_surface.get_width() <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    lines.append(current_line)  # Đưa dòng cuối vào

    # Vẽ tên người chơi trên các dòng, mỗi dòng cách nhau 30px
    player_y_offset = TOP_LEFT_Y + PLAY_HEIGHT - 140  # Vị trí của "Player"
    max_player_y_position = TOP_LEFT_Y + PLAY_HEIGHT - 30  # Vị trí tối đa không được vượt qua khu vực game
    for line in lines:
        player_name_label = font.render(f"{line}", True, BRIGHT_PURPLE)
        surface.blit(player_name_label, (TOP_LEFT_X - 180, player_y_offset))  # Kéo qua trái một chút
        player_y_offset += 30  # Thêm khoảng cách giữa các dòng tên
        
        # Kiểm tra nếu tên người chơi vượt quá khu vực game thì dừng lại
        if player_y_offset + 30 > max_player_y_position:
            break

    # Vẽ grid game
    draw_grid(surface, grid)

def get_high_score():
    cursor.execute("SELECT MAX(score) FROM scores")
    result = cursor.fetchone()
    return result[0] if result[0] else 0

def save_score(name, score):
    cursor.execute("INSERT INTO scores (name, score) VALUES (%s, %s)", (name, score))
    db.commit()

def menu_selection(win):
    run = True
    while run:
        win.blit(background_images[0], (0, 0))

        # Vẽ tiêu đề và các nút
        draw_text(win, "TETRIS", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 250, 80, RED)

        # Vẽ các nút với vị trí và kích thước cụ thể
        play_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50)
        leaderboard_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10, 200, 50)
        exit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50)

        draw_button(win, "Chơi ngay", play_button.x, play_button.y, play_button.width, play_button.height, NEON_GOLD)
        draw_button(win, "Bảng xếp hạng", leaderboard_button.x, leaderboard_button.y, leaderboard_button.width, leaderboard_button.height, NEON_BRIGHT_GREEN)
        draw_button(win, "Thoát", exit_button.x, exit_button.y, exit_button.width, exit_button.height, BRIGHT_PURPLE)

        pygame.display.update()

        # Lắng nghe sự kiện chuột
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                # Kiểm tra chuột nhấn vào các nút
                if play_button.collidepoint(mouse_x, mouse_y):
                    enter_name_screen(win)
                elif leaderboard_button.collidepoint(mouse_x, mouse_y):
                    show_leaderboard(win)
                elif exit_button.collidepoint(mouse_x, mouse_y):
                    run = False

    pygame.quit()
    sys.exit()

def enter_name_screen(win):
    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50)
    color_inactive = BRIGHT_RED		     # Thay NEON_DEEP_RED
    color_active = BRIGHT_RED	        # Thay NEON_BRIGHT_GREEN
    color = color_inactive
    active = False
    text = ''
    font = pygame.font.SysFont('Open Sans', 48)

    while True:
        win.blit(background_images[1], (0, 0))
        draw_text(win, "Enter your name:", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100, 30,DEEP_PURPLE)

        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        win.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(win, LIGHT_YELLOW, input_box, 5)  # Đổi thành NEON_GOLD và tăng độ dày viền lên 3
        draw_button(win, "Bắt đầu", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60, 200, 50, NEON_DEEP_RED)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive

                if SCREEN_WIDTH // 2 - 100 <= event.pos[0] <= SCREEN_WIDTH // 2 + 100 and SCREEN_HEIGHT // 2 + 60 <= event.pos[1] <= SCREEN_HEIGHT // 2 + 110:
                    if text:
                        main_game(text)
                        return

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if text:
                            main_game(text)
                            return
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

def show_leaderboard(surface):
    surface.blit(background_images[3], (0, 0))  # Thay dòng này
    font = pygame.font.SysFont('Source Code Pro', 62)
    title = font.render('BXH - Top 10', True, ULTRA_CYAN)
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

    cursor.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 10")
    results = cursor.fetchall()
    font = pygame.font.SysFont('Inconsolata', 42)

    for i, (name, score) in enumerate(results):
        label = font.render(f"{i+1}. {name} - {score}", True, LIGHT_YELLOW	)
        surface.blit(label, (70, 140 + i * 45))

    # Draw "Back to Menu" button
    draw_button(surface, "Trở lại Menu", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50, LIGHT_ORANGE)

    pygame.display.update()

    # Event loop for "Back to Menu" button
    back_to_menu = False
    while not back_to_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if SCREEN_WIDTH // 2 - 100 <= event.pos[0] <= SCREEN_WIDTH // 2 + 100 and SCREEN_HEIGHT - 100 <= event.pos[1] <= SCREEN_HEIGHT - 50:
                    back_to_menu = True
                    menu_selection(surface)  # Go back to main menu
                    return

def main_game(name):
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    score = 0

    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    high_score = get_high_score()

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)

        shape_pos = convert_shape_format(current_piece)
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            lines_cleared = clear_rows(grid, locked_positions)
            if lines_cleared == 1:
                score += 40
            elif lines_cleared == 2:
                score += 100
            elif lines_cleared == 3:
                score += 300
            elif lines_cleared == 4:
                score += 1200

        draw_window(win, grid, score, name)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        # Phần sửa lỗi: Khi trò chơi kết thúc
        if check_lost(locked_positions):
            draw_text_middle(win, "GAME OVER", 56, BRIGHT_RED)
            draw_button(win, "Trở lại Menu", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 150, 200, 50, LIGHT_ORANGE)
            pygame.display.update()

            # Lưu điểm ngay khi trò chơi kết thúc, trước khi chờ nhấn nút
            save_score(name, score)
            print(f"Đã lưu: {name} - {score}")  # Thêm dòng này để debug, kiểm tra xem điểm có được lưu không

            waiting_for_click = True
            while waiting_for_click:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if SCREEN_WIDTH // 2 - 100 <= event.pos[0] <= SCREEN_WIDTH // 2 + 100 and SCREEN_HEIGHT // 2 + 150 <= event.pos[1] <= SCREEN_HEIGHT // 2 + 200:
                            waiting_for_click = False
                            menu_selection(win)

            run = False
            
def main():
    pygame.init()
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Cửa sổ game
    menu_selection(win)  # Gọi menu chính

if __name__ == "__main__":
    main()