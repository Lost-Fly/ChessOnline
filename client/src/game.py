import pygame
import sys
from pygame.locals import *

from tools.moves_validator import MovesValidator

BOARD_SIZE = 8

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 36, 0)
GREEN = (0, 255, 0)
FONT_SIZE = 40


def get_cell_size(screen_width, screen_height):
    return min(screen_width, screen_height) // BOARD_SIZE


pygame.display.init()
screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
CELL_SIZE = get_cell_size(screen_width - 100, screen_height - 100)
WINDOW_BORDER = 90
WINDOW_SIZE = (BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE + WINDOW_BORDER)


class ChessGame:
    def __init__(self):
        pygame.init()
        self.message = None
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.board = self.create_board()
        self.moves_validator = MovesValidator(self.board)
        self.selected_piece = None
        self.last_move_time = pygame.time.get_ticks()
        self.player_color = "white"
        self.current_player = "white"
        self.other_player_color = "black" if self.player_color == "white" else "white"
        self.game_over = False
        self.piece_images = {
            0: "assets/black_pawn.png", 1: "assets/black_rook.png", 2: "assets/black_knight.png",
            3: "assets/black_bishop.png", 4: "assets/black_queen.png", 5: "assets/black_king.png",
            6: "assets/white_pawn.png", 7: "assets/white_rook.png", 8: "assets/white_knight.png",
            9: "assets/white_bishop.png", 10: "assets/white_queen.png", 11: "assets/white_king.png"
        }

    @classmethod
    def create_board(cls):
        board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        # Инициализируем шахматные фигуры на доске
        # Пусть 0 - черная пешка, 1 - черная ладья, 2 - черный конь,
        # 3 - черная слон, 4 - черная королева, 5 - черный король,
        # 6 - белая пешка, 7 - белая ладья, 8 - белый конь,
        # 9 - белый слон, 10 - белая королева, 11 - белый король
        for col in range(BOARD_SIZE):
            board[1][col] = 0  # черные пешки
            board[6][col] = 6  # белые пешки

        board[0][0] = board[0][7] = 1  # черные ладьи
        board[0][1] = board[0][6] = 2  # черные кони
        board[0][2] = board[0][5] = 3  # черные слоны
        board[0][3] = 4  # черная королева
        board[0][4] = 5  # черный король

        board[7][0] = board[7][7] = 7  # белые ладьи
        board[7][1] = board[7][6] = 8  # белые кони
        board[7][2] = board[7][5] = 9  # белые слоны
        board[7][3] = 10  # белая королева
        board[7][4] = 11  # белый король

        return board

    def draw_board(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                colorBox = WHITE if (row + col) % 2 == 0 else BLACK
                pygame.draw.rect(self.screen, colorBox, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def draw_pieces(self):

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece is not None:
                    image = pygame.image.load(self.piece_images[piece])
                    image_width, image_height = image.get_size()
                    # image = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
                    image = pygame.transform.scale(image, (image_width * 4, image_height * 4))
                    # Подсветка фигур
                    if self.selected_piece == (row, col):
                        highlight_rect = pygame.Rect(col * CELL_SIZE - 5, row * CELL_SIZE - 5, CELL_SIZE + 10,
                                                     CELL_SIZE + 10)
                        pygame.draw.rect(self.screen, GREEN, highlight_rect, 2)
                    self.screen.blit(image, (col * CELL_SIZE, row * CELL_SIZE))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                row, col = y // CELL_SIZE, x // CELL_SIZE
                self.handle_click(row, col)

    def handle_click(self, row, col):
        if self.selected_piece is None:
            print("Selected - " + str(row) + ", " + str(col))
            if (self.current_player == "black" and self.board[row][col] < 6) or (self.current_player == "white" and self.board[row][col] >= 6):
                self.selected_piece = (row, col)
                self.message = None
            else:
                self.message = "НЕ ВАШ ХОД"
        else:
            start_row, start_col = self.selected_piece
            piece = self.board[start_row][start_col]
            if (row, col) == self.selected_piece:
                self.selected_piece = None
                self.message = None
            else:
                if self.moves_validator.is_valid_move(piece, start_row, start_col, row, col):
                    self.make_move(self.selected_piece, (row, col))
                    self.selected_piece = None
                    self.message = None
                    self.last_move_time = pygame.time.get_ticks()
                    # Смена хода
                    self.current_player = "black" if self.current_player == "white" else "white"
                else:
                    self.message = "Неверная попытка хода!"

    def make_move(self, start_pos, end_pos):

        print("Make Move - " + str(start_pos) + ", " + str(end_pos))

        row_start, col_start = start_pos
        row_end, col_end = end_pos

        piece = self.board[row_start][col_start]
        if piece is not None:
            self.board[row_start][col_start] = None
            self.board[row_end][col_end] = piece

    def draw_text(self):
        if self.message is not None:
            text_surface = self.font.render(self.message, True, BLACK)
            text_width, text_height = text_surface.get_size()
            message_box_width = text_width + 20
            message_box_height = text_height + 10
            message_box_surface = pygame.Surface((message_box_width, message_box_height))
            message_box_surface.fill(WHITE)
            pygame.draw.rect(message_box_surface, RED, (0, 0, message_box_width, message_box_height), 2)
            message_box_surface.blit(text_surface, (10, 5))
            self.screen.blit(message_box_surface, (180, 200))

    def player_selection(self):
        selection_made = False
        player1_color = None
        title_font = pygame.font.Font(None, 60)
        button_font = pygame.font.Font(None, 40)
        while not selection_made:
            self.screen.fill(BLACK)
            title = title_font.render("Выберите цвет первого игрока", True, WHITE)
            button_white = button_font.render("Играть за белых", True, BLACK, WHITE)
            button_black = button_font.render("Играть за чёрных", True, WHITE, BLACK)

            title_rect = title.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 4))
            button_white_rect = button_white.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
            button_black_rect = button_black.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 100))

            self.screen.blit(title, title_rect)
            self.screen.blit(button_white, button_white_rect)
            self.screen.blit(button_black, button_black_rect)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if button_white_rect.collidepoint(x, y):
                        player1_color = "white"
                        selection_made = True
                    elif button_black_rect.collidepoint(x, y):
                        player1_color = "black"
                        selection_made = True

            pygame.display.flip()
            self.clock.tick(30)

        return player1_color

    def show_current_player(self):
        text_surface = self.font.render(f"Current Player: {self.current_player.capitalize()}", True, BLACK)
        text_width, text_height = text_surface.get_size()
        message_box_width = text_width + 20
        message_box_height = text_height + 10
        message_box_surface = pygame.Surface((message_box_width, message_box_height))
        message_box_surface.fill(WHITE)
        pygame.draw.rect(message_box_surface, RED, (0, 0, message_box_width, message_box_height), 2)
        message_box_surface.blit(text_surface, (10, 5))
        self.screen.blit(message_box_surface, ((WINDOW_SIZE[0] - message_box_width), WINDOW_SIZE[1] - 80))

        elapsed_time = (pygame.time.get_ticks() - self.last_move_time) // 1000  # Время в секундах
        timer_text = f"Time since last move: {elapsed_time}s"
        timer_surface = self.font.render(timer_text, True, BLACK)
        timer_box_width = text_width + 50
        timer_box_height = text_height + 10
        timer_box_surface = pygame.Surface((timer_box_width, timer_box_height))
        timer_box_surface.fill(WHITE)
        pygame.draw.rect(timer_box_surface, RED, (0, 0, timer_box_width, timer_box_height), 2)
        timer_box_surface.blit(timer_surface, (10, 5))
        self.screen.blit(timer_box_surface, (0, WINDOW_SIZE[1] - 80))

    def run(self):
        # pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)

        self.player_color = self.player_selection()
        self.other_player_color = "black" if self.player_color == "white" else "white"
        while not self.game_over:
            self.screen.fill(BLACK)
            self.draw_board()
            self.draw_pieces()
            self.handle_events()
            self.draw_text()
            self.show_current_player()
            pygame.display.flip()
            self.clock.tick(30)


if __name__ == "__main__":
    game = ChessGame()
    game.run()
