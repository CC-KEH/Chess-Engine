from concurrent.futures import thread
import glob
import pygame as p
from chess_engine import *
from game_ai import find_best_move,random_move
from multiprocessing import Process,Queue
"""
This is main driver file, responsible for handling user input and displaying current GameState object.
"""


BOARD_WIDTH = HEIGHT = 720
MOVE_LOGS_WIDTH = 300
MOVE_LOGS_HEIGHT = 270
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
WHITE_COLOR  = (245, 235, 218)
BLACK_COLOR  = (105, 79, 71)

def load_images():
    """
    Stores the pieces images in IMAGES dictionary.
    """
    pieces = ["bR", "bN", "bB", "bK", "bQ", "bP", "wR", "wN", "wB", "wK", "wQ", "wP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE)
        )

def draw_board(screen):
    global colors
    colors = [p.Color(245, 235, 218), p.Color(105, 79, 71)]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(
                screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            )

def draw_pieces(screen, board, for_white=True):
    if for_white:
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                piece = board[row][col]
                if piece != "--":
                    screen.blit(
                        IMAGES[piece],
                        p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE),
                    )
    else:
        for row in range(DIMENSION-1,-1,-1):
            for col in range(DIMENSION-1,-1,-1):
                piece = board[row][col]
                if piece != "--":
                    screen.blit(
                        IMAGES[piece],
                        p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE),
                    )
                    
