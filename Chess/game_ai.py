import random
import re
from shutil import move
from chess_engine import GameState
from multiprocessing import Queue

piece_scores={'K': 0,'P': 1,'R': 5,'N': 3,'B': 3,'Q': 10}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2


def score_material(game_state:GameState):
    score = 0
    for row in game_state.board:
        for square in row:
            if square[0]=='w':
                score+=piece_scores[square[1]]
            else:
                score-=piece_scores[square[1]]
    return score

def score_board(game_state:GameState):
    if game_state.in_check_mate:
        if game_state.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif game_state.in_stale_mate:
        return STALEMATE
    
    score = 0
    for row in game_state.board:
        for square in row:
            if square[0]=='w':
                score+=piece_scores[square[1]]
            elif square[0]=='b':
                score-=piece_scores[square[1]]
    return score

def random_move(valid_moves):
    return valid_moves[random.randint(0,len(valid_moves)-1)]

# main move function
def find_best_move(game_state:GameState,valid_moves,thread_storage,nega_max = True):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    if not nega_max:
        find_move_min_max(game_state,valid_moves,DEPTH, game_state.white_to_move)
    else:
        find_move_nega_max_alpha_beta(game_state,valid_moves,DEPTH,-CHECKMATE,CHECKMATE, 1 if game_state.white_to_move else -1)
    
    thread_storage.put(next_move)

# Min Max
def find_move_min_max(game_state:GameState,valid_moves,depth,white_to_move):
    global next_move
    if depth==0:
        return score_material(game_state.board)    
    
    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            game_state.make_move(move)
            opponent_moves = game_state.get_valid_moves()
            score = find_move_min_max(game_state,opponent_moves,depth-1,False)
            if score>max_score:
                max_score = score
                if depth==DEPTH:
                    next_move = move
            game_state.undo_move()
        return max_score
    else:
        min_score = CHECKMATE
        for move in valid_moves:
            game_state.make_move(move)
            opponent_moves = game_state.get_valid_moves()
            score = find_move_min_max(game_state,opponent_moves,depth-1,True)
            if score<min_score:
                min_score = score
                if depth==DEPTH:
                    next_move = move
            game_state.undo_move()
        return min_score

# Optimised Min Max
def find_move_nega_max(game_state:GameState,valid_moves,depth,turn_multiplier):
    global next_move
    if depth==0:
        return turn_multiplier*score_board(game_state)
    max_score = -CHECKMATE
    for move in valid_moves:
        game_state.make_move(move)
        opponent_moves = game_state.get_valid_moves()
        
        # - in score, best score of opponent is worst for us
        score = -find_move_nega_max(game_state,opponent_moves,depth-1,-turn_multiplier)
        if score>max_score:
            max_score = score
            if depth==DEPTH:
                next_move = move
        
        game_state.undo_move()
        
    return max_score

# Alpha beta pruning
def find_move_nega_max_alpha_beta(game_state:GameState,valid_moves,depth,alpha,beta,turn_multiplier):
    global next_move
    if depth==0:
        return turn_multiplier*score_board(game_state)
    max_score = -CHECKMATE
    for move in valid_moves:
        game_state.make_move(move)
        opponent_moves = game_state.get_valid_moves()
        
        # - in score, best score of opponent is worst for us
        score = -find_move_nega_max_alpha_beta(game_state,opponent_moves,depth-1,-beta,-alpha,-turn_multiplier)
        
        if score>max_score:
            max_score = score
            if depth==DEPTH:
                next_move = move
        
        game_state.undo_move()
        if max_score > alpha:
             alpha = max_score
        
        if alpha>=beta:
            break
    return max_score
