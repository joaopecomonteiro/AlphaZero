import numpy as np
import math

PLAYER1 = 1
PLAYER2 = -1

class Board():
    """
    Classe para o tabuleiro do jogo ataxx
    """
    def __init__(self, size):
        self.size = size
        self.matrix = np.zeros((self.size, self.size)).astype(int)

        self.matrix[0][0] = PLAYER1
        self.matrix[self.size-1][self.size-1] = PLAYER1
        self.matrix[0][self.size-1] = PLAYER2
        self.matrix[self.size-1][0] = PLAYER2  


    def __getitem__(self, index):
        return self.matrix[index]


    
    def place(self, x, y, player): 
        """
        Função para colocar uma peça (movimento quando a distância é menor que 2)
        """
        self[x][y] = player


    
    def jump(self, x, y, new_x, new_y, player): 
        """
        Função para fazer um salto (movimento quando a distância é maior ou igual a 2)
        """
        self[x][y] = 0
        self[new_x][new_y] = player

        
    def calc_dist(self, x1, y1, x2, y2):
        """
        Função para calcular a distância entre dois pontos
        """
        return math.sqrt((x1-x2)**2+(y1-y2)**2)



    def execute_move(self, action, player):
        """
        Função para executar o movimento
        
        Aceita movimentos no formaro (x1, y1, x2, y2) e (x2, y2)
        No primeiro caso calcula a distância entre os dois pontos e executa o respetivo movimento, 
        no segundo caso assume o ponto como sendo o ponto para onde o jogador quer jogar e joga a peça que está mais próxima do mesmo~

        Retorna True se executou o movimento e False se o movimento era inválido
        """

        if len(action) == 2: # Se o movimento for do formato (x2, y2)
            
            new_x, new_y = action
            valid_moves = self.available_moves(player)
            x, y = 0, 0
            shortest_dist = np.inf
            for old_coords, new_coords in valid_moves:
                if new_coords == action:
                    dist = self.calc_dist(old_coords[0], old_coords[1], new_coords[0], new_coords[1])
                    if dist < shortest_dist:
                        x = old_coords[0]
                        y = old_coords[1]
                        shortest_dist = dist
        else: # Se o movimento for do formato (x1, y1, x2, y2)
            x, y, new_x, new_y = action

        if new_x < 0 or new_x >= self.size or new_y < 0 or new_y >= self.size:
            return False

        if self[new_x][new_y] != 0:
            return False

        dist = self.calc_dist(x, y, new_x, new_y)

        if dist == 0:
            return False
        
        elif dist < 2:
            self.place(new_x, new_y, player)
            self.eat(new_x, new_y, player)
            return True

        elif dist < 3:
            self.jump(x, y, new_x, new_y, player)
            self.eat(new_x, new_y, player)
            return True

        else:
            return False
    

    def is_valid_piece(self, x, y, player):
        """
        Função para verificar se a casa que o jogador escolheu contém uma peça sua
        """
        if self[x][y] == player:
            return True
        else:
            return False

    
    def eat(self, x, y, player):
        """
        Função para comer as peças após o movimento
        """
        for i in range(-1, 2):
            for j in range(-1, 2):
                if x+i < self.size and x+i >=0 and y+j < self.size and y+j >=0: 
                    if self[x+i][y+j] == -player:
                        self[x+i][y+j] = player
    
    
    def get_player_pieces(self, player): 
        """
        Função para obter uma lista com as peças de uma jogador
        """
        pieces = []
        for x in range(self.size):
            for y in range (self.size): 
                if self[x][y] == player:
                    pieces.append([x,y])
        return pieces  
    
    
        
    def available_moves(self, player):
        """
        Função para obter uma lista com os movimentos que uma jogador pode fazer
        """
        moves = []
        for piece in self.get_player_pieces(player):
            x = piece[0]
            y = piece[1]
            for i in range(-2, 3):
                for j in range(-2, 3):
                    if x+i < self.size and x+i >=0 and y+j < self.size and y+j >=0: 
                        if self[x+i][y+j] == 0:
                            moves.append(((x, y) ,(x+i, y+j)))
        return moves 

    
    def is_game_over(self):
        """
        Função para verificar se o jogo acabou
        """
        if len(self.available_moves(PLAYER1)) == 0 or len(self.available_moves(PLAYER2)) == 0:
            return True
        return False
    
    
    def piece_counter(self):
        """
        Função para contar as peças dos dois jogadores
        """
        player_1_counter = len(self.get_player_pieces(PLAYER1))
        player_2_counter = len(self.get_player_pieces(PLAYER2))
        return player_1_counter, player_2_counter
    


    def count_diff(self, player):
        """
        Função para obter a diferença entre as peças de um jogador e do seu adversário
        """
        count = 0
        for y in range(self.size):
            for x in range(self.size):
                if self[x][y] == player:
                    count += 1
                elif self[x][y] == -player:
                    count -= 1
        return count


