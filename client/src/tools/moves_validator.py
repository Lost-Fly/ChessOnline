BOARD_SIZE = 8


class MovesValidator:
    def __init__(self, board):
        self.board = board

    def is_valid_move(self, piece_type, start_row, start_col, end_row, end_col):
        board = self.board
        # Проверка выхода за границы
        if not (0 <= end_row < BOARD_SIZE and 0 <= end_col < BOARD_SIZE):
            return False

        # Если на месте стоит фигура нашего цвета
        if piece_type is not None and board[end_row][end_col] is not None:
            if (board[end_row][end_col] < 6 and piece_type < 6) or (board[end_row][end_col] >= 6 and piece_type >= 6):
                return False

        # Specific move validation based on piece type
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
            return False  # Invalid piece type

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
        # Простейшая проверка хода короля (без рокировки)
        return max(abs(start_row - end_row), abs(start_col - end_col)) == 1
