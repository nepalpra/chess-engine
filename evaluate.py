import chess

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

CENTER_SQUARES = {
    chess.D4,
    chess.E4,
    chess.D5,
    chess.E5,
}

STARTING_MINOR_PIECE_SQUARES = {
    chess.WHITE: {
        chess.B1,
        chess.G1,
        chess.C1,
        chess.F1,
    },
    chess.BLACK: {
        chess.B8,
        chess.G8,
        chess.C8,
        chess.F8,
    },
}


def get_center_distance(square: int) -> int:
    file_index = chess.square_file(square)
    rank_index = chess.square_rank(square)

    file_distance = min(abs(file_index - 3), abs(file_index - 4))
    rank_distance = min(abs(rank_index - 3), abs(rank_index - 4))
    return file_distance + rank_distance


def get_rank_from_home(square: int, color: chess.Color) -> int:
    rank_index = chess.square_rank(square)
    return rank_index if color == chess.WHITE else 7 - rank_index


def get_piece_square_bonus(piece_type: chess.PieceType, square: int, color: chess.Color) -> int:
    center_distance = get_center_distance(square)
    rank_from_home = get_rank_from_home(square, color)
    file_index = chess.square_file(square)

    if piece_type == chess.PAWN:
        bonus = rank_from_home * 6
        if file_index in {3, 4}:
            bonus += 8
        if square in CENTER_SQUARES:
            bonus += 12
        return bonus

    if piece_type == chess.KNIGHT:
        return 18 - center_distance * 6

    if piece_type == chess.BISHOP:
        return 14 - center_distance * 4

    if piece_type == chess.ROOK:
        return rank_from_home * 3

    if piece_type == chess.QUEEN:
        return 8 - center_distance * 2

    if piece_type == chess.KING:
        if file_index in {2, 6}:
            return 18
        if file_index in {1, 5}:
            return 10
        if file_index in {3, 4}:
            return -10
        return 0

    return 0


def get_positional_score(board: chess.Board, color: chess.Color) -> int:
    score = 0

    for square, piece in board.piece_map().items():
        if piece.color != color:
            continue

        score += get_piece_square_bonus(piece.piece_type, square, color)

        if (
            board.fullmove_number <= 10
            and piece.piece_type in {chess.KNIGHT, chess.BISHOP}
            and square in STARTING_MINOR_PIECE_SQUARES[color]
        ):
            score -= 10

    if len(board.pieces(chess.BISHOP, color)) >= 2:
        score += 20

    return score


def evaluate_board(board: chess.Board) -> int:
    if board.is_checkmate():
        return -100000 if board.turn == chess.WHITE else 100000

    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0

    score = 0

    for piece_type, value in PIECE_VALUES.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * value
        score -= len(board.pieces(piece_type, chess.BLACK)) * value

    score += get_positional_score(board, chess.WHITE)
    score -= get_positional_score(board, chess.BLACK)

    return score
