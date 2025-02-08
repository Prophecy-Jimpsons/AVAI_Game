import PySimpleGUI as sg
from game.board import Board
from game.player import HumanPlayer, AIPlayer

def create_board_layout():
    """Create the 4x4 grid of buttons"""
    return [[sg.Button('', size=(4, 2), key=(i, j), button_color=('black', 'white')) 
             for j in range(4)] for i in range(4)]

def update_board(window, board):
    """Update the visual state of the board"""
    for i in range(4):
        for j in range(4):
            piece = board.board[i, j]
            text = '.' if piece == 0 else 'X' if piece == 1 else 'O'
            window[(i, j)].update(text=text)

def reset_colors(window):
    """Reset all button colors to default"""
    for i in range(4):
        for j in range(4):
            window[(i, j)].update(button_color=('black', 'white'))

def main():
    # Initialize game components
    board = Board()
    human = HumanPlayer(1)
    ai = AIPlayer(2)
    current_player = human
    selected_piece = None
    game_phase = "placement"
    player_pieces = {1: 0, 2: 0}  # Explicit piece counter

    # Create the window layout
    layout = [
        [sg.Text('Game Phase: Placement', key='phase', size=(30, 1))],
        [sg.Text('Player 1 Turn', key='status', size=(30, 1))],
        [sg.Text(f'Pieces - Player: {player_pieces[1]}/4, AI: {player_pieces[2]}/4', key='pieces', size=(30, 1))],
        *create_board_layout(),
        [sg.Text('', key='message', size=(30, 1), text_color='red')],
        [sg.Button('Exit')]
    ]

    window = sg.Window('4x4 Super Tic-Tac-Toe', layout)

    while True:
        event, _ = window.read()
        
        if event in (sg.WINDOW_CLOSED, 'Exit'):
            break

        if isinstance(event, tuple):
            row, col = event

            if current_player == human:
                # PLACEMENT PHASE
                if game_phase == "placement":
                    # Strict piece limit check
                    if player_pieces[1] >= 4:
                        window['message'].update("You've already placed all 4 pieces!")
                        continue
                        
                    if board.place_piece((row, col), 1):
                        player_pieces[1] += 1
                        update_board(window, board)
                        window['message'].update('')
                        window['pieces'].update(f'Pieces - Player: {player_pieces[1]}/4, AI: {player_pieces[2]}/4')
                        window['status'].update(f"Player 1: Placed piece ({player_pieces[1]}/4)")
                        
                        # Phase transition check
                        if player_pieces[1] == 4 and player_pieces[2] == 4:
                            game_phase = "movement"
                            window['phase'].update('Game Phase: Movement')
                            window['status'].update("Player 1: Select a piece to move")
                        else:
                            current_player = ai
                    else:
                        window['message'].update("Invalid placement! Cell occupied.")

                # MOVEMENT PHASE
                else:
                    if not selected_piece:
                        if board.board[row, col] == 1:
                            selected_piece = (row, col)
                            window[event].update(button_color=('black', 'yellow'))
                            window['status'].update("Select destination for piece")
                            window['message'].update('')
                        else:
                            window['message'].update("Select your own piece (X) to move")
                    else:
                        if board.move_piece(selected_piece, (row, col), 1):
                            reset_colors(window)
                            update_board(window, board)
                            window['message'].update('')
                            window['status'].update("Piece moved successfully")
                            selected_piece = None
                            current_player = ai
                        else:
                            window['message'].update("Invalid move! Select piece again")
                            reset_colors(window)
                            selected_piece = None

                if board.check_winner():
                    sg.popup("Player 1 Wins!")
                    break

            # AI TURN
            if current_player == ai:
                window['status'].update("AI is thinking...")
                window.refresh()

                if game_phase == "placement" and player_pieces[2] < 4:
                    _, move = ai.get_move(board)
                    if board.place_piece(move, 2):
                        player_pieces[2] += 1
                        update_board(window, board)
                        window['pieces'].update(f'Pieces - Player: {player_pieces[1]}/4, AI: {player_pieces[2]}/4')
                        window['status'].update(f"AI placed piece ({player_pieces[2]}/4)")
                        
                        if player_pieces[1] == 4 and player_pieces[2] == 4:
                            game_phase = "movement"
                            window['phase'].update('Game Phase: Movement')
                else:
                    # AI movement phase
                    _, move = ai.get_move(board)
                    from_pos, to_pos = move
                    if board.move_piece(from_pos, to_pos, 2):
                        update_board(window, board)
                        window['status'].update("AI moved a piece")

                if board.check_winner():
                    sg.popup("AI Wins!")
                    break

                current_player = human
                window['status'].update("Player 1's Turn")

    window.close()

if __name__ == '__main__':
    main()
