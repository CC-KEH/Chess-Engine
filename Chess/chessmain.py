import pygame as p
from Chess.chess_engine import *

"""
This is main driver file, responsible for handling user input and displaying current GameState object.
"""


WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


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
    colors = [p.Color("white"), p.Color("gray")]

    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(
                screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            )


def draw_pieces(screen,board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece!='--':
                screen.blit(IMAGES[piece],p.Rect(col*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))



def draw_game_state(screen, game_state):
    draw_board(screen)
    draw_pieces(screen, game_state.board)


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    game_state = GameState()
    load_images()
    running = True
    sq_selected = () # No square is selected in the beginning
    player_clicks = [] # Keep track of player clicks [(row,col),(row,col)] only 2 tuples: source and destination
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location  = p.mouse.get_pos() # location of mouse click
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                
                #* Player clicked on the same piece twice, might wanna add undo highlighting here
                if sq_selected == (row,col):
                    sq_selected = ()
                    player_clicks = []
                else:
                    sq_selected = (row,col)
                    player_clicks.append(sq_selected)

                if len(player_clicks)==2:
                    # This is the destination click
                    # move from player_clicks[0] to player_clicks[1]
                    move = Move(player_clicks[0],player_clicks[1],game_state.board)
                    print(move.get_chess_notation())
                    game_state.make_move(move)
                    sq_selected = ()
                    player_clicks = []
                    
        draw_game_state(screen, game_state)
        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == "__main__":
    main()
