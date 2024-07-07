from __future__ import print_function
import sys
sys.path.append('../..')
from Go.Game import Game

from .GoLogic import Board
import numpy as np 
import pygame
from copy import deepcopy

PLAYER2, EMPTY, PLAYER1, FILL, KO, UNKNOWN = range(-1, 5)

SQUARE_SIZE = 75 #Tamanho dos quadrados da interface

# PLAYER1 = 1
# PLAYER2 = -1

#Cores
BACKGROUND_COLOR = (240, 196, 52)
WHITE_COLOR = (255,255,255) 
BLACK_COLOR = (0,0,0) 
SQUARE_SIZE = 75

class GoGame(Game):
    """
    Classe para o jogo go
    """

    # Caracteres para a string do tabuleiro
    square_content = {
        -1: "X",
        +0: "-",
        +1: "O"
    }

    @staticmethod
    def getSquarePiece(piece):
        return GoGame.square_content[piece]


    def __init__(self, size):
        self.size = size
        self.consecutive_pass_count = 0
        self.visited_black = set()
        self.visited_white = set()

    def getInitBoard(self):
        """
        Função para obter o tabuleiro inicial
        """
        b = Board(self.size)
        return b

    def getBoardSize(self):
        """
        Função para obter o tamanho do tabuleiro
        """
        return (self.size, self.size)

    def getActionSize(self):
        """
        Função para obter o número de ações possiveis
        """
        return self.size * self.size + 1

    def getNextState(self, board, player, action):
        """
        Função para fazer a jogada, retorna o estado do tabuleiro depois da jogada e o próximo jogador

        Aceita jogadas no formato de um número inteiro, no formato (x, y) 
        No primeiro caso calcula a casa a que o número inteiro corresponde e executa o movimento, no segundo executa logo o movimento
        """
        if action == self.size*self.size or action==(9, 9):
            self.consecutive_pass_count += 1
            board.consecutive_pass_count += 1
            return(board, -player)
        
        b = deepcopy(board)

        if type(action) == int:
            move = (int(action/self.size), action%self.size)
        else:
            move = action

        b.execute_move(move, player)

        self.consecutive_pass_count = 0
        b.consecutive_pass_count = 0

        return (b, -player)
 

    def getValidMoves(self, board, player):
        """
        Função para obter os movimentos válidos, retorna uma array em que os movimentos válidos estão marcados com 1 e os inválidos com 0
        """
        valids = np.zeros(self.getActionSize()).astype(int)
        b = deepcopy(board)
        legalMoves = b.get_legal_moves(player)
        valids[-1]=1
        for x, y in legalMoves[:len(legalMoves)-1]:
            valids[self.size*x+y]=1
        return valids
    
    def getGameEnded(self, board, player, game_over = False, get_score=False):
        """
        Função para verificar se o jogo acabou tendo em conta a prespetiva de um determinado jogador,
        retorna 1 se esse jogador ganhou, -1 se perdeu ou None se o jogo ainda não acabou
        """
        b = deepcopy(board)
        if len(b.get_legal_moves(player))==1 or self.consecutive_pass_count >= 2  or board.consecutive_pass_count >= 2 or game_over:
            self.consecutive_pass_count = 0
            player1_score, player2_score = self.getScore(board)
            diff = player*(player1_score-player2_score)
            if diff > 0:
                if get_score:
                    return 1, player1_score, player2_score
                return 1
            elif diff < 0:
                if get_score:
                    return -1, player1_score, player2_score
                return -1
            
        return None

    def getCanonicalForm(self, board, player):
        """
        Função para obter o tabuleiro na sua forma canónica, as peças do jogador em questão ficam marcadas com 1 e do adversário com -1
        """
        b = deepcopy(board)
        b.pieces = player * b.pieces
        return b

    def getSymmetries(self, board, pi):
        """
        Função para obter as simetrias do tabuleiro para o treino do modelo
        """
        # mirror, rotational
        b = deepcopy(board)
        rotate_board = b.pieces
        assert(len(pi) == self.size**2+1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.size, self.size))
        l = []
        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(rotate_board, i)
                newPi = np.rot90(pi_board, i)
                if j:
                    newB = np.fliplr(newB)
                    newPi = np.fliplr(newPi)
                l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        return l
    

    def stringRepresentationReadable(self, board):
        """
        Função para obter o tabuleiro no formato string
        """
        board_s = "".join(self.square_content[square] for row in board.pieces for square in row)
        return board_s



    def is_valid_position(self, x, y):
        """
        Função para verificar se a posição (x, y) está dentro do tabuleiro
        """
        return 0 <= x < self.size and 0 <= y < self.size

    def count_territory(self, board, x, y, color):
        """
        Função para contar o território de um determinado jogador
        """

        if not self.is_valid_position(x, y) or board[x][y] == color:
            return 0
        
        if board[x][y] == 0:
            if color == PLAYER1:
                if (x, y) in self.visited_black:
                    return 0
                self.visited_black.add((x, y))
            else:
                if (x, y) in self.visited_white:
                    return 0
                self.visited_white.add((x, y))

        if board[x][y] == -color:
            return -np.inf

        return 1 + self.count_territory(board, x + 1, y, color) + self.count_territory(board, x - 1, y, color) + self.count_territory(board, x, y + 1, color) + self.count_territory(board, x, y - 1, color)

      
    def getScore(self, board):
        """
        Função para obter o resultado do jogo
        Está explicado ao certo como funciona no documento com as main features
        """
        black_score = 0
        white_score = 0
        
        b = deepcopy(board)

        self.visited_black.clear()
        self.visited_white.clear()
        
        minus_one_coords = [(i, j) for i in range(board.n) for j in range(board.n) if i==0 or j==0 or i==board.n-1 or j==board.n-1]
        if self.size == 7:
            plus_two_coords = [(1, 2), (2, 1), (2, 2), 
                               (1, 4), (2, 4), (2, 5), 
                               (4, 1), (4, 2), (5, 2), 
                               (4, 4), (4, 5), (5, 4)]
            
            plus_one_coords = [        (2, 3), 
                               (3, 2), (3, 3), (3, 4), 
                                       (4, 3)]

        elif self.size == 9:
            plus_two_coords = [(3, 1), (3, 2), (3, 3), (2, 3), (1, 3), 
                               (3, 7), (3, 6), (3, 5), (2, 5), (1, 5),
                               (5, 1), (5, 2), (5, 3), (6, 3), (7, 3),
                               (5, 7), (5, 6), (5, 5), (6, 5), (7, 5),]

            plus_one_coords = [        (2, 4), 
                                       (3, 4), 
                       (4, 2), (4, 3), (4, 4), (4, 5), (4, 6),
                                       (5, 4),
                                       (6, 4)]

        for i in range(self.size):
            for j in range(self.size):              
                stone = b.pieces[i][j]
                if stone == PLAYER1:
                    if (i, j) in minus_one_coords:
                        black_score -= 1
                    elif (i, j) in plus_two_coords:
                        black_score += 2 
                    elif (i, j) in plus_one_coords:
                        black_score += 1 
                    black_score += 1

                elif stone == PLAYER2:
                    if (i, j) in minus_one_coords:
                        white_score -= 1
                    elif (i, j) in plus_two_coords:
                        white_score += 2 
                    elif (i, j) in plus_one_coords:
                        white_score += 1 
                    white_score += 1


                elif stone == 0:
                    black_territory = self.count_territory(b.pieces, i, j, PLAYER1)
                    white_territory = self.count_territory(b.pieces, i, j, PLAYER2)

                    if black_territory >= 0:
                       black_score += black_territory 
                    if white_territory >= 0:
                       white_score += white_territory 

        white_score += board.komi

        return black_score, white_score
        
    def get_greedy_score(self, board, player):
        """
        Função para obter o resultado do jogo para fornecer ao jogador greedy
        """
        b_score, w_score = self.getScore(board)
        return player*(b_score-w_score)
        

    @staticmethod
    def display(b, screen):
        """
        Função para dar display ao tabuleiro
        """
        board = b.pieces
        size = len(board)
        for i in range(size -  1):
            pygame.draw.line(screen, BLACK_COLOR, ((i+1)*SQUARE_SIZE,0), ((i+1)*SQUARE_SIZE,SQUARE_SIZE*size), 2) 
            pygame.draw.line(screen, BLACK_COLOR, (0,(i+1)*SQUARE_SIZE), (SQUARE_SIZE*size,(i+1)*SQUARE_SIZE),2)    

        for k in range(size):
            for l in range(size):
                if board[k][l] == -1: 
                    pygame.draw.circle(screen, WHITE_COLOR, (int((l+1)*SQUARE_SIZE - SQUARE_SIZE/2),int((k+1)*SQUARE_SIZE - SQUARE_SIZE/2)), SQUARE_SIZE/3)
                elif board[k][l] == 1: 
                    pygame.draw.circle(screen, BLACK_COLOR, (int((l+1)*SQUARE_SIZE - SQUARE_SIZE/2),int((k+1)*SQUARE_SIZE - SQUARE_SIZE/2)), SQUARE_SIZE/3)
                else: 
                    pygame.draw.circle(screen, BACKGROUND_COLOR, (int((l+1)*SQUARE_SIZE - SQUARE_SIZE/2),int((k+1)*SQUARE_SIZE - SQUARE_SIZE/2)), SQUARE_SIZE/3)
        
        pygame.display.update() 
