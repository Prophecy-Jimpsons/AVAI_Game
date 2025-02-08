from game.board import Board
from game.player import HumanPlayer, AIPlayer

def main():
    board = Board()
    human = HumanPlayer(1)
    ai = AIPlayer(2)
    current_player = human
    selected_piece = None  # Used during movement phase to track the piece being moved

    while not board.is_game_over():
        print(board)
        print(f"Player {current_player.symbol}'s turn")

        if board.pieces_placed[current_player.symbol] < 4:  # Placement phase
            move_type, pos = current_player.get_move(board)
            if move_type == "place":
                if board.place_piece(pos, current_player.symbol):
                    print(f"Player {current_player.symbol} placed a piece at {pos}.")
                else:
                    print("Invalid placement: The cell is occupied or you already have 4 pieces.")
                    continue
            else:
                print("Invalid action: You must place a piece during the placement phase.")
                continue
        else:  # Movement phase
            if not selected_piece:  # Select a piece to move
                print("Select one of your pieces to move.")
                move_type, from_pos = current_player.get_move(board)
                if move_type == "move" and board.board[from_pos] == current_player.symbol:
                    selected_piece = from_pos
                    print(f"Selected piece at {selected_piece}. Now select a destination.")
                else:
                    print("Invalid selection. Please select one of your own pieces.")
                    continue
            else:  # Move the selected piece to a destination
                move_type, to_pos = current_player.get_move(board)
                if move_type == "move" and board.move_piece(selected_piece, to_pos, current_player.symbol):
                    print(f"Player {current_player.symbol} moved a piece from {selected_piece} to {to_pos}.")
                    selected_piece = None  # Reset after a successful move
                else:
                    print("Invalid move. Please try again.")
                    continue

        # Check for a winner after each move.
        if board.check_winner():
            print(board)
            print(f"Player {current_player.symbol} wins!")
            return

        # Switch player.
        current_player = ai if current_player == human else human

    print(board)
    print("Game over.")

if __name__ == '__main__':
    main()