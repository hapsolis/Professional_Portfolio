import random


# =========================================================
#  PROJECT: TIC-TAC-TOE - Core Logic Flow
# =========================================================
#  [1] PRINT BOARD         -> Display current state
#  [2] GET MOVE            -> Ask player for input (1–9)
#  [3] VALIDATE INPUT      -> Check if number, range & empty
#  [4] PLACE MARK          -> Update board with X or O
#  [5] CHECK WIN           -> Look for 3-in-a-row
#  [6] CHECK DRAW          -> Check if board is full
#  [7] SWITCH PLAYER       -> Toggle turn (X <-> O)
#  [8] GAME LOOP           -> Repeat steps until end
# =========================================================

def print_board(board):
    """Prints the current 3x3 Tic Tac Toe board.
    Empty cells show their corresponding 1-9 position number for player guidance.
    """
    print("\n")
    for i in range(3):
        # i*3 calculates the starting index_board_cell for each row in the 1D board list:
        # i=0 -> 0*3 = 0 (for first row: board[0:3])
        # i=1 -> 1*3 = 3 (for second row: board[3:6])
        row = board[i*3 : (i+1)*3]
        # Show position numbers if spot is empty
        display_row = []
        for index_board_cell, cell in enumerate(row, start=i*3):
            if cell == " ":
                display_row.append(str(index_board_cell + 1))
            else:
                display_row.append(cell)
        print(" |  ".join(display_row))
        if i < 2:
            print("-----------")
    print("\n")


def is_valid_move(board, position):
    """Check if move is valid: 0-8 index, spot empty on the board list.
    Returns a boolean expression, True or False
    """
    return 0 <= position <= 8 and board[position] == " "


def make_move(board, position, player):
    """Place X or O on the board.
    It takes the board list and accesses the element at the index specified by position.
    Then it changes the value of that element to the player's mark (either 'X' or 'O').
    """
    board[position] = player


def check_win(board, player):
    """Check if player has won (rows, columns, diagonals)."""
    win_patterns = [
        [0,1,2], [3,4,5], [6,7,8],     # rows
        [0,3,6], [1,4,7], [2,5,8],     # columns
        [0,4,8], [2,4,6]               # diagonals
    ]
    for win_patterns_list in win_patterns:
        # all returns True only if all the elements in the iterable are True.
        # If even one is False, all() returns False.
        if all(board[i] == player for i in win_patterns_list):
            return True
    return False


def is_not_a_draw(board):
    """Board full with no winner.
                The not operator inverts the result
    If there's an empty spot, this would evaluate to True.
    If there are no empty spots, this would evaluate to False.
    """
    return " " in board



def get_human_move(board, player):
    """
        Prompts the human player for a move and validates it.
        Keeps asking until a valid move (1-9, empty spot) is entered.
        Args:
            board (list): The current 3x3 Tic Tac Toe board state.
            player (str): The current player's mark ('X' or 'O').
        Returns:
            int: The 0-indexed position (0-8) of the validated move.
        """
    while True:
        try:
            move = int(input(f"Player {player}, enter your move (1-9): ")) - 1
            if is_valid_move(board, move):
                return move
            else:
                print("That spot is taken or invalid. Try again.")
        except ValueError:
            print("Please enter a number between 1 and 9.")





def get_computer_move(board, player):
    """
        Determines the computer's move by randomly selecting an available empty spot.
        Args:
            board (list): The current 3x3 Tic Tac Toe board state.
            player (str): The computer player's mark ('X' or 'O').
        Returns:
            int: The 0-indexed position (0-8) of the computer's chosen move.
            None: If there are no available moves (though this case should ideally
                  be handled by win/draw checks before calling this function).
        """
    available = [i for i in range(9) if board[i] == " "]

    if available:
        move = random.choice(available)
        print(f"Computer ({player}) chooses position {move + 1}")
        return move
    return None


# *************************************************************************************************************
def play_game():
    board = [" " for _ in range(9)]
    current_player = "X"

    print("Welcome to Tic Tac Toe!")
    print("Choose game mode:")
    print("  1 = Human vs Human")
    print("  2 = Human vs Computer (you play as X)")


    # Choose the game mode
    while True:
        mode_input = input("Enter 1 or 2: ").strip()
        if mode_input in ["1", "2"]:
            mode = int(mode_input)
            break
        print("Please enter 1 or 2.")


    current_player = "X"
    is_computer_mode = (mode == 2)  # Mode flag True/False


    # show initial numbered board
    print_board(board)

    # Looping turns
    while True:
        if is_computer_mode and current_player == "O":
            # Computer's turn
            move = get_computer_move(board, current_player)
        else:
            # Human's turn
            move = get_human_move(board, current_player)

        make_move(board, move, current_player)
        print_board(board)

        if check_win(board, current_player):
            print(f"Player {current_player} wins! 🎉")
            break

        if not is_not_a_draw(board):
            print("It's a draw!")
            break

        current_player = "O" if current_player == "X" else "X"




if __name__ == "__main__":
    play_game()
    # Optional: ask to play again
    while input("Play again? (y/n): ").lower() == "y":
        print("\n" + "-"*40 + "\n")
        play_game()

