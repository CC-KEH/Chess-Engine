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
        self.castle_rights_log = [CastleRights(self.current_castle_right.wks,self.current_castle_right.wqs,self.current_castle_right.bks,self.current_castle_right.bqs)]
        self.enpassant_possible = ()
        self.enpassant_possible_log = [self.enpassant_possible]

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
            self.white_king_location = (move.dst_row, move.dst_col)

        elif move.piece_moved == "bK":
            self.black_king_location = (move.dst_row, move.dst_col)
        
        # Pawn Promotion
        if move.can_promote_pawn:
            self.board[move.dst_row][move.dst_col] = move.piece_moved[0] + 'Q'
        
        # enpassant Move
        if move.is_enpassant_move:
            self.board[move.src_row][move.dst_col] = '--'
        
        
        if move.piece_moved[1]=='P' and abs(move.src_row - move.dst_row)==2:
            self.enpassant_possible = ((move.src_row+move.dst_row)//2,move.dst_col)
        else:
            self.enpassant_possible = ()
        
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
        
        self.enpassant_possible_log.append(self.enpassant_possible)
        
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castle_right.wks,self.current_castle_right.wqs,self.current_castle_right.bks,self.current_castle_right.bqs))
        
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

            # Undo enpassant Move
            if move.is_enpassant_move:
                self.board[move.dst_row][move.dst_col] = '--'
                self.board[move.src_row][move.dst_col] = move.piece_captured
            
            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]
            
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
            
            self.in_check_mate = False
            self.in_stale_mate = False

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
        
        # If rook is captured
        if move.piece_captured == 'wR':
            if move.dst_row == 7:
                if move.dst_col == 0:
                    self.current_castle_right.wqs = False
                elif move.dst_col == 7:    
                    self.current_castle_right.wks = False
        
        elif move.piece_captured == 'bR':
            if move.dst_row == 0:
                if move.dst_col == 0:
                    self.current_castle_right.wqs = False
                elif move.dst_col == 7:    
                    self.current_castle_right.wks = False
        
    def get_valid_moves(self):
        temp_castle_rights = CastleRights(self.current_castle_right.wks,self.current_castle_right.bks,self.current_castle_right.wqs,self.current_castle_right.bqs)
        
        moves = []
        self.in_check,self.pins,self.checks = self.check_for_pins_and_checks()
      
        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.in_check:
            if len(self.checks) == 1:  # only 1 check, block the check or move the king
                moves = self.get_possible_moves()
                # to block the check you must put a piece into one of the squares between the enemy piece and your king
                check = self.checks[0]  # check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []  # squares that pieces can move to
                # if knight, must capture the knight or move your king, other pieces can be blocked
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i,
                                        king_col + check[3] * i)  # check[2] and check[3] are the check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[
                            1] == check_col:  # once you get to piece and check
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # iterate through the list backwards when removing elements
                    if moves[i].piece_moved[1] != "K":  # move doesn't move king so it must block or capture
                        if not (moves[i].dst_row,
                                moves[i].dst_col) in valid_squares:  # move doesn't block or capture piece
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.getKingMoves(king_row, king_col, moves)
        else:  # not in check - all moves are fine
            moves = self.get_possible_moves()
            if self.white_to_move:
                self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
            else:
                self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)

        if len(moves) == 0:
            if self.is_in_check():
                self.checkmate = True
            else:
                # TODO stalemate on repeated moves
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.current_castling_rights = temp_castle_rights
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

    def get_pawn_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            move_amount = -1
            start_row = 6
            enemy_color = "b"
            king_row, king_col = self.white_king_location
        else:
            move_amount = 1
            start_row = 1
            enemy_color = "w"
            king_row, king_col = self.black_king_location

        if self.board[row + move_amount][col] == "--":  # 1 square pawn advance
            if not piece_pinned or pin_direction == (move_amount, 0):
                moves.append(Move((row, col), (row + move_amount, col), self.board))
                if row == start_row and self.board[row + 2 * move_amount][col] == "--":  # 2 square pawn advance
                    moves.append(Move((row, col), (row + 2 * move_amount, col), self.board))
        if col - 1 >= 0:  # capture to the left
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[row + move_amount][col - 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col - 1), self.board))
                if (row + move_amount, col - 1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col - 1)
                            outside_range = range(col + 1, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col, -1)
                            outside_range = range(col - 2, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col - 1), self.board, is_enpassant_move=True))
        if col + 1 <= 7:  # capture to the right
            if not piece_pinned or pin_direction == (move_amount, +1):
                if self.board[row + move_amount][col + 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col + 1), self.board))
                if (row + move_amount, col + 1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col)
                            outside_range = range(col + 2, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col + 1, -1)
                            outside_range = range(col - 1, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col + 1), self.board, is_enpassant_move=True))
     
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
            if not self.square_under_attack(r,c+1) and not self.square_under_attack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,is_castle_move=True))
                
    def get_queen_side_castle_moves(self,r,c,moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.square_under_attack(r,c-1) and not self.square_under_attack(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board,is_castle_move=True))
             
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

    def __init__(self, source, destination, board,is_enpassant_move = False,is_castle_move = False):
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
        # enpassant 
        self.is_enpassant_move = is_enpassant_move
        self.is_capture = self.piece_captured != "--"
        if self.is_enpassant_move:
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
    
    def __str__(self):
        if self.is_castle_move:
            return "0-0" if self.end_col == 6 else "0-0-0"

        end_square = self.get_rank_file(self.dst_row, self.dst_col)

        if self.piece_moved[1] == "p":
            if self.is_capture:
                return self.cols_to_files[self.src_col] + "x" + end_square
            else:
                return end_square + "Q" if self.is_pawn_promotion else end_square

        move_string = self.piece_moved[1]
        if self.is_capture:
            move_string += "x"
        return move_string + end_square