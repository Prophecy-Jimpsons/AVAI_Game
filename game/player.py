from abc import ABC, abstractmethod
from ai.minimax import minimax
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='game_players.log'
)
logger = logging.getLogger('players')

class Player(ABC):
    def __init__(self, symbol):
        self.symbol = symbol
        logger.info(f"Player initialized with symbol {symbol}")

    @abstractmethod
    def get_move(self, board):
        pass

class HumanPlayer(Player):
    def get_move(self, board):
        logger.debug(f"Human player {self.symbol} getting move. Pieces placed: {board.pieces_placed[self.symbol]}")
        if board.pieces_placed[self.symbol] < 4:
            logger.info(f"Human player {self.symbol} in placement phase")
            return self.get_placement(board)
        else:
            logger.info(f"Human player {self.symbol} in movement phase")
            return self.get_movement(board)

    def get_placement(self, board):
        while True:
            try:
                row = int(input("Enter row (0-3) for placement: "))
                col = int(input("Enter column (0-3) for placement: "))
                logger.debug(f"Human player {self.symbol} attempting placement at ({row}, {col})")
                
                if 0 <= row < 4 and 0 <= col < 4:
                    if board.is_valid_placement((row, col), self.symbol):
                        logger.info(f"Human player {self.symbol} placed piece at ({row}, {col})")
                        return "place", (row, col)
                    else:
                        logger.warning(f"Invalid placement attempt by human at ({row}, {col})")
                        print("Invalid placement. Either the cell is taken or you already have 4 pieces on board.")
                else:
                    logger.warning(f"Out of bounds placement attempt by human at ({row}, {col})")
                    print("Position out of bounds. Please enter numbers between 0 and 3.")
            except ValueError as e:
                logger.error(f"Invalid input by human player: {str(e)}")
                print("Invalid input. Please enter integer numbers.")

    def get_movement(self, board):
        while True:
            try:
                from_row = int(input("Enter row (0-3) of piece to move: "))
                from_col = int(input("Enter column (0-3) of piece to move: "))
                to_row = int(input("Enter row (0-3) for destination: "))
                to_col = int(input("Enter column (0-3) for destination: "))
                
                logger.debug(f"Human player {self.symbol} attempting move from ({from_row}, {from_col}) to ({to_row}, {to_col})")
                
                if (0 <= from_row < 4 and 0 <= from_col < 4 and 
                    0 <= to_row < 4 and 0 <= to_col < 4):
                    if board.is_valid_movement((from_row, from_col), (to_row, to_col), self.symbol):
                        logger.info(f"Human player {self.symbol} moved from ({from_row}, {from_col}) to ({to_row}, {to_col})")
                        return "move", ((from_row, from_col), (to_row, to_col))
                    else:
                        logger.warning(f"Invalid movement attempt by human")
                        print("Invalid movement. Ensure you select one of your pieces and move it to an adjacent empty cell.")
                else:
                    logger.warning("Out of bounds movement attempt by human")
                    print("Position out of bounds. Please enter numbers between 0 and 3.")
            except ValueError as e:
                logger.error(f"Invalid input by human player: {str(e)}")
                print("Invalid input. Please enter integer numbers.")

class AIPlayer(Player):
    def get_move(self, board):
        logger.debug(f"AI player {self.symbol} getting move. Pieces placed: {board.pieces_placed[self.symbol]}")
        if board.pieces_placed[self.symbol] < 4:
            logger.info(f"AI player {self.symbol} in placement phase")
            return self.get_placement(board)
        else:
            logger.info(f"AI player {self.symbol} in movement phase")
            return self.get_movement(board)

    def get_placement(self, board):
        logger.debug("AI calculating placement move")
        score, move = minimax(board, 3, True, self.symbol, "placement")
        if move is None:
            logger.error("AI failed to generate placement move")
            # Fallback: find first empty cell
            for i in range(4):
                for j in range(4):
                    if board.is_valid_placement((i, j), self.symbol):
                        logger.info(f"AI using fallback placement at ({i}, {j})")
                        return "place", (i, j)
        else:
            logger.info(f"AI placed piece at {move[1]} with score {score}")
            return move

    def get_movement(self, board):
        logger.debug("AI calculating movement move")
        score, move = minimax(board, 3, True, self.symbol, "movement")
        if move is None:
            logger.error("AI failed to generate movement move")
            # Fallback: find first valid move
            pieces = board.get_player_pieces(self.symbol)
            empty_cells = board.get_empty_cells()
            for piece in pieces:
                for cell in empty_cells:
                    if board.is_valid_movement(piece, cell, self.symbol):
                        logger.info(f"AI using fallback movement from {piece} to {cell}")
                        return "move", (piece, cell)
        else:
            logger.info(f"AI moved piece {move[1]} with score {score}")
            return move
