"""
Stores all information about current staet of game, It will also be responsible for determining the valid chess moves at current state, also keep a move log.
"""

from shutil import move


class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.white_to_move = True
        self.move_log = []
        self.piece_to_move_fxn = {
            "P": self.get_pawn_moves,
            "R": self.get_rook_moves,
            "N": self.get_knight_moves,
            "B": self.get_bishop_moves,
            "K": self.get_king_moves,
            "Q": self.get_queen_moves,
        }

    def make_move(self, move):
        self.board[move.source_row][move.source_col] = "--"
        self.board[move.destination_row][move.destination_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.source_row][move.source_col] = move.piece_moved
            self.board[move.destination_row][self.destination_col] = move.piece_captured
            self.white_to_move = not self.white_to_move

    def get_valid_moves(self):
        return self.get_possible_moves()

    def get_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[0])):
                piece_color = self.board[r][c][0]
                piece = self.board[r][c][1]
                if (piece_color == "w" and self.white_to_move) or (
                    piece_color == "b" and not self.white_to_move
                ):
                    self.piece_to_move_fxn[piece](
                        r, c, moves
                    )  # Calls the move function based on piece
        return moves

    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))

                # 2 cell movement
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))

            if c - 1 >= 0:  # Capture Left
                if self.board[r - 1][c - 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))

            if c + 1 < len(self.board[0]):  # Capture Right
                if self.board[r - 1][c + 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
        else:
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))

                # 2 cell movement
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))

            if c - 1 >= 0:  # Capture Left
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))

            if c + 1 < len(self.board[0]):  # Capture Right
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

    def get_rook_moves(self, r, c, moves):
        directions = (
            (0, -1),  # Left
            (1, 0),  # Down
            (-1, 0),  # Up
            (0, 1),  # Right
        )
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < len(self.board[0]) and 0 <= end_col < len(
                    self.board[0]
                ):
                    end_piece = self.board[end_row][end_col]

                    if end_piece == "--":  # Empty Cell
                        moves.append(Move((r, c), (end_row, end_col), self.board))

                    elif end_piece[0] == enemy_color:  # Enemy Piece
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break  # Cannot move further

                    else:  # Friendly Piece
                        break
                else:
                    break

    def get_knight_moves(self, r, c, moves):
        directions = (
            (-2, -1),
            (-2, 1),
            (2, -1),
            (2, 1),
            (-1, -2),
            (1, -2),
            (-1, 2),
            (1, 2),
        )
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            end_row = r + d[0]
            end_col = c + d[1]
            if 0 <= end_row < len(self.board[0]) and 0 <= end_col < len(self.board[0]):
                end_piece = self.board[end_row][end_col]
                if end_piece == "--":  # Empty Cell
                    moves.append(Move((r, c), (end_row, end_col), self.board))
                elif end_piece[0] == enemy_color:  # Enemy Piece
                    moves.append(Move((r, c), (end_row, end_col), self.board))
                    break  # Cannot move further
                else:  # Friendly Piece
                    break
            else:
                break

    def get_bishop_moves(self, r, c, moves):
        directions = (
            (-1, -1),  # up - left
            (1, 1),  # down - right
            (-1, 1),  # up - right
            (1, -1),  # down - left
        )
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < len(self.board[0]) and 0 <= end_col < len(
                    self.board[0]
                ):
                    end_piece = self.board[end_row][end_col]

                    if end_piece == "--":  # Empty Cell
                        moves.append(Move((r, c), (end_row, end_col), self.board))

                    elif end_piece[0] == enemy_color:  # Enemy Piece
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break  # Cannot move further

                    else:  # Friendly Piece
                        break
                else:
                    break

    def get_king_moves(self, r, c, moves):
        directions = (
            (0, -1),  # Left
            (1, 0),  # Down
            (-1, 0),  # Up
            (0, 1),  # Right
            (-1, -1),  # up - left
            (1, 1),  # down - right
            (-1, 1),  # up - right
            (1, -1),  # down - left
        )
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            end_row = r + d[0]
            end_col = c + d[1]
            if 0 <= end_row < len(self.board[0]) and 0 <= end_col < len(self.board[0]):
                end_piece = self.board[end_row][end_col]
                if end_piece == "--":  # Empty Cell
                    moves.append(Move((r, c), (end_row, end_col), self.board))
                elif end_piece[0] == enemy_color:  # Enemy Piece
                    moves.append(Move((r, c), (end_row, end_col), self.board))
                    break  # Cannot move further
                else:  # Friendly Piece
                    break
            else:
                break

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)


class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, source, destination, board):
        self.source_row = source[0]
        self.source_col = source[1]
        self.destination_row = destination[0]
        self.destination_col = destination[1]
        self.piece_moved = board[self.source_row][self.source_col]
        self.piece_captured = board[self.destination_row][self.destination_col]
        self.move_id = (
            self.source_row * 1000
            + self.source_col * 100
            + self.destination_row * 10
            + self.destination_col
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, Move):
            return self.move_id == other.move_id
        else:
            return False

    def get_chess_notation(self):
        return self.get_rank_file(
            self.source_row, self.source_col
        ) + self.get_rank_file(self.destination_row, self.destination_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
