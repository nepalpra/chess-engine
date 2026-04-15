import chess
import pygame

from engine import find_best_move

BOARD_SIZE = 640
SIDEBAR_WIDTH = 260
WINDOW_WIDTH = BOARD_SIZE + SIDEBAR_WIDTH
WINDOW_HEIGHT = BOARD_SIZE
SQUARE_SIZE = BOARD_SIZE // 8
AI_DEPTH = 3
FPS = 60

LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
SELECTED_SQUARE = (106, 168, 79)
LAST_MOVE_SQUARE = (246, 246, 105)
LEGAL_MOVE_HINT = (62, 111, 39)
BACKGROUND = (24, 28, 38)
SIDEBAR_BACKGROUND = (32, 37, 49)
SIDEBAR_TEXT = (236, 239, 244)
MUTED_TEXT = (187, 194, 207)
WHITE_PIECE = (247, 245, 240)
WHITE_PIECE_BORDER = (70, 70, 70)
BLACK_PIECE = (36, 41, 46)
BLACK_PIECE_BORDER = (215, 220, 228)

PIECE_LABELS = {
    chess.PAWN: "P",
    chess.KNIGHT: "N",
    chess.BISHOP: "B",
    chess.ROOK: "R",
    chess.QUEEN: "Q",
    chess.KING: "K",
}


def get_status_text(board: chess.Board) -> str:
    if board.is_checkmate():
        return "Checkmate"
    if board.is_stalemate():
        return "Stalemate"
    if board.is_insufficient_material():
        return "Draw by insufficient material"
    if board.can_claim_draw():
        return "Draw can be claimed"
    if board.is_check():
        return "Check"
    return "White to move" if board.turn == chess.WHITE else "Black to move"


def get_legal_targets(board: chess.Board, from_square: int | None) -> set[int]:
    if from_square is None:
        return set()

    return {
        move.to_square
        for move in board.legal_moves
        if move.from_square == from_square
    }


