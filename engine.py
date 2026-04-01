import chess
from evaluate import evaluate_board

INF = 10**9


def minimax(board: chess.Board, depth: int, alpha: int, beta: int, maximizing_player: bool) -> int:
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = -INF
        for move in board.legal_moves:
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
        for move in board.legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True)
            board.pop()

            min_eval = min(min_eval, eval_score)
            beta = min(beta, min_eval)

            if beta <= alpha:
                break

        return min_eval


def find_best_move(board: chess.Board, depth: int) -> chess.Move | None:
    best_move = None

    if board.turn == chess.WHITE:
        best_score = -INF
        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, -INF, INF, False)
            board.pop()

            if score > best_score:
                best_score = score
                best_move = move
    else:
        best_score = INF
        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, -INF, INF, True)
            board.pop()

            if score < best_score:
                best_score = score
                best_move = move

    return best_move