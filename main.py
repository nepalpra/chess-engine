import chess


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
                print(piece.symbol(), end=" ")
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


def main():
    board = chess.Board()

    while not board.is_game_over():
        render_board(board)

        move_text = input("Enter move in UCI format like e2e4, or 'quit': ").strip()

        if move_text.lower() == "quit":
            print("Exiting game.")
            break

        try:
            move = chess.Move.from_uci(move_text)
        except ValueError:
            print("Invalid move format. Try again.\n")
            continue

        if move not in board.legal_moves:
            print("Illegal move. Try again.\n")
            continue

        board.push(move)

    render_board(board)
    print("Result:", board.result() if board.is_game_over() else "Game not finished")


if __name__ == "__main__":
    main()
