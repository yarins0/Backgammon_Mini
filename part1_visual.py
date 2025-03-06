import matplotlib.pyplot as plt
import numpy as np
import json

def visualize_evaluation_results(results_file="evaluation_results.json"):
    """
    Visualize the results of the evaluation comparison.
    
    Args:
        results_file: Path to the JSON file containing the evaluation results
    """
    # Load results
    with open(results_file, "r") as f:
        results = json.load(f)
    
    heuristic_values = results["heuristic_values"]
    network_values = results["network_values"]
    differences = results["differences"]
    mean_diff = results["mean_difference"]
    variance_diff = results["variance_difference"]
    
    # Create figure with multiple subplots
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot 1: Scatter plot of heuristic vs network values
    axs[0, 0].scatter(heuristic_values, network_values, alpha=0.5)
    axs[0, 0].set_title('Heuristic vs Network Values')
    axs[0, 0].set_xlabel('Heuristic Value')
    axs[0, 0].set_ylabel('Network Value')
    
    # Add diagonal line for perfect correlation
    min_val = min(min(heuristic_values), min(network_values))
    max_val = max(max(heuristic_values), max(network_values))
    axs[0, 0].plot([min_val, max_val], [min_val, max_val], 'r--')
    
    # Plot 2: Histogram of differences
    axs[0, 1].hist(differences, bins=30)
    axs[0, 1].set_title('Distribution of Differences (Heuristic - Network)')
    axs[0, 1].set_xlabel('Difference')
    axs[0, 1].set_ylabel('Frequency')
    
    # Add vertical line for mean
    axs[0, 1].axvline(mean_diff, color='r', linestyle='dashed', linewidth=2)
    axs[0, 1].text(mean_diff*1.1, axs[0, 1].get_ylim()[1]*0.9, 
                  f'Mean: {mean_diff:.4f}', color='r')
    
    # Plot 3: Time series of values
    indices = range(len(heuristic_values))
    axs[1, 0].plot(indices, heuristic_values, label='Heuristic')
    axs[1, 0].plot(indices, network_values, label='Network')
    axs[1, 0].set_title('Evaluation Values Over Time')
    axs[1, 0].set_xlabel('Board State Index')
    axs[1, 0].set_ylabel('Evaluation Value')
    axs[1, 0].legend()
    
    # Plot 4: Time series of differences
    axs[1, 1].plot(indices, differences)
    axs[1, 1].set_title('Differences Over Time')
    axs[1, 1].set_xlabel('Board State Index')
    axs[1, 1].set_ylabel('Difference (Heuristic - Network)')
    
    # Add horizontal line for mean
    axs[1, 1].axhline(mean_diff, color='r', linestyle='dashed', linewidth=2)
    
    # Add summary statistics as text
    plt.figtext(0.5, 0.01, 
                f'Summary Statistics:\n'
                f'Number of Board States: {len(heuristic_values)}\n'
                f'Mean Difference: {mean_diff:.4f}\n'
                f'Variance of Differences: {variance_diff:.4f}\n'
                f'Standard Deviation: {np.sqrt(variance_diff):.4f}',
                ha='center', bbox={'facecolor': 'lightgray', 'alpha': 0.5, 'pad': 5})
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig('evaluation_comparison.png', dpi=300)
    plt.show()

if __name__ == "__main__":
    visualize_evaluation_results()