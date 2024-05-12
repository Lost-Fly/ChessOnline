import pygame
import sys
from pygame.locals import *
import random
import time

from client import ChessClient
from advanced_bot import AdvancedBot
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
CELL_SIZE = get_cell_size(screen_width - 200, screen_height - 200)
WINDOW_BORDER = 120
WINDOW_BORDER_RIGHT = 100
WINDOW_SIZE = (BOARD_SIZE * CELL_SIZE + WINDOW_BORDER_RIGHT, BOARD_SIZE * CELL_SIZE + WINDOW_BORDER)


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
        self.client = None
        self.advanced_bot = AdvancedBot(self.moves_validator)
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
        self.screen.fill(BLACK)
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                colorBox = WHITE if (row + col) % 2 == 0 else BLACK
                pygame.draw.rect(self.screen, colorBox, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        self.draw_labels()

    def draw_pieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece is not None:
                    image = pygame.image.load(self.piece_images[piece])
                    image_width, image_height = image.get_size()
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
            # print("Selected - " + str(row) + ", " + str(col))
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
                # if self.moves_validator.is_valid_move(piece, start_row, start_col, row, col, self.board) \
                #         and self.moves_validator.is_valid_move_in_check(start_row, start_col, row, col, self.board):

                all_mvs = self.moves_validator.get_all_possible_moves(self.current_player, self.board)
                if all_mvs.count(((start_row, start_col), (row, col))) > 0:
                    self.make_move(self.selected_piece, (row, col))
                    if self.online_mode:
                        self.client.send_move((self.selected_piece, (row, col)))
                    self.selected_piece = None
                    self.message = None
                    self.last_move_time = pygame.time.get_ticks()
                    # Смена хода
                    self.current_player = "black" if self.current_player == "white" else "white"
                else:
                    self.message = INCORRECT_MOVE
                self.screen.fill(BLACK)
                self.draw_board()
                self.draw_pieces()
                self.draw_text()
                pygame.display.flip()

    def make_move(self, start_pos, end_pos):

        # print("Make Move - " + str(start_pos) + ", " + str(end_pos))
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
            pygame.draw.rect(message_box_surface, RED, (0, 0,
                                                        message_box_width, message_box_height), 2)
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
            button_white_rect = button_white. \
                get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 50))
            button_black_rect = button_black. \
                get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 50))

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

        while not selection_made:
            self.screen.fill(BLACK)

            title = button_font.render("Выберите режим игры", True, WHITE)

            button_no_bot = button_font.render("Игра без бота", True, BLACK, WHITE)
            button_two_bot = button_font.render("Игра двух ботов", True, BLACK, WHITE)
            button_simple_bot = button_font.render("Простой бот", True, BLACK, WHITE)
            button_advanced_bot = button_font.render("Продвинутый бот", True, BLACK, WHITE)

            title_rect = title.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 4))

            button_no_bot_rect = button_no_bot. \
                get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 100))
            button_two_bot_rect = button_two_bot. \
                get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 100))
            button_simple_bot_rect = button_simple_bot. \
                get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
            button_advanced_bot_rect = button_advanced_bot.get_rect(
                center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 50))

            button_online = button_font.render("Игра через сеть", True, BLACK, WHITE)
            button_online_rect = button_online. \
                get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 150))
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
                        selection_made = True

            pygame.display.flip()
            self.clock.tick(30)

        return play_with_bot

    def bot_make_random_move(self):
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
        text_surface = self.font.render(f"Current Player: "
                                        f"{self.current_player.capitalize()}", True, BLACK)
        text_width, text_height = text_surface.get_size()
        message_box_width = text_width + 60
        message_box_height = text_height + 10
        message_box_surface = pygame.Surface((message_box_width, message_box_height))
        message_box_surface.fill(WHITE)
        pygame.draw.rect(message_box_surface, RED, (0, 0,
                                                    message_box_width, message_box_height), 2)
        message_box_surface.blit(text_surface, (10, 5))
        self.screen.blit(message_box_surface, ((WINDOW_SIZE[0] - message_box_width),
                                               WINDOW_SIZE[1] - 50))

        elapsed_time = (pygame.time.get_ticks() - self.last_move_time) // 1000
        timer_text = f"Time since last move: {elapsed_time}s"
        timer_surface = self.font.render(timer_text, True, BLACK)
        timer_box_width = text_width + 100
        timer_box_height = text_height + 10
        timer_box_surface = pygame.Surface((timer_box_width, timer_box_height))
        timer_box_surface.fill(WHITE)
        pygame.draw.rect(timer_box_surface, RED, (0, 0, timer_box_width, timer_box_height), 2)
        timer_box_surface.blit(timer_surface, (10, 5))
        self.screen.blit(timer_box_surface, (0, WINDOW_SIZE[1] - 50))

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
                        # print("IS CHECKMATE " + str(is_checkmate))
                        self.highlight_check_or_checkmate(row, col, is_checkmate)
                        if is_checkmate:
                            self.game_over = True
                            winner = "White" if self.current_player == "black" else "Black"
                            self.message = f"МАТ! {winner} wins!"
                    else:
                        # Проверяем на ПАТ
                        is_stalemate = self.moves_validator.is_stalemate(self.current_player, self.board)
                        if is_stalemate:
                            self.game_over = True
                            self.message = f"STALEMATE! It's a draw!"

    def draw_labels(self):
        label_font = pygame.font.Font(None, FONT_SIZE // 2)
        label_offset = CELL_SIZE // 2
        for row in range(BOARD_SIZE):
            # Отображаем цифры для строк
            label = label_font.render(str(8 - row), True, WHITE)
            label_rect = \
                label.get_rect(midright=(WINDOW_SIZE[0] - label_offset * 2,
                                         row * CELL_SIZE + label_offset))
            self.screen.blit(label, label_rect)

        for col in range(BOARD_SIZE):
            # Отображаем буквы для столбцов
            label = label_font.render(chr(ord('a') + col), True, WHITE)
            label_rect = label.get_rect(
                midtop=(col * CELL_SIZE + label_offset,
                        WINDOW_SIZE[1] - WINDOW_BORDER + label_offset // 2))
            self.screen.blit(label, label_rect)

    def highlight_check_or_checkmate(self, row, col, is_checkmate):
        color = RED if is_checkmate else ORANGE
        highlight_rect = pygame.Rect(col * CELL_SIZE - 5,
                                     row * CELL_SIZE - 5, CELL_SIZE + 10, CELL_SIZE + 10)
        pygame.draw.rect(self.screen, color, highlight_rect, 2)

    def online_mode_logic(self):
        self.message = "Waiting for opponent's move..."
        self.draw_text()
        # print("Waiting for opponent's move...")

        # Получаем ход с сервера
        opponent_move = self.client.receive_move()
        # print("OPPONENT MOVE" +
        #       str(opponent_move))
        self.message = None
        if opponent_move:
            # Применяем полученный ход к нашей доске
            start_pos, end_pos = opponent_move[0], opponent_move[1]
            self.make_move(start_pos, end_pos)
            self.current_player = self.player_color
        self.message = None

    def get_online_color(self):
        # print("BEF GET COLOR")
        color_data = self.client.receive_move()
        # print("GET  ON COLOR " + str(color_data))
        # Проверка, что полученные данные не None и являются строкой
        if color_data and isinstance(color_data, str):
            # print("SET PL COLOR")
            self.player_color = color_data
            return color_data
        else:
            # Если данные не получены или некорректны,
            # возвращаем None или выбрасываем исключение
            # print("Failed to receive color data.")
            return None

    def run(self):

        self.bot_mode = self.game_mode_selection()
        # print(self.bot_mode)

        self.client = ChessClient()

        # print("ONLINE MODE " + str(self.online_mode))
        if self.online_mode:

            # print("bef con")
            self.client.connect_to_server()
            # print("after con")

            if not self.get_online_color():
                # print("Unable to start the game due to connection issues.")
                return
        else:
            self.player_color = self.player_color_selection()

        # Вариант режима игры - играют только боты.

        play_bots_only = self.other_player_color == "bot"

        # Если выбран режим только боты, то запускаем соответствующий режим
        if play_bots_only:
            self.bots_play()
        else:

            self.other_player_color = "black" if self.player_color == "white" else "white"

            # print("OTHER PL COLOR" + self.other_player_color)
            while True:
                self.screen.fill(BLACK)
                self.draw_board()
                self.draw_pieces()
                self.draw_text()

                self.show_current_player()
                self.check_for_check_and_checkmate()
                pygame.display.flip()
                if self.online_mode:

                    if not self.client.is_connected():
                        self.client.connect_to_server()

                    if self.current_player == self.player_color:
                        # Обрабатываем клик и отправляем ход если это наш ход
                        # print("ONLINE MODE CURR P")
                        self.handle_events()
                    else:
                        # Получаем ход от противника
                        # print("ONLINE MODE OTHER PL")
                        self.online_mode_logic()
                        # Проверка на окончание игры и отображение сообщений
                    self.check_for_check_and_checkmate()
                    self.show_current_player()
                else:
                    if self.bot_mode and self.current_player == self.player_color:
                        self.handle_events()
                    elif self.bot_mode and self.current_player == self.other_player_color:
                        if self.bot_mode_difficulty == "simple":
                            self.bot_make_random_move()
                        elif self.bot_mode_difficulty == "advanced":
                            curr_move = \
                                self.advanced_bot.advanced_bot_move(self.current_player, self.board)
                            self.make_move(curr_move[0], curr_move[1])
                        self.current_player = self.player_color
                    elif not self.bot_mode:
                        self.handle_events()

                self.clock.tick(30)


if __name__ == "__main__":
    game = ChessGame()
    game.run()
