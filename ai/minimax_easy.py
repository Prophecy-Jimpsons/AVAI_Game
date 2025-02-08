import logging
from utils.helpers import evaluate_board

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='game_ai.log'
)
logger = logging.getLogger('minimax')

def evaluate_line(line, player):
    """Evaluate a line (row, column, or diagonal) for potential patterns."""
    opponent = 3 - player
    player_count = sum(1 for x in line if x == player)
    opponent_count = sum(1 for x in line if x == opponent)
    empty_count = sum(1 for x in line if x == 0)
    
    if player_count == 4:
        return 100  # Winning line
    if opponent_count == 3 and empty_count == 1:
        return 50   # Block opponent win
    if player_count == 3 and empty_count == 1:
        return 25   # Near win
    if player_count == 2 and empty_count == 2:
        return 10   # Building pattern
    return 0

def evaluate_square(square, player):
    """Evaluate a 2x2 square for potential winning patterns."""
    opponent = 3 - player
    player_count = sum(sum(1 for x in row if x == player) for row in square)
    opponent_count = sum(sum(1 for x in row if x == opponent) for row in square)
    empty_count = sum(sum(1 for x in row if x == 0) for row in square)
    
    if player_count == 4:
        return 200  # Winning square
    if player_count == 3 and empty_count == 1:
        return 50   # Near win
    if player_count == 2 and empty_count == 2:
        return 20   # Building pattern
    return 0

def evaluate_position(board, player):
    """Comprehensive evaluation of the board position."""
    score = 0
    
    # Check rows and columns
    for i in range(4):
        row = board.board[i, :]
        col = board.board[:, i]
        score += evaluate_line(row, player)
        score += evaluate_line(col, player)
    
    # Check diagonals
    diag1 = [board.board[i,i] for i in range(4)]
    diag2 = [board.board[i,3-i] for i in range(4)]
    score += evaluate_line(diag1, player)
    score += evaluate_line(diag2, player)
    
    # Check 2x2 squares
    for i in range(3):
        for j in range(3):
            square = board.board[i:i+2, j:j+2]
            score += evaluate_square(square, player)
    
    # Strategic positions
    corners = [(0,0), (0,3), (3,0), (3,3)]
    for corner in corners:
        if board.board[corner] == player:
            score += 15
    
    return score

def minimax(board, depth, maximizing_player, player, phase):
    """
    Minimax algorithm for both placement and movement phases.
    Returns (score, move) tuple.
    """
    logger.debug(f"Minimax called: depth={depth}, maximizing={maximizing_player}, player={player}, phase={phase}")
    
    # Base cases
    if depth == 0 or board.check_winner():
        score = evaluate_position(board, player)
        logger.debug(f"Base case reached: depth={depth}, score={score}")
        return score, None

    current_player = player if maximizing_player else 3 - player

    # Generate valid moves based on phase
    if phase == "placement":
        if board.pieces_placed[current_player] >= 4:
            logger.debug(f"Player {current_player} has placed all pieces")
            return evaluate_position(board, player), None
            
        # Prioritize corners during placement
        empty_cells = board.get_empty_cells()
        corners = [(0,0), (0,3), (3,0), (3,3)]
        strategic_moves = [("place", pos) for pos in empty_cells if pos in corners]
        regular_moves = [("place", pos) for pos in empty_cells if pos not in corners]
        valid_moves = strategic_moves + regular_moves
    else:
        # Movement phase - can move to any empty cell
        player_pieces = board.get_player_pieces(current_player)
        empty_cells = board.get_empty_cells()
        valid_moves = [("move", (from_pos, to_pos))
                      for from_pos in player_pieces
                      for to_pos in empty_cells]

    if not valid_moves:
        logger.debug("No valid moves available")
        return evaluate_position(board, player), None

    if maximizing_player:
        max_eval = float('-inf')
        best_move = None
        
        for move_type, move in valid_moves:
            # Make move
            move_made = False
            if move_type == "place":
                if board.pieces_placed[player] < 4:
                    if board.place_piece(move, player):
                        move_made = True
                        logger.debug(f"Placed piece at {move}")
            else:
                from_pos, to_pos = move
                if board.move_piece(from_pos, to_pos, player):
                    move_made = True
                    logger.debug(f"Moved piece from {from_pos} to {to_pos}")

            if not move_made:
                continue

            # Recursive evaluation
            eval_val, _ = minimax(board, depth - 1, False, player, phase)

            # Undo move
            if move_type == "place":
                board.board[move] = 0
                board.pieces_placed[player] -= 1
            else:
                board.board[to_pos] = 0
                board.board[from_pos] = player

            if eval_val > max_eval:
                max_eval = eval_val
                best_move = (move_type, move)
                logger.debug(f"New best move found: {best_move} with score {max_eval}")

        return max_eval, best_move

    else:  # minimizing player
        min_eval = float('inf')
        best_move = None
        opponent = 3 - player
        
        for move_type, move in valid_moves:
            # Make move
            move_made = False
            if move_type == "place":
                if board.pieces_placed[opponent] < 4:
                    if board.place_piece(move, opponent):
                        move_made = True
                        logger.debug(f"Placed piece at {move}")
            else:
                from_pos, to_pos = move
                if board.move_piece(from_pos, to_pos, opponent):
                    move_made = True
                    logger.debug(f"Moved piece from {from_pos} to {to_pos}")

            if not move_made:
                continue

            # Recursive evaluation
            eval_val, _ = minimax(board, depth - 1, True, player, phase)

            # Undo move
            if move_type == "place":
                board.board[move] = 0
                board.pieces_placed[opponent] -= 1
            else:
                board.board[to_pos] = 0
                board.board[from_pos] = opponent

            if eval_val < min_eval:
                min_eval = eval_val
                best_move = (move_type, move)
                logger.debug(f"New best move found: {best_move} with score {min_eval}")

        return min_eval, best_move
