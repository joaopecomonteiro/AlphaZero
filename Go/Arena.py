import logging
import pygame
from tqdm import tqdm
import time

log = logging.getLogger(__name__)

SQUARE_SIZE = 75
BACKGROUND_COLOR = (240, 196, 52)

class Arena():
    """
    Fortemente inspirado neste código por isso deixamos os comentários originais:
    https://github.com/suragnair/alpha-zero-general/blob/master/Arena.py
    
    An Arena class where any 2 agents can be pit against each other.
    """

    def __init__(self, player1, player2, game, display=None):
        """
        Input:
            player 1,2: two functions that takes board as input, return action
            game: Game object
            display: a function that takes board as input and prints it (e.g.
                     display in othello/OthelloGame). Is necessary for verbose
                     mode.

        see othello/OthelloPlayers.py for an example. See pit.py for pitting
        human players/other baselines with each other.
        """
        self.player1 = player1
        self.player2 = player2
        self.game = game
        self.display = display

    def playGame(self, verbose=False):
        """
        Executes one episode of a game.

        Returns:
            either
                winner: player who won the game (1 if player1, -1 if player2)
            or
                draw result returned from the game that is neither 1, -1, nor 0.
        """
        if verbose:
            assert self.display
            pygame.init()
            width = self.game.size * SQUARE_SIZE 
            height = self.game.size * SQUARE_SIZE 
            screen_size = (width, height) 
            screen = pygame.display.set_mode(screen_size)
            screen.fill(BACKGROUND_COLOR)

        players = [self.player2, None, self.player1]
        curPlayer = 1
        board = self.game.getInitBoard()
        it = 0
        while self.game.getGameEnded(board, curPlayer) is None:
            if verbose:
              pygame.event.pump()
            it += 1
            if verbose:
                assert self.display
                self.display(board, screen)

            action = players[curPlayer + 1](self.game.getCanonicalForm(board, curPlayer), curPlayer)
            valids = self.game.getValidMoves(self.game.getCanonicalForm(board, curPlayer), 1)
            if valids[action] == 0:
                log.error(f'Action {action} is not valid!')
                log.debug(f'valids = {valids}')
                assert valids[action] > 0
            board, curPlayer = self.game.getNextState(board, curPlayer, action)

        if verbose:
            assert self.display
            winner, player1_score, player2_score = self.game.getGameEnded(board, 1, game_over=True, get_score=True)
            print(f"Game over: winner -> {winner}, player1 score -> {player1_score}, player2 score -> {player2_score}")
            self.display(board, screen)
            time.sleep(5)

        return curPlayer * self.game.getGameEnded(board, curPlayer, game_over=True)

    def playGames(self, num, verbose=False):
        """
        Plays num games in which player1 starts num/2 games and player2 starts
        num/2 games.

        Returns:
            oneWon: games won by player1
            twoWon: games won by player2
            draws:  games won by nobody
        """
        num = int(num / 2)
        oneWon = 0
        twoWon = 0
        draws = 0
        for _ in tqdm(range(num), desc="Arena.playGames (1)"):
            gameResult = self.playGame(verbose=verbose)
            if gameResult == 1:
                oneWon += 1
            elif gameResult == -1:
                twoWon += 1
            else:
                draws += 1

        self.player1, self.player2 = self.player2, self.player1

        for _ in tqdm(range(num), desc="Arena.playGames (2)"):
            gameResult = self.playGame(verbose=verbose)
            if gameResult == -1:
                oneWon += 1
            elif gameResult == 1:
                twoWon += 1
            else:
                draws += 1

        return oneWon, twoWon, draws