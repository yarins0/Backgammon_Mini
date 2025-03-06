import time
import numpy as np
from Constants import *
from BackgammonGameManager import BackgammonGameManager
from Eval_position import evaluate_position
from HeuristicNet import neural_eval
from tkinter import Tk

def wait_until(somepredicate, timeout, period=0.25, *args, **kwargs):
  mustend = time.time() + timeout
  while time.time() < mustend:
    if somepredicate(*args, **kwargs): return True
    time.sleep(period)
  return False

def run_evaluation_comparison(num_games=4, target_boards=200):
    """
    Run multiple games against a random player, collect board states,
    calculate heuristic and network values, and compute statistics.
    
    Args:
        num_games: Minimum number of games to run
        target_boards: Target number of board states to collect
        
    Returns:
        dict: Statistics about the differences between heuristic and network evaluations
    """
    
    # Initialize data collection
    boards = []
    board_count = 0
    games_played = 0
    
    # Create a root window for Tkinter (can be hidden)
    root = Tk()
    root.withdraw()  # Hide the window
        
    # Run games until we have enough board states
    while board_count < target_boards:
        games_played += 1
        print(f"Starting game {games_played}...")
        
        # Create a new game
        game_manager = BackgammonGameManager(root, [NEURAL_AI, RAND_AI])
        
        # Play the game and collect board states
        wait_until(lambda gm=game_manager: gm.is_over(), timeout=1, period=0.5)
        
        # Add all board states from this game to our collection
        if hasattr(game_manager, 'board_history') and game_manager.board_history:
            boards.extend(game_manager.board_history)
            board_count = len(boards)
        
        print(f"Game {games_played} completed. Total board states: {board_count}")
    
    # Calculate heuristic and neural network values for each board
    heuristic_values = []
    network_values = []
    differences = []
    
    for board_state, turn in boards:
        # Calculate heuristic value
        heuristic_value = evaluate_position(board_state)
        
        # Calculate network value
        network_value = neural_eval(board_state, turn)
        
        # Store values
        heuristic_values.append(heuristic_value)
        network_values.append(network_value)
        differences.append(heuristic_value - network_value)
    
    # Calculate statistics
    differences = np.array(differences)
    mean_diff = np.mean(differences)
    variance_diff = np.var(differences)
    
    # Print results
    print("\nEvaluation Results:")
    print(f"Total games played: {games_played}")
    print(f"Total board states analyzed: {len(boards)}")
    print(f"Average difference (Heuristic - Network): {mean_diff:.4f}")
    print(f"Variance of differences: {variance_diff:.4f}")
    
    # Close the Tkinter window
    root.destroy()
    
    # Return statistics
    return {
        "games_played": games_played,
        "board_states": len(boards),
        "mean_difference": mean_diff,
        "variance_difference": variance_diff,
        "heuristic_values": heuristic_values,
        "network_values": network_values,
        "differences": differences.tolist(),
        "boards": boards
    }

if __name__ == "__main__":
    results = run_evaluation_comparison(num_games=4, target_boards=200)
    
    # You could save the results to a file for further analysis
    import json
    
    # Convert numpy arrays to lists for JSON serialization
    serializable_results = {
        "games_played": results["games_played"],
        "board_states": results["board_states"],
        "mean_difference": float(results["mean_difference"]),
        "variance_difference": float(results["variance_difference"]),
        "heuristic_values": [float(val) for val in results["heuristic_values"]],
        "network_values": [float(val) for val in results["network_values"]],
        "differences": [float(val) for val in results["differences"]]
    }
    
    with open("evaluation_results.json", "w") as f:
        json.dump(serializable_results, f)
    
    print("Results saved to evaluation_results.json")