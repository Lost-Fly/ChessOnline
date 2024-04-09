BOARD_SIZE = 8


class MovesValidator:
    def __init__(self):
        self.exist = True

    def get_all_possible_moves(self, player_color, board):
        all_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = board[row][col]
                if piece is not None:
                    if (player_color == "white" and 6 <= piece < 12) or (player_color == "black" and 0 <= piece < 6):
                        # Проверяем каждую клетку доски на возможность хода для фигуры
                        for end_row in range(BOARD_SIZE):
                            for end_col in range(BOARD_SIZE):
                                if self.is_valid_move(piece, row, col, end_row, end_col, board):
                                    all_moves.append(((row, col), (end_row, end_col)))
        return all_moves

    def is_under_attack(self, row, col, attacking_color, board):
        attackers = range(6) if attacking_color == "black" else range(6, 12)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] in attackers:
                    if self.is_valid_move(board[r][c], r, c, row, col, board):
                        return True
        return False

    def is_check(self, king_row, king_col, board):
        king_color = "white" if board[king_row][king_col] == 11 else "black"
        attacking_color = "black" if king_color == "white" else "white"

        # Проверка, под атакой ли король
        return self.is_under_attack(king_row, king_col, attacking_color, board)

    def is_checkmate(self, king_row, king_col, board):
        # Проверка на шах
        if not self.is_check(king_row, king_col, board):
            return False

        # Цвет короля и атакующих
        king_color = "white" if board[king_row][king_col] == 11 else "black"
        attacking_color = "black" if king_color == "white" else "white"

        # Проверка может ли король выйти из под шаха сам
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = king_row + dr, king_col + dc
                if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                    if self.is_valid_move(board[king_row][king_col], king_row, king_col, new_row, new_col, board):
                        # Делаем ход
                        saved_piece = board[new_row][new_col]
                        board[king_row][king_col] = None
                        board[new_row][new_col] = 11 if king_color == "white" else 5
                        if not self.is_under_attack(new_row, new_col, attacking_color, board):

                            print("KING CAN ESCAPE")
                            board[new_row][new_col] = saved_piece
                            board[king_row][king_col] = 11 if king_color == "white" else 5
                            return False
                        # Отмена хода
                        board[new_row][new_col] = saved_piece
                        board[king_row][king_col] = 11 if king_color == "white" else 5

        # Проверка, могут ли другие фигуры спасти короля
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] is not None:
                    if (king_color == "white" and 6 <= board[r][c] < 12) or (
                            king_color == "black" and 0 <= board[r][c] < 6):
                        for new_r in range(BOARD_SIZE):
                            for new_c in range(BOARD_SIZE):
                                if board[r][c] != 11 and board[r][c] != 5:
                                    if self.is_valid_move(board[r][c], r, c, new_r, new_c, board):
                                        # Делаем ход
                                        captured_piece = board[new_r][new_c]
                                        board[new_r][new_c] = board[r][c]
                                        board[r][c] = None
                                        if not self.is_check(king_row, king_col, board):
                                            print("SUGGESTED SAVE MOVE: from " + str(r) +", " + str(c) +"  with " + str(board[new_r][new_c]) + "   to " + str(new_r) +", " + str(new_c))
                                            # Отмена хода
                                            print("KING CAN BE SAVED")
                                            board[r][c] = board[new_r][new_c]
                                            board[new_r][new_c] = captured_piece
                                            return False
                                        # Отмена хода
                                        board[r][c] = board[new_r][new_c]
                                        board[new_r][new_c] = captured_piece

        return True  # Мат - если не вышел сам и не закрыли фигуры

    def is_valid_move(self, piece_type, start_row, start_col, end_row, end_col, board):
        # Проверка выхода за границы
        if not (0 <= end_row < BOARD_SIZE and 0 <= end_col < BOARD_SIZE):
            return False

        # Если на месте стоит фигура нашего цвета
        if piece_type is not None and board[end_row][end_col] is not None:
            if (board[end_row][end_col] < 6 and piece_type < 6) or (board[end_row][end_col] >= 6 and piece_type >= 6):
                return False

        # Для каждой фигуры свой метод
        if piece_type == 0 or piece_type == 6:  # Пешка
            return self.is_valid_pawn_move(piece_type, start_row, start_col, end_row, end_col, board)
        elif piece_type == 1 or piece_type == 7:  # Ладья
            return self.is_valid_rook_move(piece_type, start_row, start_col, end_row, end_col, board)
        elif piece_type == 2 or piece_type == 8:  # Конь
            return self.is_valid_knight_move(piece_type, start_row, start_col, end_row, end_col, board)
        elif piece_type == 3 or piece_type == 9:  # Слон
            return self.is_valid_bishop_move(piece_type, start_row, start_col, end_row, end_col, board)
        elif piece_type == 4 or piece_type == 10:  # Ферзь
            return self.is_valid_queen_move(piece_type, start_row, start_col, end_row, end_col, board)
        elif piece_type == 5 or piece_type == 11:  # Король
            return self.is_valid_king_move(piece_type, start_row, start_col, end_row, end_col, board)
        else:
            return False

    def is_valid_pawn_move(self, piece_type, start_row, start_col, end_row, end_col, board):
        direction = 1 if piece_type == 0 else -1  # Определяем направление: вверх для белых, вниз для черных

        # Проверка на обычный ход вперед
        if start_col == end_col and board[end_row][end_col] is None:
            if end_row - start_row == direction:
                return True
            # Проверка на двойной ход с начальной позиции
            if (start_row == 1 or start_row == 6) and end_row - start_row == 2 * direction and \
                    board[start_row + direction][start_col] is None:
                return True
        # Проверка на взятие фигуры
        elif abs(start_col - end_col) == 1 and end_row - start_row == direction and board[end_row][end_col] is not None:
            return True
        return False

    def is_valid_knight_move(self, piece_type, start_row, start_col, end_row, end_col, board):
        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)
        # Ход конем
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def is_valid_bishop_move(self, piece_type, start_row, start_col, end_row, end_col, board):
        if abs(start_row - end_row) != abs(start_col - end_col):
            return False
        # Проверка наличия других фигур на диагональном пути
        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1
        for step in range(1, abs(start_row - end_row)):
            if board[start_row + step * row_step][start_col + step * col_step] is not None:
                return False
        return True

    def is_valid_rook_move(self, piece_type, start_row, start_col, end_row, end_col, board):
        # Проверка, что ход ладьей происходит либо по горизонтали, либо по вертикали
        if start_row != end_row and start_col != end_col:
            return False
        # Проверка наличия других фигур на пути
        if start_row == end_row:
            step = 1 if end_col > start_col else -1
            for col in range(start_col + step, end_col, step):
                if board[start_row][col] is not None:
                    return False
        else:
            step = 1 if end_row > start_row else -1
            for row in range(start_row + step, end_row, step):
                if board[row][start_col] is not None:
                    return False
        return True

    def is_valid_queen_move(self, piece_type, start_row, start_col, end_row, end_col, board):
        # Ферзь может двигаться как ладья или как слон
        return self.is_valid_rook_move(piece_type, start_row, start_col, end_row, end_col, board) or \
               self.is_valid_bishop_move(piece_type, start_row, start_col, end_row, end_col, board)

    def is_valid_king_move(self, piece_type, start_row, start_col, end_row, end_col, board):
        # if self.is_check(end_row, end_col, board):
        #     return False
        # Простейшая проверка хода короля (без рокировки)
        return max(abs(start_row - end_row), abs(start_col - end_col)) == 1
