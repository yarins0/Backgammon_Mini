# Flags and modes
DEBUG_MODE = True
SAFE_TEST = False # Set to True to test AI without initializing pieces from board
NETWORK_TRAINING = True # Set to True to train the neural network

# Game parameters
WHITE = "white"
BLACK = "black"
START_BOARD = [2, 0, 0, 0, 0, -5, 0, -3, 0, 0, 0, 5, -5, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, -2, 0, 0, 0, 0]

CHOSEN_EVAL_METHOD = 1 # Choose 1 for heuristic, 2 for MCTS, 3 for strategic (min max)

# Min-max parameters
MIN_MAX_DEPTH = 1  # Default depth for min-max search

# MCST parameters
MCTS_C = 1.4 # Exploration parameter for UCB
TURN_TIME = 60  # Default turn time limit in seconds
AI_TURN_TIME = 2  # Default AI turn time limit in seconds
AI_DELAY = 0  # Delay between AI moves in milliseconds

# Heuristic evaluation parameters
CONSIDER_DICE_PROBABILITIES = False
EVAL_DISTRIBUTION = {
    "prime_structure": 1,
    "anchors": 0,
    "blots": 0,
    "race_advantage": 0,
    "home_board_strength": 0,
    "captured_pieces": 0,
}

