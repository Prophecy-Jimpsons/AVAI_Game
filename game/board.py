import numpy as np
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='game_board.log'
)
logger = logging.getLogger('board')

class Board:
    def __init__(self):
        """Initialize an empty 4x4 board."""
        self.board = np.zeros((4, 4), dtype=int)
        self.pieces_placed = {1: 0, 2: 0}
        self.last_move = None
        self.phase = "placement"  # "placement" or "movement"
        logger.info("New board initialized")

    def place_piece(self, position, player):
        """Place a piece if valid (cell is empty and player has <4 pieces)."""
        try:
            if not isinstance(position, tuple) or len(position) != 2:
                logger.error(f"Invalid position format: {position}")
                return False
                
            row, col = position
            logger.debug(f"Attempting to place piece for player {player} at ({row}, {col})")
            
            if not (0 <= row < 4 and 0 <= col < 4):
                logger.warning(f"Position out of bounds: ({row}, {col})")
                return False
                
            if self.pieces_placed[player] >= 4:
                logger.warning(f"Player {player} already has maximum pieces")
                return False
                
            if self.board[row, col] != 0:
                logger.warning(f"Cell ({row}, {col}) is already occupied")
                return False
                
            self.board[row, col] = player
            self.pieces_placed[player] += 1
            self.last_move = (row, col)
            
            # Check if we should transition to movement phase
            if all(count >= 4 for count in self.pieces_placed.values()):
                self.phase = "movement"
                logger.info("Transitioning to movement phase")
                
            logger.info(f"Player {player} placed piece at ({row}, {col}). Total pieces: {self.pieces_placed[player]}")
            return True
            
        except Exception as e:
            logger.error(f"Error in place_piece: {str(e)}")
            return False
        

    def move_piece(self, from_pos, to_pos, player):
        """Move an existing piece to any empty cell."""
        try:
            if not (isinstance(from_pos, tuple) and isinstance(to_pos, tuple) and 
                    len(from_pos) == 2 and len(to_pos) == 2):
                logger.error("Invalid position format")
                return False
                
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            
            logger.debug(f"Player {player} attempting move from ({from_row}, {from_col}) to ({to_row}, {to_col})")
            
            # Basic validation checks
            if not (0 <= from_row < 4 and 0 <= from_col < 4 and 
                0 <= to_row < 4 and 0 <= to_col < 4):
                logger.warning("Position out of bounds")
                return False
                
            # Check if source has player's piece
            if self.board[from_row, from_col] != player:
                logger.warning(f"Source position ({from_row}, {from_col}) does not contain player {player}'s piece")
                return False
                
            # Check if destination is empty
            if self.board[to_row, to_col] != 0:
                logger.warning(f"Destination position ({to_row}, {to_col}) is not empty")
                return False
                
            # Make the move
            self.board[from_row, from_col] = 0
            self.board[to_row, to_col] = player
            self.last_move = (to_row, to_col)
            logger.info(f"Player {player} successfully moved from ({from_row}, {from_col}) to ({to_row}, {to_col})")
            return True
            
        except Exception as e:
            logger.error(f"Error in move_piece: {str(e)}")
            return False
    
    def is_valid_movement(self, from_pos, to_pos, player):
        """Check if a piece can be moved to any empty cell."""
        try:
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            
            if not (0 <= from_row < 4 and 0 <= from_col < 4 and 
                   0 <= to_row < 4 and 0 <= to_col < 4):
                return False
                    
            return (self.board[from_row, from_col] == player and
                    self.board[to_row, to_col] == 0)
        except (IndexError, TypeError):
            return False


    def is_adjacent(self, pos1, pos2):
        """Check if two positions are adjacent (including diagonals)."""
        try:
            row1, col1 = pos1
            row2, col2 = pos2
            row_diff = abs(row1 - row2)
            col_diff = abs(col1 - col2)
            return (row_diff <= 1 and col_diff <= 1 and (row1, col1) != (row2, col2))
        except Exception as e:
            logger.error(f"Error in is_adjacent: {str(e)}")
            return False
        
    def is_game_over(self):
        """Check if the game is over."""
        try:
            # Game is over if there's a winner or all pieces are placed and no valid moves remain
            if self.check_winner():
                logger.info("Game over: Winner found")
                return True
                
            if self.phase == "placement":
                # In placement phase, game is over if all pieces are placed
                if all(count >= 4 for count in self.pieces_placed.values()):
                    logger.info("Game over: All pieces placed")
                    return True
            else:
                # In movement phase, game is over if any player has no valid moves
                for player in [1, 2]:
                    pieces = self.get_player_pieces(player)
                    empty_cells = self.get_empty_cells()
                    has_valid_move = any(
                        self.is_adjacent(piece, empty_cell)
                        for piece in pieces
                        for empty_cell in empty_cells
                    )
                    if not has_valid_move:
                        logger.info(f"Game over: Player {player} has no valid moves")
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error in is_game_over: {str(e)}")
            return False


    def check_winner(self):
        """Check for a winning condition."""
        try:
            # Check rows and columns
            for i in range(4):
                if (self.board[i, 0] != 0 and np.all(self.board[i, :] == self.board[i, 0]) or
                    self.board[0, i] != 0 and np.all(self.board[:, i] == self.board[0, i])):
                    return True

            # Check diagonals
            if (self.board[0, 0] != 0 and np.all(np.diag(self.board) == self.board[0, 0]) or
                self.board[0, 3] != 0 and np.all(np.diag(np.fliplr(self.board)) == self.board[0, 3])):
                return True

            # Check 2x2 squares
            for i in range(3):
                for j in range(3):
                    square = self.board[i:i+2, j:j+2]
                    if square[0, 0] != 0 and np.all(square == square[0, 0]):
                        return True
            return False
            
        except Exception as e:
            logger.error(f"Error in check_winner: {str(e)}")
            return False

    def get_empty_cells(self):
        """Get all empty cells on the board."""
        try:
            return list(zip(*np.where(self.board == 0)))
        except Exception as e:
            logger.error(f"Error in get_empty_cells: {str(e)}")
            return []

    def get_player_pieces(self, player):
        """Get all positions of a player's pieces."""
        try:
            return list(zip(*np.where(self.board == player)))
        except Exception as e:
            logger.error(f"Error in get_player_pieces: {str(e)}")
            return []

    def __str__(self):
        """String representation of the board."""
        try:
            symbols = {0: '.', 1: 'X', 2: 'O'}
            return "\n".join(" ".join(symbols[cell] for cell in row) for row in self.board)
        except Exception as e:
            logger.error(f"Error in __str__: {str(e)}")
            return "Error displaying board"
