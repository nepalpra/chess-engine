import sys

import chess

from engine import find_best_move

UNICODE_PIECES = {
    "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
    "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚"
}

COLOR_NAMES = {
    chess.WHITE: "White",
    chess.BLACK: "Black",
}


def render_board(board: chess.Board) -> None:
    print("\n       a   b   c   d   e   f   g   h")
    print("    +---+---+---+---+---+---+---+---+")

    for rank in range(7, -1, -1):
        print(f"  {rank + 1} |", end="")
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)

            if piece is None:
                symbol = " "
            else:
                symbol = UNICODE_PIECES[piece.symbol()]

            print(f" {symbol} |", end="")
        print(f" {rank + 1}")
        print("    +---+---+---+---+---+---+---+---+")

    print("       a   b   c   d   e   f   g   h\n")

    print("Turn:", "White" if board.turn == chess.WHITE else "Black")
    print("Legal moves:", board.legal_moves.count())

    if board.is_check():
        print("Status: Check")

    if board.is_checkmate():
        print("Status: Checkmate")
    elif board.is_stalemate():
        print("Status: Stalemate")
    elif board.is_insufficient_material():
        print("Status: Draw by insufficient material")
    elif board.can_claim_draw():
        print("Status: Draw can be claimed")
    elif board.is_game_over():
        print("Status: Game over")


def get_user_move(board: chess.Board) -> chess.Move | None:
    while True:
        move_text = input("Enter move in UCI format like e2e4, or 'quit': ").strip()

        if move_text.lower() == "quit":
            return None

        try:
            move = chess.Move.from_uci(move_text)
        except ValueError:
            print("Invalid move format. Try again.\n")
            continue

        if move not in board.legal_moves:
            print("Illegal move. Try again.\n")
            continue

        return move


def choose_cli_side() -> chess.Color | None:
    while True:
        choice = input("Choose your side ([w]hite/[b]lack) or 'quit': ").strip().lower()

        if choice in {"quit", "q"}:
            return None
        if choice in {"w", "white"}:
            return chess.WHITE
        if choice in {"b", "black"}:
            return chess.BLACK

        print("Invalid choice. Enter 'w', 'white', 'b', 'black', or 'quit'.\n")


def run_cli() -> None:
    board = chess.Board()
    ai_depth = 3

    print("Starting CLI mode.")
    print("Welcome to CLI Chess.")
    player_color = choose_cli_side()
    if player_color is None:
        print("Exiting game.")
        return

    ai_color = not player_color
    print(f"You are {COLOR_NAMES[player_color]}. AI is {COLOR_NAMES[ai_color]}.")
    print("Enter moves in UCI format like e2e4.\n")

    while not board.is_game_over(claim_draw=True):
        render_board(board)

        if board.turn == player_color:
            move = get_user_move(board)

            if move is None:
                print("Exiting game.")
                break

            board.push(move)

        else:
            print("AI is thinking...")
            ai_move = find_best_move(board, ai_depth)

            if ai_move is None:
                print("AI could not find a move.")
                break

            print(f"AI plays: {ai_move}\n")
            board.push(ai_move)

    render_board(board)
    print("Result:", board.result(claim_draw=True) if board.is_game_over(claim_draw=True) else "Game not finished")


def print_usage() -> None:
    print("Usage:")
    print("  python3 main.py      # Run the CLI version")
    print("  python3 main.py gui  # Run the Pygame GUI version")


def run_gui() -> int:
    try:
        from gui import run_gui as launch_gui
    except ModuleNotFoundError as exc:
        if exc.name == "pygame":
            print("GUI mode requires the 'pygame' package.")
            print("Install it with: python3 -m pip install pygame")
            return 1
        raise

    print("Starting GUI mode.")
    launch_gui()
    return 0


def main(args: list[str] | None = None) -> int:
    argv = sys.argv[1:] if args is None else args

    if not argv:
        run_cli()
        return 0

    if len(argv) == 1 and argv[0] == "gui":
        return run_gui()

    print_usage()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
