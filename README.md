ירין סולומון 206454530

# Backgammon AI Project
A Python implementation of the classic board game Backgammon, featuring both human and AI players. This project allows you to play against an AI opponent or watch two AI players compete against each other. The AI uses heuristic evaluation and minimax strategies to make decisions.

# Introduction:
This project implements a playable version of Backgammon with AI capabilities. The AI players are designed to simulate human-like decision-making by evaluating the game board and predicting future moves using heuristic and strategic methods. The goal is to provide an engaging experience whether you're playing against the computer or observing AI strategies.

# Features:
Human vs. AI: Play against an AI opponent with configurable difficulty.
AI vs. AI: Watch two AI players compete, showcasing different strategies.
Heuristic Evaluation: The AI assesses board positions using weighted factors.
Minimax Algorithm: Implements depth-limited minimax search for strategic planning.
Customizable Parameters: Adjust evaluation weights and search depth to modify AI behavior.
Project Structure
run.py: Entry point for running the game.
Player.py: Contains the Player class, representing both human and AI players.
AI_Player.py: Extends Player with AI capabilities, including move generation and evaluation.
Eval_position.py: Functions for evaluating board positions based on various criteria.
Constants.py: Configuration constants and parameters used throughout the project.
Board.py: Manages the game board state and visual representation.
Utils.py: Utility functions used by multiple modules.
Installation
Prerequisites
Python 3.7 or higher installed on your system.

Installation Steps:
Clone the Repository
git clone https://github.com/yarins0/Backgammon_Mini.git

Navigate to the Project Directory
cd Backgammon_Mini


Note: As of now, there are no external dependencies other than Python standard libraries.

# Start the game
run the run.py script: python run.py

You will be prompted to select game modes and other configurations.
****Right now game modes depend on player array fed into BackgammonGameGUI in run.py***

# Game Modes:
Human vs. AI: Play against the AI.
AI vs. AI: Watch two AI players compete.
Human vs. Human: Play against another human (sharing the same computer).
Game Rules
Backgammon is a two-player game where each player moves their checkers according to the roll of two dice. The objective is to move all your checkers into your home board and then bear them off.

# Basic Rules:
Players move checkers in opposite directions.
A point occupied by a single checker is a blot. If an opponent lands on a blot, it is hit and placed on the bar.
A player must re-enter any checkers on the bar before making any other moves.
The first player to bear off all their checkers wins the game.
For detailed rules, you may refer to official Backgammon rules.

# AI Strategies
The AI in this project employs two primary strategies:

1. Heuristic Evaluation
The AI uses a weighted sum of various board features to evaluate positions. The evaluation considers:

Prime Structure: Building consecutive occupied points to block the opponent.
Blots: Vulnerable single checkers that can be hit.
Race Advantage: The overall progress of checkers towards the home board.
Home Board Strength: The strength of the player's home board in preventing opponent re-entry.
The weights for these features are configurable.

2. Minimax Algorithm
The AI uses a depth-limited minimax algorithm with alpha-beta pruning for strategic decision-making. It simulates possible moves up to a certain depth and chooses the move that maximizes its advantage while minimizing the opponent's.

Customization
Adjusting AI Evaluation Parameters
The AI's behavior can be tailored by adjusting the evaluation weights in Constants.py.

# Constants.py
EVAL_DISTRIBUTION = {
    "prime_structure": 0.2,
    "anchors": 0.0,
    "blots": 0.2,
    "race_advantage": 0.5,
    "home_board_strength": 0.1,
}

Modify the values to change the importance of each feature in the AI's evaluation function. Ensure that the sum of all weights equals 1.0.

Changing the Minimax Depth
The depth of the minimax search affects the AI's foresight. A greater depth allows the AI to plan further ahead but increases computation time.

MIN_MAX_DEPTH = 2  # Increase this value for deeper search

Note: Be cautious when increasing the depth, as it may significantly slow down the game.
