"""Module 2 - Adversarial search on Tic-tac-toe (AIMA ch. 5).

The board is a list of 9 cells holding "X", "O" or "".  The human is X (MIN),
the computer is O (MAX).  Utility: +1 if O wins, -1 if X wins, 0 for a draw,
scaled by depth so that faster wins (and slower losses) score better.
"""
import math

LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def winning_line(board):
    for line in LINES:
        a, b, c = line
        if board[a] and board[a] == board[b] == board[c]:
            return line
    return None


def winner(board):
    line = winning_line(board)
    if line:
        return board[line[0]]
    return "Draw" if all(board) else None


def moves(board):
    return [i for i, v in enumerate(board) if not v]


def utility(board, depth):
    w = winner(board)
    return {"O": 10 - depth, "X": depth - 10, "Draw": 0}[w]


def minimax(board, player="O"):
    """Plain Minimax. Returns (best move, value, nodes visited)."""
    nodes = 0

    def value(b, turn, depth):
        nonlocal nodes
        nodes += 1
        if winner(b):
            return utility(b, depth)
        scores = []
        for m in moves(b):
            b[m] = turn
            scores.append(value(b, "X" if turn == "O" else "O", depth + 1))
            b[m] = ""
        return max(scores) if turn == "O" else min(scores)

    return _pick(board, player, lambda b, nxt: value(b, nxt, 1)) + (nodes,)


def alphabeta(board, player="O"):
    """Minimax with Alpha-Beta pruning: same answer, fewer nodes."""
    nodes = 0

    def value(b, turn, depth, alpha, beta):
        nonlocal nodes
        nodes += 1
        if winner(b):
            return utility(b, depth)
        best = -math.inf if turn == "O" else math.inf
        for m in moves(b):
            b[m] = turn
            v = value(b, "X" if turn == "O" else "O", depth + 1, alpha, beta)
            b[m] = ""
            if turn == "O":
                best, alpha = max(best, v), max(alpha, v)
            else:
                best, beta = min(best, v), min(beta, v)
            if alpha >= beta:
                break  # prune: the opponent will never let the game reach here
        return best

    return _pick(board, player, lambda b, nxt: value(b, nxt, 1, -math.inf, math.inf)) + (nodes,)


def _pick(board, player, score):
    """Try every move for `player` and keep the best one."""
    b, nxt = list(board), "X" if player == "O" else "O"
    best_move, best_val = None, None
    for m in moves(b):
        b[m] = player
        v = score(b, nxt)
        b[m] = ""
        better = best_val is None or (v > best_val if player == "O" else v < best_val)
        if better:
            best_move, best_val = m, v
    return best_move, best_val


ALGORITHMS = {"Minimax": minimax, "Alpha-Beta pruning": alphabeta}
