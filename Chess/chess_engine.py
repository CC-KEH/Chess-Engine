"""
Stores all information about current staet of game, It will also be responsible for determining the valid chess moves at current state, also keep a move log.
"""
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
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = False
        self.in_stale_mate = False
        self.in_check_mate = False
        self.pins = []
        self.checks = []
        self.current_castle_right = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castle_right.wks,self.current_castle_right.wqs,self.current_castle_right.bks,self.current_castle_right.bqs,)]
        self.empassant_possible = ()

    def square_under_attack(self,r,c):
        self.white_to_move = not self.white_to_move
        opp_moves = self.get_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opp_moves:
            if move.dst_row == r and move.dst_col==c:
                return True
        return False        
    
    def is_in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0],self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0],self.black_king_location[1])
    
    def make_move(self, move):
        self.board[move.src_row][move.src_col] = "--"
        self.board[move.dst_row][move.dst_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        if move.piece_moved == "wK":
            self.white_king_location = (self.dst_row, self.dst_col)

        elif move.piece_moved == "bK":
            self.black_king_location = (self.dst_row, self.dst_col)
        
        # Pawn Promotion
        if move.can_promote_pawn:
            self.board[move.dst_row][move.dst_col] = move.piece_moved[0] + 'Q'
        
        # Empassant Move
        if move.is_empassant_move:
            self.board[move.src_row][move.dst_col] = '--'
        
        
        if move.piece_moved[1]=='P' and abs(move.src_row - move.dst_row)==2:
            self.empassant_possible = ((move.src_row+move.dst_row)//2,move.src_col)
        else:
            self.empassant_possible = ()
        
        if move.is_castle_move:
            if move.dst_col - move.src_col==2:
                # king side castle
                # moves the rook
                self.board[move.dst_row][move.dst_col-1] = self.board[move.dst_row][len(self.board[0])-1]
                self.board[move.dst_row][move.dst_col+1] = '--' #erase old rook
                
            else:
                # queen side castle
                # moves the rook
                self.board[move.dst_row][move.dst_col+1] = self.board[move.dst_row][move.dst_col-2]
                self.board[move.dst_row][move.dst_col-2] = '--'
        
        self.update_castle_rights(move)
        self.castle_rights_log.append([CastleRights(self.current_castle_right.wks,self.current_castle_right.wqs,self.current_castle_right.bks,self.current_castle_right.bqs,)])
        
    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.src_row][move.src_col] = move.piece_moved
            self.board[move.dst_row][move.dst_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            
            if move.piece_moved == "wK":
                self.white_king_location = (move.src_row, move.src_col)

            elif move.piece_moved == "bK":
                self.black_king_location = (move.src_row, move.src_col)

            # Undo Empassant Move
            if move.is_empassant_move:
                self.board[move.dst_row][move.dst_col] = '--'
                self.board[move.src_row][move.dst_col] = move.piece_captured
                self.empassant_possible = (move.dst_row, move.dst_col)
            
            # Undo 2 Square pawn advantage
            if move.piece_moved[1]=='P' and abs(move.src_row - move.dst_row)==2:
                self.empassant_possible = ()
            
            # undo castle rights
            self.castle_rights_log.pop()
            self.current_castle_right = self.castle_rights_log[-1]
            # undo castle move
            if move.is_castle_move:
                if move.dst_col - move.src_col==2:
                    self.board[move.dst_row][move.dst_col+1] = self.board[move.dst_row][move.dst_col-1] 
                    self.board[move.dst_row][move.dst_col-1] = '--'
                    
                else:
                    self.board[move.dst_row][move.dst_col-2] = self.board[move.dst_row][move.dst_col+1] 
                    self.board[move.dst_row][move.dst_col+1] = '--'

    def update_castle_rights(self,move):
        if move.piece_moved=='wK':
            self.current_castle_right.wks = False
            self.current_castle_right.wqs = False
        elif move.piece_moved=='bK':
            self.current_castle_right.bks = False
            self.current_castle_right.bqs = False
        elif move.piece_moved=='wR':
            if move.src_row==7:
                if move.src_col==0:
                    self.current_castle_right.wqs = False
                elif move.src_col==7:
                    self.current_castle_right.wks = False            
        elif move.piece_moved=='bR':
            if move.src_row==0:
                if move.src_col==0:
                    self.current_castle_right.bqs = False
                elif move.src_col==7:
                    self.current_castle_right.bks = False
        
    def get_valid_moves(self):
        temp_empassant_possible = self.empassant_possible
        temp_castle_rights = CastleRights(self.current_castle_right.wks,self.current_castle_right.bks,self.current_castle_right.wqs,self.current_castle_right.bqs)
        
        moves = self.get_possible_moves()
        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0],self.white_king_location[1],moves)
        else:
            self.get_castle_moves(self.black_king_location[0],self.black_king_location[1],moves)
        
        for i in range(len(moves)-1,-1,-1):
            self.make_move(moves[i])
            # generate all opponent moves
            # for each move, check if it attacks our king
            self.white_to_move = not self.white_to_move
            if self.is_in_check():
                moves.remove(moves[i]) # If they can attack the king this is not a valid move for you then
            self.white_to_move = not self.white_to_move
            self.undo_move()
            
        # Left with no valid moves
        if len(moves)==0:
            if self.is_in_check():
                self.in_check_mate = True
            else:
                self.in_stale_mate = True

        self.empassant_possible = temp_empassant_possible
        self.current_castle_right = temp_castle_rights
        return moves

    def check_for_pins_and_checks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            src_row = self.white_king_location[0]
            src_col = self.white_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            src_row = self.black_king_location[0]
            src_col = self.black_king_location[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = (
            (-1, 0),
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        )
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                dst_row = src_row + direction[0] * i
                dst_col = src_col + direction[1] * i
                if 0 <= dst_row <= 7 and 0 <= dst_col <= 7:
                    destination_piece = self.board[dst_row][dst_col]
                    if destination_piece[0] == ally_color and destination_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (
                                dst_row,
                                dst_col,
                                direction[0],
                                direction[1],
                            )
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif destination_piece[0] == enemy_color:
                        enemy_type = destination_piece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (
                            (0 <= j <= 3 and enemy_type == "R")
                            or (4 <= j <= 7 and enemy_type == "B")
                            or (
                                i == 1
                                and enemy_type == "p"
                                and (
                                    (enemy_color == "w" and 6 <= j <= 7)
                                    or (enemy_color == "b" and 4 <= j <= 5)
                                )
                            )
                            or (enemy_type == "Q")
                            or (i == 1 and enemy_type == "K")
                        ):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append(
                                    (dst_row, dst_col, direction[0], direction[1])
                                )
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knight_moves = (
            (-2, -1),
            (-2, 1),
            (-1, 2),
            (1, 2),
            (2, -1),
            (2, 1),
            (-1, -2),
            (1, -2),
        )
        for move in knight_moves:
            dst_row = src_row + move[0]
            dst_col = src_col + move[1]
            if 0 <= dst_row <= 7 and 0 <= dst_col <= 7:
                destination_piece = self.board[dst_row][dst_col]
                if (
                    destination_piece[0] == enemy_color and destination_piece[1] == "N"
                ):  # enemy knight attacking a king
                    in_check = True
                    checks.append((dst_row, dst_col, move[0], move[1]))
        return in_check, pins, checks

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
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            if self.board[r - 1][c] == "--":
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))

                    # 2 cell movement
                    if r == 6 and self.board[r - 2][c] == "--":
                        moves.append(Move((r, c), (r - 2, c), self.board))

            if c - 1 >= 0:  # Capture Left
                if self.board[r - 1][c - 1][0] == "b":
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r-1,c-1)==self.empassant_possible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board,is_empassant_move=True))
                    
            if c + 1 < len(self.board[0]):  # Capture Right
                if self.board[r - 1][c + 1][0] == "b":
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                    elif (r-1,c+1)==self.empassant_possible:
                        moves.append(Move((r, c), (r - 1, c + 1), self.board,is_empassant_move=True))
        else:
            if self.board[r + 1][c] == "--":
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    # 2 cell movement
                    if r == 1 and self.board[r + 2][c] == "--":
                        moves.append(Move((r, c), (r + 2, c), self.board))

            if c - 1 >= 0:  # Capture Left
                if self.board[r + 1][c - 1][0] == "w":
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                    elif (r+1,c-1)==self.empassant_possible:
                        moves.append(Move((r, c), (r + 1, c - 1), self.board,is_empassant_move=True))
            
            if c + 1 < len(self.board[0]):  # Capture Right
                if self.board[r + 1][c + 1][0] == "w":
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                    elif (r+1,c+1)==self.empassant_possible:
                        moves.append(Move((r, c), (r + 1, c + 1), self.board,is_empassant_move=True))
            
    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if (
                    self.board[r][c][1] != "Q"
                ):  # Since we are also calculating Queen movements with this func
                    self.pins.remove(self.pins[i])
                break

        directions = (
            (0, -1),  # Left
            (1, 0),  # Down
            (-1, 0),  # Up
            (0, 1),  # Right
        )
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                dst_row = r + d[0] * i
                dst_col = c + d[1] * i
                if 0 <= dst_row < len(self.board[0]) and 0 <= dst_col < len(
                    self.board[0]
                ):
                    if (
                        not piece_pinned
                        or pin_direction == d
                        or pin_direction == (-d[0], -d[1])
                    ):
                        destination_piece = self.board[dst_row][dst_col]

                        if destination_piece == "--":  # Empty Cell
                            moves.append(Move((r, c), (dst_row, dst_col), self.board))

                        elif destination_piece[0] == enemy_color:  # Enemy Piece
                            moves.append(Move((r, c), (dst_row, dst_col), self.board))
                            break  # Cannot move further

                        else:  # Friendly Piece
                            break
                else:
                    break


    def get_knight_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
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
        ally_color = "w" if self.white_to_move else "b"
        for d in directions:
            dst_row = r + d[0]
            dst_col = c + d[1]
            if 0 <= dst_row < len(self.board[0]) and 0 <= dst_col < len(self.board[0]):
                if not piece_pinned:
                    destination_piece = self.board[dst_row][dst_col]
                    if destination_piece[0] != ally_color:  # Enemy Piece
                        moves.append(Move((r, c), (dst_row, dst_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = (
            (-1, -1),  # up - left
            (1, 1),  # down - right
            (-1, 1),  # up - right
            (1, -1),  # down - left
        )
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                dst_row = r + d[0] * i
                dst_col = c + d[1] * i
                if 0 <= dst_row < len(self.board[0]) and 0 <= dst_col < len(
                    self.board[0]
                ):
                    if (
                        not piece_pinned
                        or pin_direction == d
                        or pin_direction == (-d[0], -d[1])
                    ):
                        destination_piece = self.board[dst_row][dst_col]

                        if destination_piece == "--":  # Empty Cell
                            moves.append(Move((r, c), (dst_row, dst_col), self.board))

                        elif destination_piece[0] == enemy_color:  # Enemy Piece
                            moves.append(Move((r, c), (dst_row, dst_col), self.board))
                            break  # Cannot move further

                        else:  # Friendly Piece
                            break
                else:
                    break

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

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
        ally_color = "w" if self.white_to_move else "b"
        for d in directions:
            dst_row = r + d[0]
            dst_col = c + d[1]
            if 0 <= dst_row < len(self.board[0]) and 0 <= dst_col < len(self.board[0]):
                destination_piece = self.board[dst_row][dst_col]
                if destination_piece[0] != ally_color:
                    if ally_color == "w":  # Empty Cell
                        self.white_king_location = (dst_row, dst_col)
                    else:
                        self.black_king_location = (dst_row, dst_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:  # Enemy Piece
                        moves.append(Move((r, c), (dst_row, dst_col), self.board))
                    if ally_color == "w":
                        self.white_king_location = (r, c)
                    else:
                        self.black_king_location = (r, c)
                  
    def get_castle_moves(self,r,c,moves):
        if self.square_under_attack(r,c):
            return
        if (self.white_to_move and self.current_castle_right.wks) or (not self.white_to_move and self.current_castle_right.bks):
            self.get_king_side_castle_moves(r,c,moves)
        
        if (self.white_to_move and self.current_castle_right.wqs) or (not self.white_to_move and self.current_castle_right.bqs):
            self.get_queen_side_castle_moves(r,c,moves)
        
    def get_king_side_castle_moves(self,r,c,moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.is_cell_under_attack(r,c+1) and not self.is_cell_under_attack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,is_castle_move=True))
                
    def get_queen_side_castle_moves(self,r,c,moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.is_cell_under_attack(r,c-1) and not self.is_cell_under_attack(r,c-2) and not self.is_cell_under_attack(r,c-3):
                moves.append(Move((r,c),(r,c-3),self.board,is_castle_move=True))
             
class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, source, destination, board,is_empassant_move = False,is_castle_move = False):
        self.src_row = source[0]
        self.src_col = source[1]
        self.dst_row = destination[0]
        self.dst_col = destination[1]
        self.piece_moved = board[self.src_row][self.src_col]
        self.piece_captured = board[self.dst_row][self.dst_col]
        self.is_castle_move = is_castle_move
        self.move_id = (
            self.src_row * 1000
            + self.src_col * 100
            + self.dst_row * 10
            + self.dst_col
        )
        # Pawn Promotion
        self.can_promote_pawn =  (self.piece_moved == "wP" and self.dst_row == 0) or (
            self.piece_moved == "bP" and self.dst_row == 7
        )
        # Empassant 
        self.is_empassant_move = is_empassant_move
        if self.is_empassant_move:
            self.piece_captured = 'wP' if self.piece_moved =='bP' else 'bP'

        
        
        
    def __eq__(self, other) -> bool:
        if isinstance(other, Move):
            return self.move_id == other.move_id
        else:
            return False

    def get_chess_notation(self):
        return self.get_rank_file(
            self.src_row, self.src_col
        ) + self.get_rank_file(self.dst_row, self.dst_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]