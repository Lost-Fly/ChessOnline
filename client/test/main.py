import unittest

from client.src.game import ChessGame
from client.src.tools.moves_validator import MovesValidator


class TestMovesValidator(unittest.TestCase):

    def setUp(self):
        self.validator = MovesValidator()
        self.board = ChessGame.create_board()

    def test_is_valid_pawn_move(self):
        # Тест на проверку валидности хода пешки
        start_position = (6, 0)  # Обычный первый ход пешки
        end_position = (4, 0)
        piece_type = 6  # White
        self.assertTrue(self.validator.is_valid_pawn_move(piece_type, *start_position, *end_position, self.board))

        # Тестирование заблокированной пешки
        self.board[5][0] = 0
        self.assertFalse(self.validator.is_valid_pawn_move(piece_type, *start_position, *end_position, self.board))

        # TODO рассмотреть другие ситуации ходов

    def test_is_valid_knight_move(self):
        # Проверяем ходы коня
        piece_type = 2  # Black
        start_position = (7, 1)
        correct_moves = [(5, 0), (5, 2)]

        for end_position in correct_moves:
            with self.subTest(end_position=end_position):
                self.assertTrue(
                    self.validator.is_valid_knight_move(piece_type, *start_position, *end_position, self.board))


    # TODO методы для других фигур
    # - test_is_valid_bishop_move
    # - test_is_valid_rook_move
    # - test_is_valid_queen_move
    # - test_is_valid_king_move
    # - test_is_check
    # - test_is_checkmate
    # - test_is_under_attack


class TestChessGame(unittest.TestCase):

    def setUp(self):
        self.game = ChessGame()

    def test_create_board(self):
        board = self.game.create_board()
        self.assertEqual(len(board), 8)
        self.assertEqual(len(board[0]), 8)

    def test_make_move(self):
        # Тестируем, правильно ли отрабатывает make_move
        start_pos = (6, 0)
        end_pos = (4, 0)
        self.assertIsNone(self.game.board[4][0], "Должно быть пусто, перед тем как пешка переместится.")

        self.game.make_move(start_pos, end_pos)
        self.assertEqual(self.game.board[4][0], 6, "Пешка должна переместиться на позицию (4, 0).")
        self.assertIsNone(self.game.board[6][0], "Позиция начального хода пешки должна быть пуста после хода.")

    def test_game_over(self):
        pass

    def test_handle_click(self):
        # Тестирование обработки клика мышью, выбора и перемещения фигур
        pass

    # TODO тесты для других методов ChessGame
    # - test_draw_board
    # - test_draw_pieces
    # - test_handle_events
    # - test_player_selection
    # - test_check_for_check_and_checkmate


if __name__ == '__main__':
    unittest.main()
