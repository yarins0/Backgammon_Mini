# Flags and modes
DEBUG_MODE = not True # Set to True to enable debug mode
GUI_MODE = not False # Set to True to enable GUI
SAFE_TEST = False # Set to True to test AI without initializing pieces from board
NETWORK_TRAINING = True # Set to True to train the neural network
ONE_RUN = False # Set to True to run only one game

# Colors parameters
WHITE = "white"
BLACK = "black"

# Player types
RAND_AI = "Random_AI"
HEUR_AI = "Heuristic_AI"
MIN_MAX_AI = "Min_Max_AI"
MCTS_AI = "MCTS_AI"
NEURAL_AI = "Neural_AI"
HUMAN = "Human"

# Game parameters
START_BOARD = [2, 0, 0, 0, 0, -5, 0, -3, 0, 0, 0, 5, -5, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, -2, 0, 0, 0, 0]

TURN_TIME = 1000  # Default turn time limit in seconds
AI_DELAY = 0  # Delay between AI moves in milliseconds

# Gui parameters
TRI_WIDTH = 50
TRI_HEIGHT = 200

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