def highlight_squares(screen,game_state,valid_moves,sq_selected):
    r,c = sq_selected
    if game_state.board[r][c][0]==('w' if game_state.white_to_move else 'b'):
        s = p.Surface((SQ_SIZE,SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('blue'))
        screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
        s.fill(p.Color('green'))
        for move in valid_moves:
            if move.src_row==r and move.src_col==c:
                screen.blit(s,(move.dst_col*SQ_SIZE,move.dst_row*SQ_SIZE))

def draw_game_state(screen, game_state,valid_moves,sq_selected,move_log_font,for_white=True):
    draw_board(screen)
    if sq_selected: highlight_squares(screen,game_state,valid_moves,sq_selected)
    draw_pieces(screen, game_state.board,game_state.white_to_move)
    draw_move_log(screen,game_state,move_log_font)
    draw_menu(screen)

def animate_move(game_state,screen,board,clock):
    global colors
    coords = [] # list of cords animation will move through
    move = game_state.move_log[-1]
    dR = move.dst_row - move.src_row
    dC = move.dst_col - move.src_col
    frames_per_square = 10
    frame_count = (abs(dR)+abs(dC))*frames_per_square
    for frame in range(frame_count+1):
        temp_r,temp_c = (move.src_row + dR*frame/frame_count,move.src_col + dC * frame/frame_count)
        draw_board(screen)
        draw_pieces(screen,board,game_state.white_to_move)
        color = colors[(move.dst_row+move.dst_col)%2]
        end_square = p.Rect(move.dst_col*SQ_SIZE,move.dst_row*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen,color,end_square)
        if move.piece_captured !='--':
            if move.is_enpassant_move:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col * SQ_SIZE, enpassant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        screen.blit(IMAGES[move.piece_moved],p.Rect(temp_c*SQ_SIZE,temp_r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(100)

def draw_text(screen,text):
    font = p.font.SysFont('Helvitca',32,True,False)
    text_object = font.render(text,0,p.Color('Black'))
    text_location = p.Rect(0,0,BOARD_WIDTH,HEIGHT).move(BOARD_WIDTH/2 - text_object.get_width()/2,HEIGHT/2-text_object.get_height()/2)
    screen.blit(text_object,text_location)

def draw_move_log(screen,game_state,font):
    move_log_rect = p.Rect(BOARD_WIDTH,HEIGHT-MOVE_LOGS_HEIGHT,MOVE_LOGS_WIDTH,MOVE_LOGS_HEIGHT)
    p.draw.rect(screen,p.Color(BLACK_COLOR),move_log_rect)
    move_log = game_state.move_log
    move_texts = move_log
    padding = 20
    text_X = padding
    heading = "Move Logs"
    text_object = font.render(heading,True,p.Color('white'))
    text_location = move_log_rect.move(MOVE_LOGS_WIDTH/2 - text_object.get_width()/2,padding)
    screen.blit(text_object,text_location)
    text_X+=text_object.get_height()
    for i in range(len(move_texts)):
        if text_X + font.get_height() >= MOVE_LOGS_WIDTH:
            text_X = padding + font.get_height()
            padding += 30
        move_no_str = i+1
        move = move_texts[i].get_chess_notation()
        text = str(move_no_str)+". " + str(move)
        text_object = font.render(text,True,p.Color('white'))
        text_location = move_log_rect.move(text_X,padding+50)
        screen.blit(text_object,text_location)
        text_X+=text_object.get_height() + 45

def draw_menu(screen):
    menu_rect = p.Rect(BOARD_WIDTH,0,MOVE_LOGS_WIDTH,HEIGHT-MOVE_LOGS_HEIGHT)
    p.draw.rect(screen,p.Color(WHITE_COLOR),menu_rect)
    heading_font = p.font.SysFont('Helvetica',30,True,False)
    font = p.font.SysFont('Helvetica',20,True,False)
    
    text = "PyChess"
    text_object = heading_font.render(text,True,p.Color(BLACK_COLOR))
    text_location = menu_rect.move(MOVE_LOGS_WIDTH/2 - text_object.get_width()/2,20)
    screen.blit(text_object,text_location)
    text = "Press 'r' to reset game"
    text_object = font.render(text,True,p.Color(BLACK_COLOR))
    text_location = menu_rect.move(MOVE_LOGS_WIDTH/2 - text_object.get_width()/2 - 17,90)
    screen.blit(text_object,text_location)
    text = "Press 'z' to undo move"
    text_object = font.render(text,True,p.Color(BLACK_COLOR))
    text_location = menu_rect.move(MOVE_LOGS_WIDTH/2 - text_object.get_width()/2 - 17,130)
    screen.blit(text_object,text_location)
    text = "Press 'm' to switch modes"
    text_object = font.render(text,True,p.Color(BLACK_COLOR))
    text_location = menu_rect.move(MOVE_LOGS_WIDTH/2 - text_object.get_width()/2,170)
    screen.blit(text_object,text_location)
    text = "Press 's' to switch sides"
    text_object = font.render(text,True,p.Color(BLACK_COLOR))
    text_location = menu_rect.move(MOVE_LOGS_WIDTH/2 - text_object.get_width()/2 - 10,210)
    screen.blit(text_object,text_location)


def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH+MOVE_LOGS_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    move_log_font = p.font.SysFont('Helvitca',25,False,False)
    game_state = GameState()
    valid_moves = game_state.get_valid_moves()
    move_made = False
    load_images()
    running = True
    animate = False
    sq_selected = ()  # No square is selected in the beginning
    player_clicks = []  # Keep track of player clicks [(row,col),(row,col)] only 2 tuples: source and destination
    game_over = False
    
    player_one = True # Play as white
    player_two = True # Play as black
    
    ai_thinking = False
    move_finder_process = None
    move_undone = False
    while running:
        human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)
        
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # location of mouse click
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    # * Player clicked on the same piece twice, might wanna add undo highlighting here
                    if sq_selected == (row, col) or col>=8:
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)

                    if len(player_clicks) == 2 and human_turn:
                        # This is the destination click
                        # move from player_clicks[0] to player_clicks[1]
                        move = Move(player_clicks[0], player_clicks[1], game_state.board)
                        print(move.get_chess_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.make_move(valid_moves[i])
                                sq_selected = ()
                                player_clicks = []
                                move_made = True
                                animate = True
                        if not move_made:
                            player_clicks = [sq_selected]  # Selected another piece
                            print("Invalid Move")
                            

            elif e.type == p.KEYDOWN:
                # Undo when 'z' is pressed
                if e.key == p.K_z:
                    game_state.undo_move()
                    move_made = True 
                    animate = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key == p.K_r: # Reset Game
                    game_state = GameState()   
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                    
                if e.key ==p.K_m:
                    game_state = GameState()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    player_one = True
                    player_two = True
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                    
                    
                if e.key == p.K_s:
                    game_state = GameState()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    player_one = not player_one
                    player_two = not player_two
                    if not player_one and not player_two:
                        player_one = True
                        
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                    
                
        # AI Move  
        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                thread_storage = Queue()
                move_finder_process = Process(target=find_best_move,args=(game_state,valid_moves,thread_storage))
                move_finder_process.start()
                ai_move = thread_storage.get()
                print(ai_move)
                
                               
            if move_finder_process.is_alive:
                if ai_move is None:
                    ai_move = random_move(valid_moves)
                game_state.make_move(ai_move)
                move_made = True
                animate = True
                ai_thinking = False
            
            
        if move_made:
            if animate:
                animate_move(game_state,screen,game_state.board,clock)
            valid_moves = game_state.get_valid_moves()
            move_made = False
            animate = False
            move_undone = False
            
        draw_game_state(screen, game_state, valid_moves, sq_selected, move_log_font, game_state.white_to_move)
        
        if game_state.in_check_mate:
            game_over = True
            if game_state.white_to_move:
                draw_text(screen,'Black wins by checkmate')
            else:
                draw_text(screen,'White wins by checkmate')
        elif game_state.in_stale_mate:
            game_over = True
            draw_text(screen,'Stalemate')
        
        
        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == "__main__":
    main()
