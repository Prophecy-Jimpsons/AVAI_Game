import numpy as np

def evaluate_board(board, player):
    if board.check_winner():
        # Return positive score if our player made the last move, negative if opponent.
        if board.board[board.last_move] == player:
            return 100
        else:
            return -100
    return heuristic_evaluation(board, player)

def heuristic_evaluation(board, player):
    opponent = 1 if player == 2 else 2
    player_score = count_potential_wins(board, player)
    opponent_score = count_potential_wins(board, opponent)
    return player_score - opponent_score

def count_potential_wins(board, player):
    score = 0
    # Evaluate rows and columns.
    for i in range(4):
        score += evaluate_line(board.board[i, :], player)
        score += evaluate_line(board.board[:, i], player)
    # Evaluate diagonals.
    score += evaluate_line(np.diag(board.board), player)
    score += evaluate_line(np.diag(np.fliplr(board.board)), player)
    # Evaluate 2x2 squares.
    for i in range(3):
        for j in range(3):
            score += evaluate_square(board.board[i:i+2, j:j+2], player)
    return score

def evaluate_line(line, player):
    opponent = 1 if player == 2 else 2
    if np.count_nonzero(line == player) == 3 and np.count_nonzero(line == 0) == 1:
        return 10
    elif np.count_nonzero(line == player) == 2 and np.count_nonzero(line == 0) == 2:
        return 5
    elif np.count_nonzero(line == opponent) == 3 and np.count_nonzero(line == 0) == 1:
        return -9
    return 0

def evaluate_square(square, player):
    opponent = 1 if player == 2 else 2
    if np.count_nonzero(square == player) == 3 and np.count_nonzero(square == 0) == 1:
        return 15
    elif np.count_nonzero(square == player) == 2 and np.count_nonzero(square == 0) == 2:
        return 8
    elif np.count_nonzero(square == opponent) == 3 and np.count_nonzero(square == 0) == 1:
        return -14
    return 0
