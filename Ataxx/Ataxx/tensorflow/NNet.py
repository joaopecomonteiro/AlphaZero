import os
import numpy as np
import sys
import tensorflow as tf

sys.path.append('../..')
from Ataxx.utils import *
from Ataxx.NeuralNet import NeuralNet
from .AtaxxNNet import AtaxxNNet as ataxxnet

args = dotdict({
    'lr': 0.001,
    'dropout': 0.3,
    'epochs': 10,
    'batch_size': 64,
    'cuda': False,
    'num_channels': 128,
})


class NNetWrapper(NeuralNet):
    """
    Wrapper do modelo
    """
    def __init__(self, game):
        self.nnet = ataxxnet(game, args)
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()

    
    def train(self, examples):
        """
        Função para treinar o modelo

        examples: lista com os exemplos para o treino, cada exemplo com a forma (board, pi, v)
        """

        input_boards, target_pis, target_vs = list(zip(*examples))
        input_boards = np.asarray(input_boards)
        exp_input_boards = np.expand_dims(input_boards, axis=-1)
        target_pis = np.asarray(target_pis)
        target_vs = np.asarray(target_vs)
        self.nnet.model.fit(x = exp_input_boards, y = [target_pis, target_vs], batch_size = args.batch_size, epochs = args.epochs)


    def predict(self, board):
        """
        Função para prever a jogada a fazer
        """

        board = board[np.newaxis, :, :]
        pi, v = self.nnet.model.predict(board, verbose=False)

        return pi[0], v[0]


    def save_model(self, folder='checkpoint', filename='checkpoint.h5'):
        """
        Função para salvar o modelo
        
        folder: nome do diretório onde vai ser guardado o modelo
        filename: nome do ficheiro que vai guardar o modelo
        """

        filename = filename.split(".")[0] + ".h5"

        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists! ")
        self.nnet.model.save(filepath)



    def load_model(self, folder='checkpoint', filename='checkpoint.h5'):
        """
        Função para dar load a um modelo já treinado
        
        folder: nome do diretório com o modelo
        filename: nome do ficheiro com o modelo
        """

        filename = filename.split(".")[0] + ".h5"

        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise("No model in path {}".format(filepath))

        self.nnet.model = tf.keras.models.load_model(filepath)




