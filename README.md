@author: Yarin Solomon

# Backgammon AI Project

A Python implementation of the classic board game Backgammon, featuring both human and AI players. This project allows you to play against an AI opponent or watch two AI players compete against each other. The AI uses heuristic evaluation, minimax, MCTS, and neural network strategies to make decisions.

## Introduction

This project implements a playable version of Backgammon with AI capabilities. The AI players are designed to simulate human-like decision-making by evaluating the game board and predicting future moves using heuristic and strategic methods. The goal is to provide an engaging experience whether you're playing against the computer or observing AI strategies.

## Features and game modes

- **Human vs. AI**: Play against an AI opponent with configurable difficulty.
- **AI vs. AI**: Watch two AI players compete, showcasing different strategies.
- **Heuristic Evaluation**: The AI assesses board positions using weighted factors.
- **Minimax Algorithm**: Implements depth-limited minimax search for strategic planning.
- **MCTS Algorithm**: Uses Monte Carlo Tree Search for decision making.
- **Neural Network Evaluation**: Uses a trained neural network to evaluate board positions.
- **Customizable Parameters**: Adjust evaluation weights, search depth, and other parameters to modify AI behavior.

## AI Strategies
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

3. MCTS Algorithm The AI uses Monte Carlo Tree Search to explore possible moves and outcomes, balancing exploration and exploitation to make decisions.

4. Neural Network Evaluation The AI uses a trained neural network to evaluate board positions, providing a more sophisticated and learned approach to decision-making.


## Project Structure

- `run.py`: Entry point for running the game.
- `run2.py`: Alternative entry point for running the game with different configurations.
- `BackgammonGameManager.py`: Manages the game logic and player interactions.
- `Players/`: Contains various player classes, including human and different AI strategies.
  - `Player.py`: Base class for all players.
    - `Human_Player.py`: Class for human players.
    - `AI_Player.py`: Base class for AI players.
        - `Heuristic_Player.py`: AI player using heuristic evaluation.
        - `Random_Player.py`: AI player making random moves.
        - `Min_Max_Player.py`: AI player using minimax algorithm.
        - `MCTS_Player.py`: AI player using Monte Carlo Tree Search.
        - `Neural_Player.py`: AI player using neural network evaluation.
- `Eval_position.py`: Functions for evaluating board positions based on various criteria.
- `Constants.py`: Configuration constants and parameters used throughout the project.
- `BoardTree.py`: Manages the game tree for MCTS and minimax algorithms.
- `GUI.py`: Manages the graphical user interface for the game.
- `HeuristicNet.py`: Defines and trains the neural network for board evaluation.

## Installation

### Prerequisites

- Python 3.7 or higher installed on your system.

### Installation Steps

1. Clone the Repository
   ```sh
   git clone https://github.com/yarins0/Backgammon_Mini.git

2. Navigate to the Project Directory
    cd Backgammon_Mini


Note: As of now, there are no external dependencies other than Python standard libraries.

# Start the game
run the run.py script: 
    python run.py

You will be prompted to select game modes and other configurations.
Set ONE_RUN = False flag in constants.py to run the game in a loop (usefull for net training), type 'q' in console in order to terminate the loop.

## Customization - run.py
In run.py, you can customize the game by modifying the player array fed into BackgammonGameGUI. This array determines the players participating in the game and their types (human or AI).

Example:

    # Define the starting board - will be set to default if not specifird in game builder
    start_board = [0, 0, 0, -4, 0, -4, 0, 0, 0, -1, -1, 4, 1, 0, 1, 0, 2, 2, 5, -1, 0, -2, -1, 0, 0, 1, 0, 0]

    ratios = {
      "prime_structure": 0.5,
      "anchors": 0.05,
      "blots": 0.45,
      "race_advantage": 0.0,
      "home_board_strength": 0.0,
      "captured_pieces": 0.0
      }
    
    # Define the players
    players1 = [HUMAN, MIN_MAX_AI]
    players2 = [MIN_MAX_AI, [MIN_MAX_AI, ratios1, 2]] #minmax algorithm based players with default or custome variables
    players3 = [NEURAL_AI , [NEURAL_AI, "HeuristicNets/newformat06.03.pth"]] #neural network players one with most recent model and one with an older less trained one
    players4 = [[HEUR_AI, ratios] , [MCTS_AI, ratios, 3.2]]

    # Start the game with the defined players
    window = Tk()
    BackgammonGameManager(window, players1, start_board)

 You can replace players componets with other AI player classes like: 
 - RAND_AI
 - HEUR_AI    / [HEUR_AI, ratios]               # when ratios is a weight map
 - MIN_MAX_AI / [MIN_MAX_AI, ratios, depth] 
 - MCTS_AI    / [MCTS_AI, ratios, c] 
 - NEURAL_AI  / [NEURAL_AI, model_path]         # when model_path is a path to a saved model

Choosing the first option will use the default values stored in Constants.py. 

## Customization - Constants.py
This file contains flags and constants used throughout the project. You can modify these values to suit your needs and read about each variable in the file.

# Game Rules:
Backgammon is a two-player game where each player moves their checkers according to the roll of two dice. The objective is to move all your checkers into your home board and then bear them off.

## Basic Rules:
- Players move checkers in opposite directions.
- A point occupied by a single checker is a blot. If an opponent lands on a blot, it is hit and placed on the bar.
- A player must re-enter any checkers on the bar before making any other moves.
- The first player to bear off all their checkers wins the game.
- For detailed rules, you may refer to official Backgammon rules.


