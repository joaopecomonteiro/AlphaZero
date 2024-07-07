class NeuralNet():
    """
    Fortemente inspirado neste código por isso deixamos os comentários originais:
    https://github.com/suragnair/alpha-zero-general/blob/master/NeuralNet.py

    This class specifies the base NeuralNet class. To define your own neural
    network, subclass this class and implement the functions below. The neural
    network does not consider the current player, and instead only deals with
    the canonical form of the board.
    """

    def __init__(self, game):
        pass

    def train(self, examples):
        """
        This function trains the neural network with examples obtained from
        self-play.

        Input:
            examples: a list of training examples, where each example is of form
                      (board, pi, v). pi is the MCTS informed policy vector for
                      the given board, and v is its value. The examples has
                      board in its canonical form.
        """
        pass

    def predict(self, board):
        """
        Input:
            board: current board in its canonical form.

        Returns:
            pi: a policy vector for the current board- a numpy array of length
                game.getActionSize
            v: a float in [-1,1] that gives the value of the current board
        """
        pass

    def save_model(self, folder, filename):
        """
        Saves the current model in folder/filename
        """
        pass

    def load_model(self, folder, filename):
        """
        Loads model from folder/filename
        """
        pass