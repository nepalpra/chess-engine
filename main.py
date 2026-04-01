import chess
from engine import find_best_move


import chess

UNICODE_PIECES = {
    "P": "♟", "N": "♞", "B": "♝", "R": "♜", "Q": "♛", "K": "♚",
    "p": "♙", "n": "♘", "b": "♗", "r": "♖", "q": "♕", "k": "♔"
}


def render_board(board: chess.Board) -> None:
    print("\n    a b c d e f g h")
    print("   -----------------")

    for rank in range(7, -1, -1):
        print(f" {rank + 1} |", end=" ")
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)

            if piece is None:
                print(".", end=" ")
            else:
                print(UNICODE_PIECES[piece.symbol()], end=" ")
        print(f"| {rank + 1}")

    print("   -----------------")
    print("    a b c d e f g h\n")

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
    elif board.is_game_over():
        print("Status: Game over")


def get_user_move(board: chess.Board) -> chess.Move:
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


def main():
    board = chess.Board()
    ai_depth = 3

    print("Welcome to CLI Chess.")
    print("You are White. AI is Black.")
    print("Enter moves in UCI format like e2e4.\n")

    while not board.is_game_over():
        render_board(board)

        if board.turn == chess.WHITE:
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
    print("Result:", board.result() if board.is_game_over() else "Game not finished")


if __name__ == "__main__":
    main()