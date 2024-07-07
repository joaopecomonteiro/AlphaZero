import sys
import numpy as np
import time
import pygame
import math
import random

from .tensorflow.NNet import NNetWrapper as nn
sys.path.append('../..')
from Go.MCTS import MCTS
from Go.utils import *

SQUARE_SIZE = 75

models_folder = "C:/Users/joaom/Desktop/trabalho2_liacd/Go/models"

class GreedyPlayer():
    """
    Classe para o jogador greedy (joga uma das jogadas que lhe dá melhor pontuação)
    """
    def __init__(self, game):
        self.game = game

    def play(self, board, curPlayer, screen=None):

        if board.consecutive_pass_count > 0 and curPlayer*self.game.get_greedy_score(board, 1) > 0:
            return self.game.size*self.game.size

        valids = self.game.getValidMoves(board, 1)
        candidates = []
        for a in range(self.game.getActionSize()):
            if valids[a]==1:
                next_board, _ = self.game.getNextState(board, 1, a)
                score = self.game.get_greedy_score(next_board, 1)
                candidates.append((-score, a))
        candidates.sort()
        best_score = candidates[0][0]
        best_actions = []
        for score, action in candidates:
            if score == best_score:
                best_actions.append(action)
        return random.choice(best_actions)


class HumanPlayer():
    """
    Classe para o jogador humano
    """

    def __init__(self, game):
        self.game = game

    def play(self, board, player, screen=None):
        pygame.init()
        valid = self.game.getValidMoves(board, 1)
        start_time = time.time()
        while True:
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    posy = event.pos[0]
                    y = int(math.floor(posy/SQUARE_SIZE)) 
                    posx = event.pos[1]
                    x = int(math.floor(posx/SQUARE_SIZE)) 
                    try:
                        if ((0 <= x) and (x < self.game.size) and (0 <= y) and (y < self.game.size)) or \
                            ((x == self.game.size) and (y == 0)):
                            a = self.game.size * x + y if x != -1 else self.game.size ** 2
                        if valid[a]:
                            return a
                        else:
                            print("invalid move")
                    except ValueError:
                        'Invalid integer'
                        
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:

                        return self.game.size*self.game.size
            end_time = time.time()
            elapsed_time = end_time - start_time

            if elapsed_time >= 10:
                print(f"out of time -> {elapsed_time}")
                return None
        
    
class G7x7():
    """
    Classe para o jogador de go 7x7
    """
    def __init__(self, game):
        self.game = game
        self.nnet = nn(game)
        self.nnet.load_model(models_folder, 'G7x7.h5')
    
    def play(self, board, player,  screen=None):
        if board.consecutive_pass_count > 0 and player*self.game.get_greedy_score(board, 1) > 0:
            return board.n*board.n
        
        args = dotdict({'numMCTSSims': 25, 'cpuct': 1.0})
        mcts = MCTS(self.game, self.nnet, args)

        return np.argmax(mcts.getActionProb(board, temp=0))


class G9x9():
    """
    Classe para o jogador de go 9x9
    """
    def __init__(self, game):
        self.game = game
        self.nnet = nn(game)
        self.nnet.load_model(models_folder, 'G9x9.h5')
    
    def play(self, board, player, screen=None):
        if board.consecutive_pass_count > 0 and player*self.game.get_greedy_score(board, 1) > 0:
            return board.n*board.n
        
        args = dotdict({'numMCTSSims': 25, 'cpuct': 1.0})
        mcts = MCTS(self.game, self.nnet, args)

        return np.argmax(mcts.getActionProb(board, temp=0))