def mouse_to_square(position: tuple[int, int]) -> int | None:
    mouse_x, mouse_y = position

    if mouse_x < 0 or mouse_x >= BOARD_SIZE or mouse_y < 0 or mouse_y >= BOARD_SIZE:
        return None

    file_index = mouse_x // SQUARE_SIZE
    rank_index = 7 - (mouse_y // SQUARE_SIZE)
    return chess.square(file_index, rank_index)


def build_player_move(board: chess.Board, from_square: int, to_square: int) -> chess.Move | None:
    move = chess.Move(from_square, to_square)
    if move in board.legal_moves:
        return move

    queen_promotion = chess.Move(from_square, to_square, promotion=chess.QUEEN)
    if queen_promotion in board.legal_moves:
        return queen_promotion

    return None


def draw_board(
    screen: pygame.Surface,
    board: chess.Board,
    fonts: dict[str, pygame.font.Font],
    selected_square: int | None,
    legal_targets: set[int],
    last_move: chess.Move | None,
) -> None:
    for rank in range(8):
        for file_index in range(8):
            square = chess.square(file_index, 7 - rank)
            square_x = file_index * SQUARE_SIZE
            square_y = rank * SQUARE_SIZE

            base_color = LIGHT_SQUARE if (file_index + rank) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(screen, base_color, (square_x, square_y, SQUARE_SIZE, SQUARE_SIZE))

            if last_move is not None and square in {last_move.from_square, last_move.to_square}:
                pygame.draw.rect(screen, LAST_MOVE_SQUARE, (square_x, square_y, SQUARE_SIZE, SQUARE_SIZE))

            if square == selected_square:
                pygame.draw.rect(screen, SELECTED_SQUARE, (square_x, square_y, SQUARE_SIZE, SQUARE_SIZE))

            if square in legal_targets:
                center = (square_x + SQUARE_SIZE // 2, square_y + SQUARE_SIZE // 2)
                pygame.draw.circle(screen, LEGAL_MOVE_HINT, center, 10)

            piece = board.piece_at(square)
            if piece is None:
                continue

            piece_center = (square_x + SQUARE_SIZE // 2, square_y + SQUARE_SIZE // 2)
            fill_color = WHITE_PIECE if piece.color == chess.WHITE else BLACK_PIECE
            border_color = WHITE_PIECE_BORDER if piece.color == chess.WHITE else BLACK_PIECE_BORDER
            text_color = BLACK_PIECE if piece.color == chess.WHITE else WHITE_PIECE

            pygame.draw.circle(screen, fill_color, piece_center, 28)
            pygame.draw.circle(screen, border_color, piece_center, 28, 2)

            label = fonts["piece"].render(PIECE_LABELS[piece.piece_type], True, text_color)
            label_rect = label.get_rect(center=piece_center)
            screen.blit(label, label_rect)

    for file_index in range(8):
        file_label = fonts["coords"].render(chr(ord("a") + file_index), True, MUTED_TEXT)
        file_rect = file_label.get_rect(center=(file_index * SQUARE_SIZE + SQUARE_SIZE // 2, BOARD_SIZE - 12))
        screen.blit(file_label, file_rect)

    for rank in range(8):
        rank_label = fonts["coords"].render(str(8 - rank), True, MUTED_TEXT)
        rank_rect = rank_label.get_rect(center=(12, rank * SQUARE_SIZE + SQUARE_SIZE // 2))
        screen.blit(rank_label, rank_rect)


def draw_sidebar(
    screen: pygame.Surface,
    board: chess.Board,
    fonts: dict[str, pygame.font.Font],
    last_move: chess.Move | None,
) -> None:
    sidebar_rect = pygame.Rect(BOARD_SIZE, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(screen, SIDEBAR_BACKGROUND, sidebar_rect)

    lines = [
        ("GUI MODE", fonts["title"], SIDEBAR_TEXT),
        ("Click a white piece.", fonts["body"], SIDEBAR_TEXT),
        ("Then click its destination.", fonts["body"], SIDEBAR_TEXT),
        ("AI controls Black.", fonts["body"], SIDEBAR_TEXT),
        (f"Turn: {'White' if board.turn == chess.WHITE else 'Black'}", fonts["body"], SIDEBAR_TEXT),
        (f"Status: {get_status_text(board)}", fonts["body"], SIDEBAR_TEXT),
        (f"Legal moves: {board.legal_moves.count()}", fonts["body"], SIDEBAR_TEXT),
        (f"Last move: {last_move.uci() if last_move is not None else '-'}", fonts["body"], SIDEBAR_TEXT),
    ]

    if board.is_game_over(claim_draw=True):
        lines.append((f"Result: {board.result(claim_draw=True)}", fonts["body"], SIDEBAR_TEXT))

    lines.extend(
        [
            ("", fonts["body"], SIDEBAR_TEXT),
            ("Controls", fonts["subtitle"], SIDEBAR_TEXT),
            ("R = restart game", fonts["body"], MUTED_TEXT),
            ("Esc = quit window", fonts["body"], MUTED_TEXT),
        ]
    )

    top = 24
    for text, font, color in lines:
        if not text:
            top += 10
            continue

        rendered = font.render(text, True, color)
        screen.blit(rendered, (BOARD_SIZE + 20, top))
        top += rendered.get_height() + 12


def draw_scene(
    screen: pygame.Surface,
    board: chess.Board,
    fonts: dict[str, pygame.font.Font],
    selected_square: int | None,
    legal_targets: set[int],
    last_move: chess.Move | None,
) -> None:
    screen.fill(BACKGROUND)
    draw_board(screen, board, fonts, selected_square, legal_targets, last_move)
    draw_sidebar(screen, board, fonts, last_move)


def reset_game() -> tuple[chess.Board, int | None, set[int], chess.Move | None]:
    return chess.Board(), None, set(), None


def run_gui() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chess Engine - GUI Mode")
    clock = pygame.time.Clock()

    fonts = {
        "title": pygame.font.SysFont("arial", 28, bold=True),
        "subtitle": pygame.font.SysFont("arial", 22, bold=True),
        "body": pygame.font.SysFont("arial", 20),
        "piece": pygame.font.SysFont("arial", 28, bold=True),
        "coords": pygame.font.SysFont("arial", 16),
    }

    board, selected_square, legal_targets, last_move = reset_game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    board, selected_square, legal_targets, last_move = reset_game()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if board.turn != chess.WHITE or board.is_game_over(claim_draw=True):
                    continue

                clicked_square = mouse_to_square(event.pos)
                if clicked_square is None:
                    selected_square = None
                    legal_targets = set()
                    continue

                clicked_piece = board.piece_at(clicked_square)

                if (
                    clicked_piece is not None
                    and clicked_piece.color == chess.WHITE
                    and (selected_square is None or clicked_square != selected_square)
                ):
                    selected_square = clicked_square
                    legal_targets = get_legal_targets(board, selected_square)
                    continue

                if selected_square is None:
                    continue

                move = build_player_move(board, selected_square, clicked_square)
                if move is not None:
                    board.push(move)
                    last_move = move
                    selected_square = None
                    legal_targets = set()
                elif clicked_square == selected_square:
                    selected_square = None
                    legal_targets = set()

        if running and not board.is_game_over(claim_draw=True) and board.turn == chess.BLACK:
            draw_scene(screen, board, fonts, selected_square, legal_targets, last_move)
            pygame.display.flip()

            ai_move = find_best_move(board, AI_DEPTH)
            if ai_move is not None:
                board.push(ai_move)
                last_move = ai_move

            selected_square = None
            legal_targets = set()

        draw_scene(screen, board, fonts, selected_square, legal_targets, last_move)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
