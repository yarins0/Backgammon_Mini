from Player import *

class Human_Player(Player):

    def __init__(self):
        super().__init__()
        
    def __init__(self, color):
        super().__init__(color)

    def isHuman(self):
        return True
