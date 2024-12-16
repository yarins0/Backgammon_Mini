MIN_MAX_DEPTH = 2
EVAL_METHODS = {1:"heuristic" , 2:"strategic (min max)"}
CHOSEN_EVAL_METHOD = 1

CONSIDER_DICE_PROBABILITIES = False
EVAL_DISTRIBUTION = {
    "prime_structure": 0.2,  # Increased from 0.05 to emphasize closing off positions
    "anchors": 0.0,
    "blots": 0.2,  # Ensure this is significant to avoid leaving blots
    "race_advantage": 0.5,  # Adjust if necessary to balance racing and blocking
    "home_board_strength": 0.1,  # Increased to emphasize home board control
}

TURN_TIME = 1000  # Default turn time limit in seconds
AI_DELAY = 10  # Delay between AI moves in milliseconds

DEBUG_MODE = False
SAFE_TEST = False # Set to True to test AI without initializing pieces from board