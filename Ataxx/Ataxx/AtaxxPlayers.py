import numpy as np
import time
import pygame
import sys
import math
import random

from .tensorflow.NNet import NNetWrapper as nn
from .tensorflow_flex.NNetFlex import NNetWrapperFlex as nnflex
from Ataxx.MCTS import MCTS
from Ataxx.utils import *

SQUARE_SIZE = 75

models_folder = "C:/Users/joaom/Desktop/trabalho2_liacd/Ataxx/models"

class GreedyPlayer():
    """
    Classe para o jogador greedy (joga uma das jogadas que lhe dá melhor pontuação)
    """
    def __init__(self, game):
        self.game = game

    def play(self, board, player, screen):
        valids = self.game.getValidMoves(board, 1)
        candidates = []
        for a in range(self.game.getActionSize()):
            if valids[a]==1:
                next_board, _ = self.game.getNextState(board, 1, a)
                score = self.game.getScore(next_board, 1)
                candidates.append((-score, a))
        candidates.sort()
        best_score = candidates[0][0]
        best_actions = []
        for score, action in candidates:
            if score == best_score:
                best_actions.append(action)

        return int(random.choice(best_actions))


class A4x4():
    """
    Classe para o jogador de ataxx 4x4
    """
    def __init__(self, game):
        self.game = game
        self.nnet = nn(game)
        self.nnet.load_model(models_folder, 'A4x4.h5')
    
    def play(self, board, player, screen):
        args = dotdict({'numMCTSSims': 25, 'cpuct': 1.0})
        mcts = MCTS(self.game, self.nnet, args)
        return int(np.argmax(mcts.getActionProb(board, temp=0)))


class A5x5():
    """
    Classe para o jogador de ataxx 5x5
    """
    def __init__(self, game):
        self.game = game
        self.nnet = nn(game)
        self.nnet.load_model(models_folder, 'A5x5.h5')
    
    def play(self, board, player, screen):
        args = dotdict({'numMCTSSims': 25, 'cpuct': 1.0})
        mcts = MCTS(self.game, self.nnet, args)
        return int(np.argmax(mcts.getActionProb(board, temp=0)))


class A6x6():
    """
    Classe para o jogador de ataxx 5x5
    """
    def __init__(self, game):
        self.game = game
        self.nnet = nn(game)
        self.nnet.load_model(models_folder, 'A6x6.h5')
    
    def play(self, board, player, screen):
        args = dotdict({'numMCTSSims': 25, 'cpuct': 1.0})
        mcts = MCTS(self.game, self.nnet, args)
        return int(np.argmax(mcts.getActionProb(board, temp=0)))


class AFlex():
    """
    Classe para o jogador de ataxx com tamanho do tabuleiro variável
    """
    def __init__(self, game):
        self.game = game
        self.nnet = nn(game)
        self.nnet.load_model(models_folder, 'AFlex.h5')
    
    def play(self, board, player, screen):
        target_shape = (6, 6)
        pad_width = [(0, max(0, target_shape[i] - board.shape[i])) for i in range(len(target_shape))]
        padded_board = np.pad(board, pad_width, mode='constant', constant_values=9)
        args = dotdict({'numMCTSSims': 25, 'cpuct': 1.0})
        mcts = MCTS(self.game, self.nnet, args, flex=True)
        return int(np.argmax(mcts.getActionProb(padded_board, temp=0)))


class HumanPlayer():
    """
    Classe para o jogador humano

    Este jogador tem um limite de 10 segundos para jogar, quando terminar esse tempo retorna 0
    A razão desta limitação tem que ver com o limite de tempo que o servidor dá a cada jogador para jogar, 
    se o tempo não fosse contabilizado do cliente podia dar-se o caso de ter mudado o turno e este ainda estar a jogar
    """
    def __init__(self, game):
        self.game = game

    def change_board(self, board, x, y):
        """
        Função para preencher as casas para onde o jogador pode jogar(tendo em conta a peça que escolheu) 
        com 3 para aparecerem com um circulo cinzento na interface
        """
        new_board = np.copy(board)
        for i in range(-2, 3):
            for j in range(-2, 3):
                if x+i >= 0 and x+i < len(board) and j+y >= 0 and j+y < len(board):
                    if board[x+i][j+y] == 0:
                        new_board[x+i][j+y] = 3
        return new_board

    def change_board_back(self, board):
        """
        Função para retirar os 3 do tabuleiro após o jogador terminar a jogada ou escolher outra peça
        """
        new_board = np.copy(board)
        new_board[new_board == 3] = 0
        return new_board


    def play(self, board, player, screen):
        """
        A funcionalidade dos clicks serve para verificar se o jogador já escolheu a peça que quer jogar, 
        se ainda não escolheu clicks=0, se já escolheu clicks=1
        Isto é importante para a visualização dos circulos cinzentos após ser selecionada uma peça
        """
        pygame.init()
        valid = self.game.getValidMoves(board, 1)
        clicks = 0
        start_time = time.time()
        while True:
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if clicks == 0:
                        posy = event.pos[0]
                        y1 = int(math.floor(posy/SQUARE_SIZE)) 
                        posx = event.pos[1]
                        x1 = int(math.floor(posx/SQUARE_SIZE)) 
                        print(x1, y1)
                        if board[x1][y1] == 1:
                            board = self.change_board(board, x1, y1)
                            self.game.display(player*board, screen)
                            clicks = 1

                    elif clicks == 1:
                        posy = event.pos[0]
                        y2 = int(math.floor(posy/SQUARE_SIZE)) 
                        posx = event.pos[1]
                        x2 = int(math.floor(posx/SQUARE_SIZE)) 
                        print(x2, y2)
                        if ((0 <= x2) and (x2 < self.game.size) and (0 <= y2) and (y2 < self.game.size)) or \
                            ((x2 == self.game.size) and (y2 == 0)):
                            a = self.game.size * x2 + y2 if x2 != -1 else self.game.size ** 2
                        if valid[a]:
                            return (x1, y1, x2, y2)
                        else:
                            board = self.change_board_back(board)
                            self.game.display(player*board, screen)
                            clicks = 0
                            print("invalid move")
            end_time = time.time()
            elapsed_time = end_time - start_time

            if elapsed_time >= 10:
                print(f"out of time -> {elapsed_time}")
                return None