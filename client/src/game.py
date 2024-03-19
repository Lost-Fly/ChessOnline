import pygame
import sys
from pygame.locals import *


BOARD_SIZE = 8
CELL_SIZE = 80
WINDOW_SIZE = (BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE)


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class ChessGame:
    def __init__(self, player_color):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.board = self.create_board()
        self.selected_piece = None
        self.game_over = False
        self.player_color = player_color

    def create_board(self):
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
                color = WHITE if (row + col) % 2 == 0 else BLACK
                pygame.draw.rect(self.screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def draw_pieces(self):
        piece_images = {
            0: "assets/black_pawn.png", 1: "assets/black_rook.png", 2: "assets/black_knight.png",
            3: "assets/black_bishop.png", 4: "assets/black_queen.png", 5: "assets/black_king.png",
            6: "assets/white_pawn.png", 7: "assets/white_rook.png", 8: "assets/white_knight.png",
            9: "assets/white_bishop.png", 10: "assets/white_queen.png", 11: "assets/white_king.png"
        }
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece is not None:
                    image = pygame.image.load(piece_images[piece])
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
            # Если нажата пустая клетка или фигура не вашего цвета, ничего не делаем
            # piece = self.board[row][col]
            # if piece is None or (piece < 6 and self.player_color == "white") or (piece >= 6 and self.player_color == "black"):
            #     return
            # self.selected_piece = (row, col)
            pass
        else:
            # Если уже выбрана фигура, попробуем сделать ход
            move = self.board[row][col]
            if move is not None and ((move < 6 and self.player_color == "white") or (move >= 6 and self.player_color == "black")):
                # Если выбрана фигура того же цвета, сбросим выбор
                self.selected_piece = None
            else:
                # Выполним ход
                self.make_move(self.selected_piece, (row, col))
                self.selected_piece = None


    def make_move(self, start_pos, end_pos):
        row_start, col_start = start_pos
        row_end, col_end = end_pos


    def run(self):
        while not self.game_over:
            self.screen.fill(BLACK)
            self.draw_board()
            self.draw_pieces()
            self.handle_events()
            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    player_color = input("Enter your color (white or black): ").lower()
    game = ChessGame(player_color)
    game.run()