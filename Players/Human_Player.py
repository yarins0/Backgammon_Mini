from Players.Player import *


class Human_Player(Player):
        
    def __init__(self, color ,board=START_BOARD):
        super().__init__(color ,board , is_human=True)
   
    def __str__(self):
        return f"Human Player ({self.color})"
