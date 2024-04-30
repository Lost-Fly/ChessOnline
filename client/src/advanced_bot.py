import copy
import random


class AdvancedBot:
    def __init__(self, moves_validator):
        self.moves_validator = moves_validator

    def advanced_bot_move(self, current_player, board):
        best_score = -float('inf')
        best_move = None
        all_possible_moves = self.moves_validator.get_all_possible_moves(current_player, board)

        for move in all_possible_moves:
            cloned_board = copy.deepcopy(board)
            self.simulate_move(cloned_board, move[0], move[1])
            score = self.minimax(cloned_board, depth=3, alpha=-float('inf'), beta=float('inf'), maximizing_player=True)
            if score > best_score:
                best_score = score
                best_move = move

        if best_move:
            return best_move[0], best_move[1]

    def simulate_move(self, board, start_pos, end_pos):
        piece = board[start_pos[0]][start_pos[1]]
        board[start_pos[0]][start_pos[1]] = None
        board[end_pos[0]][end_pos[1]] = piece

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0:
            return self.evaluate_board(board)

        if maximizing_player:
            max_eval = -float('inf')
            all_moves = self.moves_validator.get_all_possible_moves('white', board)
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
            all_moves = self.moves_validator.get_all_possible_moves('black', board)
            for move in all_moves:
                new_board = copy.deepcopy(board)
                self.simulate_move(new_board, move[0], move[1])
                eval_ = self.minimax(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_)
                beta = min(beta, eval_)
                if beta <= alpha:
                    break
            return min_eval

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

    def choose_random_black_piece(self, board):

        black_pieces = [(i, j) for i in range(len(board))
                        for j in range(len(board[i])) if board[i][j] is not None and board[i][j] < 6]

        if black_pieces:
            return random.choice(black_pieces)
        else:
            return None
