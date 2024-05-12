import copy

BOARD_SIZE = 8


class MovesValidator:
    def __init__(self):

        self.exist = True

    def get_kings_pos(self, board):
        kings_pos = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = board[row][col]
                if piece is not None:
                    if piece == 5 or piece == 11:
                        kings_pos.append((row, col))
        return kings_pos

    def get_all_possible_moves(self, player_color, board):
        all_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = board[row][col]
                # k_pos = self.get_kings_pos(board)
                if piece is not None:
                    if (player_color == "white" and 6 <= piece < 12) or (player_color == "black" and 0 <= piece < 6):
                        # Проверяем каждую клетку доски на возможность хода для фигуры
                        for end_row in range(BOARD_SIZE):
                            for end_col in range(BOARD_SIZE):

                                if piece == 5 or piece == 11:  # Индексы королей
                                    if self.is_valid_move(piece, row, col, end_row, end_col, board):
                                        cloned_board = copy.deepcopy(board)
                                        piece = cloned_board[row][col]
                                        cloned_board[row][col] = None
                                        cloned_board[end_row][end_col] = piece

                                        is_check = self.is_check(end_row, end_col, cloned_board)
                                        if not is_check:
                                            all_moves.append(((row, col), (end_row, end_col)))

                                elif self.is_valid_move(piece, row, col, end_row, end_col, board):

                                    cloned_board = copy.deepcopy(board)
                                    piece = cloned_board[row][col]
                                    cloned_board[row][col] = None
                                    cloned_board[end_row][end_col] = piece

                                    k_pos = self.get_kings_pos(board)

                                    is_check_1 = self.is_check(k_pos[0][0], k_pos[0][1], cloned_board)
                                    piece_1 = board[k_pos[0][0]][k_pos[0][1]]
                                    is_check_2 = self.is_check(k_pos[1][0], k_pos[1][1], cloned_board)
                                    piece_2 = board[k_pos[1][0]][k_pos[1][1]]

                                    if piece_1 == 5 and player_color == "black" and not is_check_1:
                                        all_moves.append(((row, col), (end_row, end_col)))
                                    elif piece_1 == 11 and player_color == "white" and not is_check_1:
                                        all_moves.append(((row, col), (end_row, end_col)))
                                    elif piece_2 == 5 and player_color == "black" and not is_check_2:
                                        all_moves.append(((row, col), (end_row, end_col)))
                                    elif piece_2 == 11 and player_color == "white" and not is_check_2:
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
                            # print("KING CAN ESCAPE")
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
                                            # print(
                                            #     "SUGGESTED SAVE MOVE: from " + str(r) + ", " + str(c) + "  with " + str(
                                            #         board[new_r][new_c]) + "   to " + str(new_r) + ", " + str(new_c))
                                            # # Отмена хода
                                            # print("KING CAN BE SAVED")
                                            board[r][c] = board[new_r][new_c]
                                            board[new_r][new_c] = captured_piece
                                            return False
                                        # Отмена хода
                                        board[r][c] = board[new_r][new_c]
                                        board[new_r][new_c] = captured_piece

        return True  # Мат - если не вышел сам и не закрыли фигуры

    def is_stalemate(self, player_color, board):
        all_moves = self.get_all_possible_moves(player_color, board)
        if not all_moves:  # Если нет доступных ходов
            king_row, king_col = self.get_king_pos(player_color, board)  # Получаем позицию короля
            if not self.is_check(king_row, king_col, board):  # Если король не находится под шахом
                return True  # Это пат
        return False

    def get_king_pos(self, player_color, board):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = board[row][col]
                if player_color == "white" and piece == 11 or player_color == "black" and piece == 5:
                    return row, col
        return None, None

    def is_valid_move_in_check(self, start_row, start_col, end_row, end_col, board):
        # Проверка на выход из под шаха
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = board[row][col]
                if piece == 5 or piece == 11:  # Индексы королей
                    is_check = self.is_check(row, col, board)  # шах до хода
                    # print("IS CHECK BEF MPVE" + str(is_check))
                    if is_check:
                        cloned_board = copy.deepcopy(board)
                        piece = cloned_board[start_row][start_col]
                        cloned_board[start_row][start_col] = None
                        cloned_board[end_row][end_col] = piece

                        for row_h in range(BOARD_SIZE):
                            for col_h in range(BOARD_SIZE):
                                piece = cloned_board[row_h][col_h]
                                if piece == 5 or piece == 11:  # Индексы королей
                                    is_check_after = self.is_check(row_h, col_h, cloned_board)  # шах после хода
                                    # print("IS CHECK AFTER MPVE " + str(is_check_after))
                                    if is_check_after:
                                        return False
        return True

    def is_valid_move(self, piece_type, start_row, start_col, end_row, end_col, board):
        # Проверка выхода за границы
        if not (0 <= end_row < BOARD_SIZE and 0 <= end_col < BOARD_SIZE):
            return False

        # Если на месте стоит фигура нашего цвета
        if piece_type is not None and board[end_row][end_col] is not None:
            if (board[end_row][end_col] < 6 and piece_type < 6) or (board[end_row][end_col] >= 6 and piece_type >= 6):
                return False

        # for row_c in range(BOARD_SIZE):
        #     for col_c in range(BOARD_SIZE):
        #         piece = board[row_c][col_c]
        #         if piece is not None:
        #             if piece == 5 or piece == 11:  # Индексы королей
        #
        #                 cloned_board = copy.deepcopy(board)
        #                 piece_other = cloned_board[start_row][start_col]
        #                 cloned_board[start_row][start_col] = None
        #                 cloned_board[end_row][end_col] = piece_other
        #
        #                 if self.is_check(row_c, col_c, cloned_board):
        #                     return False

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

        # Если это обычный ход короля
        if max(abs(start_row - end_row), abs(start_col - end_col)) == 1:
            opposite_king = 11 if piece_type == 5 else 5
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    if not (0 <= end_row + dr < BOARD_SIZE and 0 <= end_col + dc < BOARD_SIZE):
                        continue
                    elif board[end_row + dr][end_col + dc] == opposite_king:
                        return False

            return True
        # Проверка на рокировку
        elif self.is_valid_castling_move(piece_type, start_row, start_col, end_row, end_col, board):
            self.perform_castling(start_row, start_col, 0 if end_col < start_col else 7, board)
            return True

        return False

    def is_valid_castling_move(self, piece_type, start_row, start_col, end_row, end_col, board):
        if start_row != end_row or (start_row != 0 or start_row != 7) or (end_row != 0 or end_row != 7):
            return False
        # Только король может участвовать в рокировке
        if piece_type not in [5, 11]:
            return False

        # Проверяем, что король на той же строке и остается в пределах колонок для рокировки
        if start_row != end_row or abs(start_col - end_col) != 2:
            return False

        # Проверяем, не находится ли король под шахом
        if self.is_check(start_row, start_col, board):
            return False

        # Определяем сторону рокировки и соответствующие ладьи
        rook_col = 0 if end_col < start_col else 7
        king_side = rook_col == 7
        direction = 1 if king_side else -1

        # Проверяем, что между королем и ладьей нет фигур
        for col in range(min(start_col, rook_col) + 1, max(start_col, rook_col)):
            if board[start_row][col] is not None:
                return False

        # Проверяем, что клетки, через которые проходит король, не под атакой
        for col in range(start_col, end_col + direction, direction):
            if self.is_under_attack(start_row, col, "black" if piece_type == 11 else "white", board):
                return False

        return True

    def perform_castling(self, start_row, start_col, rook_col, board):
        # Обновляем позицию короля
        new_king_col = 6 if rook_col == 7 else 2
        board[start_row][new_king_col] = board[start_row][start_col]
        board[start_row][start_col] = None

        # Обновляем позицию ладьи
        new_rook_col = 5 if rook_col == 7 else 3
        board[start_row][new_rook_col] = board[start_row][rook_col]
        board[start_row][rook_col] = None
