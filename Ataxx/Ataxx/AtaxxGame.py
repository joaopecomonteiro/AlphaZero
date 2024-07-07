from __future__ import print_function
import sys
sys.path.append('..')
from Ataxx.Game import Game
from .AtaxxLogic import Board
import numpy as np 
import pygame

SQUARE_SIZE = 75 #Tamanho dos quadrados da interface

PLAYER1 = 1
PLAYER2 = -1

#Cores
BLUE = (0,0,255) 
RED = (255,0,0) 
WHITE_COLOR = (255,255,255) 
BLACK_COLOR = (0,0,0) 
GREY = (182,179,179) 



class AtaxxGame(Game):
    """
    Classe para o jogo ataxx
    """

    # Caracteres para a string do tabuleiro
    square_content = {
        -1: "X",
        +0: "-",
        +1: "O",
        +9: "I",
        -9: "I"
    }

    @staticmethod
    def getSquarePiece(piece):
        return AtaxxGame.square_content[piece]


    def __init__(self, size):
        self.size = size


    def getInitBoard(self):
        """
        Função para obter o tabuleiro inicial
        """
        b = Board(self.size)
        return b.matrix

    def getBoardSize(self):
        """
        Função para obter o tamanho do tabuleiro
        """
        return (self.size, self.size)

    def getActionSize(self):
        """
        Função para obter o número de ações possiveis
        """
        return self.size*self.size+1
    
    def getNextState(self, board, player, action):
        """
        Função para fazer a jogada, retorna o estado do tabuleiro depois da jogada e o próximo jogador
        
        Aceita jogadas no formato de um número inteiro, no formato (x2, y2) ou no formato (x1, y1, x2, y2)
        No primeiro caso calcula a casa a que o número inteiro corresponde e executa o movimento, no restantes executa logo o movimento
        """
        if action == self.size*self.size+1:
            return(board, -player)
        b = Board(self.size)
        b.matrix = np.copy(board)
        
        if type(action) is int:
            move = (int(action/self.size), action%self.size)
        else:
            move = action

        b.execute_move(move, player)

        return (b.matrix, -player)


    def get_piece_to_move(self, board, action, player):
        """
        Função para obter a peça mais próxima das coordenadas para onde o jogador quer jogar 
        """
        b = Board(self.size)
        b.matrix = np.copy(board)

        valid_moves = b.available_moves(player)
        x, y = 0, 0
        shortest_dist = np.inf
        for old_coords, new_coords in valid_moves:
            if new_coords == action:
                dist = b.calc_dist(old_coords[0], old_coords[1], new_coords[0], new_coords[1])
                if dist < shortest_dist:

                    x = old_coords[0]
                    y = old_coords[1]
                    shortest_dist = dist

        return x, y



    def getValidMoves(self, board, player):
        """
        Função para obter os movimentos válidos, retorna uma array em que os movimentos válidos estão marcados com 1 e os inválidos com 0
        """

        valids = np.zeros(self.getActionSize()).astype(int)
        b = Board(self.size)
        b.matrix = np.copy(board)
        legalMoves = b.available_moves(player)
        if len(legalMoves)==0:
            valids[-1]=1
            valids
        
        for old_coords, new_coords in legalMoves:
            valids[self.size*new_coords[0]+new_coords[1]]=1
    
        return valids
    
    def get_legal_moves(self, board, player):
        """
        Função para obter os movimentos válidos, retorna uma lista com os movimentos válidos no formato ((x1, y1), (x2, y2))
        """
        b = Board(self.size)
        b.matrix = np.copy(board)
        legalMoves = b.available_moves(player)
        return legalMoves


    def getGameEnded(self, board, player):
        """
        Função para verificar se o jogo acabou tendo em conta a prespetiva de um determinado jogador,
        retorna 1 se esse jogador ganhou, -1 se perdeu, 0 se o jogo acabou empatado ou None se o jogo ainda não acabou
        """
        b = Board(self.size)
        b.matrix = np.copy(board)
        
        if b.is_game_over():
            if b.count_diff(player) > 0:
                return 1
            elif b.count_diff(player) < 0:
                return -1
            else:
                return 0
        
        return None
    
    def getCanonicalForm(self, board, player):
        """
        Função para obter o tabuleiro na sua forma canónica, as peças do jogador em questão ficam marcadas com 1 e do adversário com -1
        """
        return player*board
    
    
    def getSymmetries(self, board, pi):
        """
        Função para obter as simetrias do tabuleiro para o treino do modelo
        """

        # mirror, rotational
        assert(len(pi) == self.size**2+1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.size, self.size))
        l = []

        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(board, i)
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
        board_s = "".join(self.square_content[square] for row in board for square in row)
        return board_s

    def getScore(self, board, player):
        """
        Função para obter o resultado do jogo
        """
        b = Board(self.size)
        b.matrix = np.copy(board)
        return b.count_diff(player)
    
    def piece_counter(self, board):
        """
        Função para obter o número de peças dos dois jogadores
        """
        b = Board(self.size)
        b.matrix = np.copy(board)
        return b.piece_counter()
    

    @staticmethod
    def display(board, screen):
        """
        Função para dar display ao tabuleiro
        """
        size = len(board)
        for i in range(size -  1):
            pygame.draw.line(screen, WHITE_COLOR, ((i+1)*SQUARE_SIZE,0), ((i+1)*SQUARE_SIZE,SQUARE_SIZE*size), 2) 
            pygame.draw.line(screen, WHITE_COLOR, (0,(i+1)*SQUARE_SIZE), (SQUARE_SIZE*size,(i+1)*SQUARE_SIZE),2)    

        for k in range(size):
            for l in range(size):
                if board[k][l] == PLAYER1: 
                    pygame.draw.circle(screen, RED, (int((l+1)*SQUARE_SIZE - SQUARE_SIZE/2),int((k+1)*SQUARE_SIZE - SQUARE_SIZE/2)), SQUARE_SIZE/3)
                
                elif board[k][l] == PLAYER2: 
                    pygame.draw.circle(screen, BLUE, (int((l+1)*SQUARE_SIZE - SQUARE_SIZE/2),int((k+1)*SQUARE_SIZE - SQUARE_SIZE/2)), SQUARE_SIZE/3)
                
                elif board[k][l]==3 or board[k][l]==-3: 
                    pygame.draw.circle(screen, GREY, (int((l+1)*SQUARE_SIZE - SQUARE_SIZE/2),int((k+1)*SQUARE_SIZE - SQUARE_SIZE/2)), SQUARE_SIZE/3)
                
                else: 
                    pygame.draw.circle(screen, BLACK_COLOR, (int((l+1)*SQUARE_SIZE - SQUARE_SIZE/2),int((k+1)*SQUARE_SIZE - SQUARE_SIZE/2)), SQUARE_SIZE/3)
        
        pygame.display.update() 
    
    @staticmethod
    def display_grey_circles(board, screen):
        """
        Função para dar display aos circulos cinzentos que representam para onde o jogador pode jogar uma peça após a ter selecionado
        """
        size = len(board)
        for k in range(size):
            for l in range(size):
                if board[k][l] == 3: 
                    pygame.draw.circle(screen, GREY, (int((l+1)*SQUARE_SIZE - SQUARE_SIZE/2),int((k+1)*SQUARE_SIZE - SQUARE_SIZE/2)), SQUARE_SIZE/3)
                
        pygame.display.update() 


    

















