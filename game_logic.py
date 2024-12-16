'''Creates a class for Human backgammon pieces
Created 2024
@author: Anni Ainesaz
'''

import random
import time

# game_logic.py

from Player import *
from AI_Player2 import *
from Human_Player import *

class BackgammonGameLogic:
    WHITE = "white"
    BLACK = "black"

    def __init__(self, players):
        self.players = players
        self.scores = [0] * len(self.players)
        self.board_history = []
        self.current_board_index = -1
        self.white = None
        self.black = None

    def start_game(self, black_player, white_player):
        self.black = AI_Player(self.BLACK) if black_player == "AI" else Human_Player(self.BLACK)
        self.white = AI_Player(self.WHITE) if white_player == "AI" else Human_Player(self.WHITE)

        self.white.set_other(self.black)
        self.black.set_other(self.white)

        self.turn = self.WHITE
        self.prepare_turn()

        if self.white.win():
            return self.WHITE
        elif self.black.win():
            return self.BLACK
        return None

    def current_player(self):
        return self.white if self.turn == self.WHITE else self.black

    def other_player(self):
        return self.black if self.turn == self.WHITE else self.white

    def switch_turn(self):
        self.turn = self.WHITE if self.turn == self.BLACK else self.BLACK

    def prepare_turn(self):
        current_player = self.current_player()
        if not current_player.isHuman():
            self.AI_turn()

    def AI_turn(self):
        computer_roll = roll()
        board = self.status_format()
        move_sequence = self.current_player().play(board, computer_roll)
        if move_sequence:
            for move in move_sequence:
                self.current_player().move_piece(abs(move[0] - move[1]), move[0], computer_roll)
                self.update_and_render_board()

        if self.current_player().win():
            return

    def status_format(self):
        if self.white is None or self.black is None:
            raise AttributeError("Players are not initialized. Call start_game first.")
        return generate_board(self.white.get_pieces(), self.black.get_pieces())

    def update_and_render_board(self):
        board = self.status_format()
        self.board_history.append(board)
        self.current_board_index += 1
        self.render_board(board)

    def render_board(self, board):
        # Implement the rendering logic here
        pass

def roll():
    r = [random.randint(1,6), random.randint(1,6)]
    if r[0] == r[1]:
        r = [r[0], r[0], r[0], r[0]]
    return r

def generate_board(white_pieces , black_pieces):
        board = [0] * 28
        for point in white_pieces:
            if point == 0: # white captured
                board[26] += 1
            elif point == 25:
                board[24] += 1 # white out
            else:
                board[point - 1] += 1

        for point in black_pieces:
            if point == 25:  # black captured
                board[27] += 1
            elif point == 0:
                board[25] += 1  # black out
            else:
                board[point - 1] -= 1


        return board


