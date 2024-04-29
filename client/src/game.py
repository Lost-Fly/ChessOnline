import copy

import pygame
import sys
from pygame.locals import *
import random
import time

from client import ChessClient
# from client.src.tools.constants import *
# from client.src.tools.moves_validator import MovesValidator
from tools.constants import *
from tools.moves_validator import MovesValidator

BOARD_SIZE = 8

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 36, 0)
GREEN = (0, 255, 0)
FONT_SIZE = 40
ORANGE = (255, 43, 67)


def get_cell_size(screen_w, screen_h):
    return min(screen_w, screen_h) // BOARD_SIZE


pygame.display.init()
screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
CELL_SIZE = get_cell_size(screen_width - 100, screen_height - 100)
WINDOW_BORDER = 90
WINDOW_SIZE = (BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE + WINDOW_BORDER)


class ChessGame:
    def __init__(self):
        self.bot_mode_difficulty = "simple"
        pygame.init()
        self.bot_mode = False
        self.message = None
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption(GAME_NAME)
        self.clock = pygame.time.Clock()
        self.board = self.create_board()
        self.moves_validator = MovesValidator()
        self.selected_piece = None
        self.last_move_time = pygame.time.get_ticks()
        self.player_color = "white"
        self.current_player = "white"
        self.other_player_color = "black" if self.player_color == "white" else "white"
        self.game_over = False
        self.online_mode = False
        self.client = None  # Reference to the client object
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
            if self.board[row][col] is not None:
                if (self.current_player == "black" and self.board[row][col] < 6) or (
                        self.current_player == "white" and self.board[row][col] >= 6):
                    self.selected_piece = (row, col)
                    self.message = None
                else:
                    self.message = NOT_YOUR_MOVE
        else:
            start_row, start_col = self.selected_piece
            piece = self.board[start_row][start_col]
            if (row, col) == self.selected_piece:
                self.selected_piece = None
                self.message = None
            else:
                if self.moves_validator.is_valid_move(piece, start_row, start_col, row, col, self.board):
                    self.make_move(self.selected_piece, (row, col))
                    # self.client.send_move((self.selected_piece, (row, col)))
                    self.selected_piece = None
                    self.message = None
                    self.last_move_time = pygame.time.get_ticks()
                    # Смена хода
                    self.current_player = "black" if self.current_player == "white" else "white"
                else:
                    self.message = INCORRECT_MOVE

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

    def player_color_selection(self):
        selection_made = False
        player1_color = None
        title_font = pygame.font.Font(None, 60)
        button_font = pygame.font.Font(None, 40)
        while not selection_made:
            self.screen.fill(BLACK)
            title = title_font.render(CHOSE_PLAYER_COLOR, True, WHITE)
            button_white = button_font.render(PLAY_FOR_WHITE, True, BLACK, WHITE)
            button_black = button_font.render(PLAY_FOR_BLACK, True, WHITE, BLACK)

            title_rect = title.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 4))
            button_white_rect = button_white.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 50))
            button_black_rect = button_black.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 50))

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

    def bots_play(self):
        while not self.game_over:
            self.screen.fill(BLACK)
            self.draw_board()
            self.draw_pieces()
            self.bot_make_random_move()
            self.show_current_player()
            self.check_for_check_and_checkmate()
            pygame.display.flip()
            self.clock.tick(1)
            time.sleep(0.5)

            # Смена хода
            self.current_player = "black" if self.current_player == "white" else "white"

    def game_mode_selection(self):
        selection_made = False
        play_with_bot = None
        button_font = pygame.font.Font(None, 40)

        # bot_difficulty = "simple"

        while not selection_made:
            self.screen.fill(BLACK)

            title = button_font.render("Выберите режим игры", True, WHITE)

            button_no_bot = button_font.render("Игра без бота", True, BLACK, WHITE)
            button_two_bot = button_font.render("Игра двух ботов", True, BLACK, WHITE)
            button_simple_bot = button_font.render("Простой бот", True, BLACK, WHITE)
            button_advanced_bot = button_font.render("Продвинутый бот", True, BLACK, WHITE)

            title_rect = title.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 4))

            button_no_bot_rect = button_no_bot.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 100))
            button_two_bot_rect = button_two_bot.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 100))
            button_simple_bot_rect = button_simple_bot.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
            button_advanced_bot_rect = button_advanced_bot.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 50))

            button_online = button_font.render("Игра через сеть", True, BLACK, WHITE)
            button_online_rect = button_online.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 150))
            self.screen.blit(button_online, button_online_rect)

            self.screen.blit(title, title_rect)
            self.screen.blit(button_no_bot, button_no_bot_rect)
            self.screen.blit(button_two_bot, button_two_bot_rect)
            self.screen.blit(button_simple_bot, button_simple_bot_rect)
            self.screen.blit(button_advanced_bot, button_advanced_bot_rect)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if button_no_bot_rect.collidepoint(x, y):
                        play_with_bot = False
                        selection_made = True
                    elif button_simple_bot_rect.collidepoint(x, y):
                        play_with_bot = True
                        self.bot_mode_difficulty = "advanced"
                        selection_made = True
                    elif button_advanced_bot_rect.collidepoint(x, y):
                        play_with_bot = True
                        self.bot_mode_difficulty = "advanced"
                        selection_made = True
                    elif button_two_bot_rect.collidepoint(x, y):
                        play_with_bot = False
                        selection_made = True
                        self.other_player_color = "bot"
                    elif button_online_rect.collidepoint(x, y):
                        self.online_mode = True
                        self.client = ChessClient()
                        self.client.connect_to_server()
                        selection_made = True

            pygame.display.flip()
            self.clock.tick(30)

        return play_with_bot

    def choose_random_black_piece(self, board):
        # Фильтрация списка фигур, чтобы оставить только черные
        black_pieces = [(i, j) for i in range(len(board))
                        for j in range(len(board[i])) if board[i][j] is not None and board[i][j] < 6]

        # Если в списке есть черные фигуры, выбираем из них одну случайно
        if black_pieces:
            return random.choice(black_pieces)
        else:
            return None

    def bot_make_random_move(self):
        # self.clock.tick(1)
        # time.sleep(1)
        # Получаем список всех возможных ходов
        all_moves = self.moves_validator.get_all_possible_moves(self.current_player, self.board)
        # Если есть ходы, случайным образом выбираем один ход из списка
        if all_moves:
            start_pos, end_pos = random.choice(all_moves)
            self.make_move(start_pos, end_pos)
        else:
            # Если ходов нет - это пат или мат
            self.game_over = True
            self.message = f"МАТ! {self.other_player_color.capitalize()} wins!"

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
        timer_box_width = text_width + 100
        timer_box_height = text_height + 10
        timer_box_surface = pygame.Surface((timer_box_width, timer_box_height))
        timer_box_surface.fill(WHITE)
        pygame.draw.rect(timer_box_surface, RED, (0, 0, timer_box_width, timer_box_height), 2)
        timer_box_surface.blit(timer_surface, (10, 5))
        self.screen.blit(timer_box_surface, (0, WINDOW_SIZE[1] - 80))

    def check_for_check_and_checkmate(self):
        # Сначала определяем, находится ли какой-либо из королей под шахом
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece == 5 or piece == 11:  # Индексы королей
                    is_check = self.moves_validator.is_check(row, col, self.board)
                    if is_check:
                        # Проверяем, есть ли возможные ходы для короля, если нет, то это мат
                        is_checkmate = self.moves_validator.is_checkmate(row, col, self.board)
                        print(is_checkmate)
                        self.highlight_check_or_checkmate(row, col, is_checkmate)
                        if is_checkmate or (is_check and self.player_color == self.current_player):
                            self.game_over = True
                            winner = "White" if self.current_player == "black" else "Black"
                            self.message = f"МАТ! {winner} wins!"

    def highlight_check_or_checkmate(self, row, col, is_checkmate):
        color = RED if is_checkmate else ORANGE
        highlight_rect = pygame.Rect(col * CELL_SIZE - 5, row * CELL_SIZE - 5, CELL_SIZE + 10, CELL_SIZE + 10)
        pygame.draw.rect(self.screen, color, highlight_rect, 2)

    def evaluate_board(self, board):
        piece_value = {
            0: -10, 1: -50, 2: -30, 3: -30, 4: -90, 5: -900,  # Black pieces values
            6: 10, 7: 50, 8: 30, 9: 30, 10: 90, 11: 900  # White pieces values
        }
        value = 0
        for row in board:
            for piece in row:
                if piece is not None:
                    value += piece_value[piece]
        return value

    def simulate_move(self, board, start_pos, end_pos):
        piece = board[start_pos[0]][start_pos[1]]
        board[start_pos[0]][start_pos[1]] = None
        board[end_pos[0]][end_pos[1]] = piece

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.game_over:
            return self.evaluate_board(board)

        if maximizing_player:
            max_eval = -float('inf')
            all_moves = self.moves_validator.get_all_possible_moves('white', self.board)
            for move in all_moves:
                new_board = copy.deepcopy(board)
                self.simulate_move(new_board, move[0], move[1])
                eval_ = self.minimax(new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_)
                alpha = max(alpha, eval_)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            all_moves = self.moves_validator.get_all_possible_moves('black', self.board)
            for move in all_moves:
                new_board = copy.deepcopy(board)
                self.simulate_move(new_board, move[0], move[1])
                eval_ = self.minimax(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_)
                beta = min(beta, eval_)
                if beta <= alpha:
                    break
            return min_eval

    def advanced_bot_move(self):
        best_score = -float('inf')
        best_move = None
        all_possible_moves = self.moves_validator.get_all_possible_moves(self.current_player, self.board)

        for move in all_possible_moves:
            cloned_board = copy.deepcopy(self.board)
            self.simulate_move(cloned_board, move[0], move[1])
            score = self.minimax(cloned_board, depth=3, alpha=-float('inf'), beta=float('inf'), maximizing_player=True)
            if score > best_score:
                best_score = score
                best_move = move

        if best_move:
            self.make_move(best_move[0], best_move[1])

    def online_mode_logic(self):
        self.message = "Waiting for opponent's move..."

        # Получаем ход с сервера
        opponent_move = self.client.receive_move()
        self.message = None
        if opponent_move:
            # Применяем полученный ход к нашей доске
            start_pos, end_pos = opponent_move['start'], opponent_move['end']
            self.make_move(start_pos, end_pos)
            self.current_player = self.player_color
        self.message = None

    def run(self):
        # pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)

        self.bot_mode = self.game_mode_selection()
        print(self.bot_mode)
        self.player_color = self.player_color_selection()

        # Вариант режима игры - играют только боты.
        print(self.other_player_color)
        play_bots_only = self.other_player_color == "bot"

        # Если выбран режим только боты, то запускаем соответствующий режим
        if play_bots_only:
            self.bots_play()
        else:
            self.other_player_color = "black" if self.player_color == "white" else "white"
            while True:
                self.screen.fill(BLACK)
                self.draw_board()
                self.draw_pieces()
                self.handle_events()
                self.draw_text()
                if self.online_mode:
                    if self.current_player == self.player_color:
                        # Обрабатываем клик и отправляем ход если это наш ход
                        self.handle_events()
                    else:
                        # Получаем ход от противника
                        self.online_mode_logic()
                        # Проверка на окончание игры и отображение сообщений
                    self.check_for_check_and_checkmate()
                    self.show_current_player()
                else:
                    if self.bot_mode and self.current_player == self.other_player_color:
                        if self.bot_mode_difficulty == "simple":
                            self.bot_make_random_move()
                        elif self.bot_mode_difficulty == "advanced":
                            self.advanced_bot_move()
                        self.current_player = self.player_color
                        # time.sleep(3)

                self.show_current_player()
                self.check_for_check_and_checkmate()
                pygame.display.flip()
                self.clock.tick(30)


if __name__ == "__main__":
    game = ChessGame()
    game.run()
