import time
import numpy as np
from Constants import *
from BackgammonGameManager import BackgammonGameManager
from tkinter import Tk
import matplotlib.pyplot as plt


def wait_until(somepredicate, timeout, period=0.25):
    """Wait for a condition to be true or timeout expires."""
    mustend = time.time() + timeout
    while time.time() < mustend:
        if somepredicate(): 
            return True
        time.sleep(period)
    return False

def run_comparison_games(num_games=10, timeout_per_game=5):
    """
    Run multiple games between heuristic player and neural network player.
    
    Args:
        num_games: Number of games to run
        timeout_per_game: Maximum time in seconds to wait for each game to complete
        
    Returns:
        dict: Statistics about the game results
    """
    # Create a root window for Tkinter (can be hidden)
    root = Tk()
    root.withdraw()  # Hide the window
    
    # Initialize counters
    heuristic_wins = 0
    neural_wins = 0
    games_played = 0
    game_results = []
    
    # Run the specified number of games
    for game_num in range(1, num_games + 1):
        games_played += 1
        print(f"\nStarting game {game_num} of {num_games}...")

        neural_player = [NEURAL_AI, "HeuristicNets/newformat06.03.pth"]
        players = [HEUR_AI, neural_player] if game_num % 2 == 0 else [neural_player, HEUR_AI] #alternating players in order to achieve fair colors
        
        # Create a new game with heuristic player (player 1) vs neural player (player 2)
        game_manager = BackgammonGameManager(root, players) 
        
        # Wait for the game to complete or timeout
        wait_until(lambda gm=game_manager: gm.is_over, 
                                   timeout=timeout_per_game, period=0.5)
                
        
        # Determine the winner
        winner = game_manager.winner_idx
        winner = winner if game_num % 2 == 0 else 1-winner
        if winner == 0:  # Heuristic player won
            heuristic_wins += 1
            result = "Heuristic player won"
        else:  # Neural player won
            neural_wins += 1
            result = "Neural player won"
        
        print(f"Game {game_num} result: {result}")

        game_results.append({
            "game_number": game_num,
            "winner": winner,
            "result": result
        })
    
    # Calculate win percentages
    heuristic_win_pct = (heuristic_wins / games_played) * 100 if games_played > 0 else 0
    neural_win_pct = (neural_wins / games_played) * 100 if games_played > 0 else 0
    
    # Print summary results
    print("\n" + "="*50)
    print("GAME COMPARISON RESULTS")
    print("="*50)
    print(f"Total games played: {games_played}")
    print(f"Heuristic player wins: {heuristic_wins} ({heuristic_win_pct:.1f}%)")
    print(f"Neural player wins: {neural_wins} ({neural_win_pct:.1f}%)")
    print("="*50)
    
    # Close the Tkinter window
    root.destroy()
    
    # Return statistics
    return {
        "games_played": games_played,
        "heuristic_wins": heuristic_wins,
        "neural_wins": neural_wins,
        "heuristic_win_percentage": heuristic_win_pct,
        "neural_win_percentage": neural_win_pct,
        "game_results": game_results
    }

def visualize_results(results):
    """
    Create a simple visualization of the game results.
    
    Args:
        results: Dictionary containing the game results
    
    Returns:
        float: Error metric (if applicable)
    """
    # Create a pie chart of the results
    labels = ['Heuristic Wins', 'Neural Wins']
    sizes = [results['heuristic_wins'], results['neural_wins']]
    colors = ['#ff9999', '#66b3ff']
    explode = (0.1, 0.1)  # explode all slices for visibility
    
    plt.figure(figsize=(10, 7))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title(f'Game Results: Heuristic vs Neural ({results["games_played"]} games)')
    
    # Add a text box with detailed statistics
    textstr = '\n'.join((
        f'Total Games: {results["games_played"]}',
        f'Heuristic Wins: {results["heuristic_wins"]} ({results["heuristic_win_percentage"]:.1f}%)',
        f'Neural Wins: {results["neural_wins"]} ({results["neural_win_percentage"]:.1f}%)',
    ))
    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.figtext(0.5, 0.02, textstr, fontsize=12, ha='center',
                bbox=props)
    
    plt.savefig('comparison_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Calculate error metric (if needed)
    # This is just a placeholder - replace with your actual error calculation
    error = abs(results["heuristic_win_percentage"] - results["neural_win_percentage"])
    
    return error

if __name__ == "__main__":
    # Run 10 games between heuristic and neural players
    results = run_comparison_games(num_games=30)
    
    # Visualize the results and get error metric
    #error = visualize_results(results)
    
    #print(f"Performance difference (error metric): {error:.2f}")
    
    # Save results to a file
    import json
    with open("comparison_results.json", "w") as f:
        json.dump(results, f, indent=4)
    
    print("Results saved to comparison_results.json")