import random

import chess
from evaluate import evaluate_board

INF = 10**9
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}
OPENING_MOVE_VARIATION_MARGIN = 8


def choose_search_depth(board: chess.Board, base_depth: int) -> int:
    search_depth = base_depth

    if board.fullmove_number <= 2:
        search_depth += 1
    elif board.legal_moves.count() <= 12:
        search_depth += 1
    elif len(board.piece_map()) <= 10:
        search_depth += 1

    return search_depth


def get_capture_score(board: chess.Board, move: chess.Move) -> int:
    if board.is_en_passant(move):
        captured_piece_type = chess.PAWN
    else:
        captured_piece_type = board.piece_type_at(move.to_square)

    moving_piece_type = board.piece_type_at(move.from_square)
    if captured_piece_type is None or moving_piece_type is None:
        return 0

    return 10 * PIECE_VALUES[captured_piece_type] - PIECE_VALUES[moving_piece_type]


def score_move(board: chess.Board, move: chess.Move) -> int:
    score = 0

    if board.is_capture(move):
        score += 100 + get_capture_score(board, move)

    if move.promotion is not None:
        score += 200 + PIECE_VALUES[move.promotion]

    if board.gives_check(move):
        score += 50

    if board.is_castling(move):
        score += 40

    return score


def get_ordered_moves(board: chess.Board) -> list[chess.Move]:
    return sorted(board.legal_moves, key=lambda move: score_move(board, move), reverse=True)


def minimax(board: chess.Board, depth: int, alpha: int, beta: int, maximizing_player: bool) -> int:
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = -INF
        for move in get_ordered_moves(board):
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False)
            board.pop()

            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, max_eval)

            if beta <= alpha:
                break

        return max_eval

    else:
        min_eval = INF
        for move in get_ordered_moves(board):
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True)
            board.pop()

            min_eval = min(min_eval, eval_score)
            beta = min(beta, min_eval)

            if beta <= alpha:
                break

        return min_eval


def find_best_move(board: chess.Board, depth: int) -> chess.Move | None:
    search_depth = choose_search_depth(board, depth)
    scored_moves: list[tuple[chess.Move, int]] = []

    if board.turn == chess.WHITE:
        for move in get_ordered_moves(board):
            board.push(move)
            score = minimax(board, search_depth - 1, -INF, INF, False)
            board.pop()
            scored_moves.append((move, score))

        if not scored_moves:
            return None

        best_score = max(score for _, score in scored_moves)
        variation_margin = OPENING_MOVE_VARIATION_MARGIN if board.fullmove_number <= 2 else 0
        best_moves = [
            move
            for move, score in scored_moves
            if score >= best_score - variation_margin
        ]
    else:
        for move in get_ordered_moves(board):
            board.push(move)
            score = minimax(board, search_depth - 1, -INF, INF, True)
            board.pop()
            scored_moves.append((move, score))

        if not scored_moves:
            return None

        best_score = min(score for _, score in scored_moves)
        variation_margin = OPENING_MOVE_VARIATION_MARGIN if board.fullmove_number <= 2 else 0
        best_moves = [
            move
            for move, score in scored_moves
            if score <= best_score + variation_margin
        ]

    return random.choice(best_moves)
