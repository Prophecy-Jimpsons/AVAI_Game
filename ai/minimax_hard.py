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
    """Evaluate a line with enhanced threat detection and pattern recognition."""
    opponent = 3 - player
    player_count = sum(1 for x in line if x == player)
    opponent_count = sum(1 for x in line if x == opponent)
    empty_count = sum(1 for x in line if x == 0)
    
    # Critical positions
    if player_count == 4:
        return 10000  # Winning line
    if opponent_count == 4:
        return -10000  # Lost line
    if opponent_count == 3 and empty_count == 1:
        return -5000  # Critical block needed
    if player_count == 3 and empty_count == 1:
        return 4000   # Potential win next move
    
    # Developing threats
    if opponent_count == 2 and empty_count == 2:
        return -2000  # Block developing threat
    if player_count == 2 and empty_count == 2:
        return 1500   # Developing opportunity
    
    # Early position control
    if player_count == 1 and empty_count == 3:
        return 500
    if opponent_count == 1 and empty_count == 3:
        return -400
        
    return 0

def evaluate_square(square, player):
    """Evaluate a 2x2 square with enhanced pattern recognition."""
    opponent = 3 - player
    player_count = sum(sum(1 for x in row if x == player) for row in square)
    opponent_count = sum(sum(1 for x in row if x == opponent) for row in square)
    empty_count = sum(sum(1 for x in row if x == 0) for row in square)
    
    # Critical square patterns
    if player_count == 4:
        return 20000  # Winning square
    if opponent_count == 4:
        return -20000  # Lost square
    if opponent_count == 3 and empty_count == 1:
        return -8000  # Must block square
    if player_count == 3 and empty_count == 1:
        return 6000   # Near win square
    
    # Developing patterns
    if opponent_count == 2 and empty_count == 2:
        return -3000  # Potential threat
    if player_count == 2 and empty_count == 2:
        return 2000   # Good development
        
    return 0

def detect_immediate_threats(board, player):
    """Detect if there are any immediate threats that need attention."""
    opponent = 3 - player
    threat_positions = set()
    
    # Check rows and columns
    for i in range(4):
        row = board.board[i, :]
        col = board.board[:, i]
        
        # Check row threats
        if sum(1 for x in row if x == opponent) == 3 and sum(1 for x in row if x == 0) == 1:
            empty_pos = (i, next(j for j in range(4) if row[j] == 0))
            threat_positions.add(empty_pos)
            
        # Check column threats
        if sum(1 for x in col if x == opponent) == 3 and sum(1 for x in col if x == 0) == 1:
            empty_pos = (next(j for j in range(4) if col[j] == 0), i)
            threat_positions.add(empty_pos)
    
    # Check 2x2 squares
    for i in range(3):
        for j in range(3):
            square = board.board[i:i+2, j:j+2]
            if (sum(sum(1 for x in row if x == opponent) for row in square) == 3 and
                sum(sum(1 for x in row if x == 0) for row in square) == 1):
                # Find the empty position in the square
                for di in range(2):
                    for dj in range(2):
                        if square[di][dj] == 0:
                            threat_positions.add((i+di, j+dj))
    
    return threat_positions

def evaluate_position(board, player):
    """Enhanced position evaluation with threat detection and strategic scoring."""
    score = 0
    opponent = 3 - player
    threats = detect_immediate_threats(board, player)
    
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
            score += 1000
        elif board.board[corner] == opponent:
            score -= 1200
    
    # Threat handling
    if threats:
        if board.pieces_placed[player] < 4:  # Placement phase
            score -= 15000  # Critical to block in placement
        else:  # Movement phase
            score -= 10000  # Important but can potentially move other pieces
    
    return score

def minimax(board, depth, maximizing_player, player, phase, alpha=float('-inf'), beta=float('inf')):
    """Enhanced minimax algorithm with alpha-beta pruning and threat detection."""
    logger.debug(f"Minimax called: depth={depth}, maximizing={maximizing_player}, player={player}, phase={phase}")
    
    # Base cases
    if depth == 0 or board.check_winner():
        score = evaluate_position(board, player)
        logger.debug(f"Base case reached: depth={depth}, score={score}")
        return score, None

    current_player = player if maximizing_player else 3 - player
    threats = detect_immediate_threats(board, current_player)

    # Generate and prioritize moves
    if phase == "placement":
        if board.pieces_placed[current_player] >= 4:
            return evaluate_position(board, player), None
            
        empty_cells = board.get_empty_cells()
        corners = [(0,0), (0,3), (3,0), (3,3)]
        
        # Prioritize moves: threats > corners > other moves
        threat_moves = [("place", pos) for pos in empty_cells if pos in threats]
        corner_moves = [("place", pos) for pos in empty_cells if pos in corners]
        regular_moves = [("place", pos) for pos in empty_cells if pos not in corners and pos not in threats]
        valid_moves = threat_moves + corner_moves + regular_moves
    else:
        player_pieces = board.get_player_pieces(current_player)
        empty_cells = board.get_empty_cells()
        
        # Prioritize defensive moves if threats exist
        if threats:
            valid_moves = [("move", (from_pos, to_pos))
                         for from_pos in player_pieces
                         for to_pos in threats]
            if not valid_moves:  # If can't directly block, consider all moves
                valid_moves = [("move", (from_pos, to_pos))
                             for from_pos in player_pieces
                             for to_pos in empty_cells]
        else:
            valid_moves = [("move", (from_pos, to_pos))
                         for from_pos in player_pieces
                         for to_pos in empty_cells]

    if not valid_moves:
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
            else:
                from_pos, to_pos = move
                if board.move_piece(from_pos, to_pos, player):
                    move_made = True

            if not move_made:
                continue

            eval_val, _ = minimax(board, depth - 1, False, player, phase, alpha, beta)

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
            
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break

        return max_eval, best_move

    else:
        min_eval = float('inf')
        best_move = None
        opponent = 3 - player
        
        for move_type, move in valid_moves:
            move_made = False
            if move_type == "place":
                if board.pieces_placed[opponent] < 4:
                    if board.place_piece(move, opponent):
                        move_made = True
            else:
                from_pos, to_pos = move
                if board.move_piece(from_pos, to_pos, opponent):
                    move_made = True

            if not move_made:
                continue

            eval_val, _ = minimax(board, depth - 1, True, player, phase, alpha, beta)

            if move_type == "place":
                board.board[move] = 0
                board.pieces_placed[opponent] -= 1
            else:
                board.board[to_pos] = 0
                board.board[from_pos] = opponent

            if eval_val < min_eval:
                min_eval = eval_val
                best_move = (move_type, move)
            
            beta = min(beta, eval_val)
            if beta <= alpha:
                break

        return min_eval, best_move
