# Flags and modes
DEBUG_MODE = not True # Set to True to enable debug mode
SAFE_TEST = False # Set to True to test AI without initializing pieces from board
NETWORK_TRAINING = True # Set to True to train the neural network
ONE_RUN = False # Set to True to run only one game

# Game parameters
WHITE = "white"
BLACK = "black"

# Player types
AI = "AI"
RAND_AI = "Random_AI"
HEUR_AI = "Heuristic_AI"
MIN_MAX_AI = "Min_Max_AI"
MCTS_AI = "MCTS_AI"
HUMAN = "Human"

# Game parameters
START_BOARD = [2, 0, 0, 0, 0, -5, 0, -3, 0, 0, 0, 5, -5, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, -2, 0, 0, 0, 0]

CHOSEN_EVAL_METHOD = 4 # Choose 1 for heuristic, 2 for MCTS, 3 for strategic (min max), 4 for neural network, 5 for random
TURN_TIME = 1000  # Default turn time limit in seconds
AI_DELAY = 0  # Delay between AI moves in milliseconds

# Neural network parameters
PATH = "HeuristicNets/newformat18.02.pth"
LEARNING_RATE = 0.001
EPOCHS_NUM = 20
BOARD_SIZE = 28  # Board format length
NUM_SAMPLES = 500 # Number of samples to generate for heuristic training

# Min-max parameters
MIN_MAX_DEPTH = 1  # Default depth for min-max search

# MCST parameters
MCTS_C = 1.4 # Exploration parameter for UCB
AI_TURN_TIME = 2  # Default AI turn time limit in seconds

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

