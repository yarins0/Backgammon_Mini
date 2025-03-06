import msvcrt
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from Eval_position import evaluate_position, win_based_evaluation
from Constants import NETWORK_TRAINING, PATH, WHITE, BLACK, LEARNING_RATE, EPOCHS_NUM, BOARD_SIZE, NUM_SAMPLES


# 1. Define the Neural Network
class HeuristicNet(nn.Module):
    def __init__(self, input_size = BOARD_SIZE):
        super(HeuristicNet, self).__init__()
        self.fc1 = nn.Linear(input_size  + 1, 40)  # First hidden layer
        self.fc2 = nn.Linear(40, 40)               # Second hidden layer
        self.output = nn.Linear(40, 1)             # Output layer
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.output(x)  # No activation for output
        return torch.sigmoid(x)  # Ensure output is between 0 and 1

# Generate Random Boards and Heuristic Values
def generate_data(NUM_SAMPLES, BOARD_SIZE, heuristic_func):
    data = []
    for _ in range(NUM_SAMPLES):
        board = generate_random_board(BOARD_SIZE)  # Generate random board
        value = heuristic_func(board) # Compute heuristic value
        data.append((board + [-1], 1 - value)) # Add board configuration and heuristic value as black
        data.append((board + [1], value)) # Add board configuration and heuristic value as white

    return data

def generate_data_from_boards(board_history):
    """
    Process the board history to generate labeled data for training.

    Args:
        board_history (list): A list of board configurations.
        winner_color (str): The color of the winner.

    Returns:
        list: A list of tuples containing the board configuration and the corresponding heuristic value.
    """
    data = []
    winner = board_history[-1][1]
    value = win_based_evaluation(board_history[-1][0].copy(), winner) # Compute heuristic value for winner

    for board, player in board_history:
        player_value = value if winner == player else 1 - value  # Compute heuristic value
        turn = 1 if player == WHITE else -1

        data.append((board + [turn], player_value))
        #data.append((board + [-1*  turn], 1-player_value))
    return data

def generate_random_board(BOARD_SIZE):
    """
    Generate a random board according to the described format and rules.

    Returns:
        list: A list representing the board configuration.
    """
    board = [0] * BOARD_SIZE

    # Total pieces per player
    total_pieces = 15

    # Assign random positive (white) and negative (black) pieces to positions 1-24
    positions = list(range(24))
    random.shuffle(positions)

    white_remaining = total_pieces
    black_remaining = total_pieces

    for pos in positions:
        if white_remaining > 0 and black_remaining > 0:
            white_count = random.randint(0, white_remaining)
            black_count = random.randint(0, black_remaining)

            if white_count > 0 and black_count > 0:
                # Ensure no mixed pieces in the same position
                if random.choice([True, False]):
                    black_count = 0
                else:
                    white_count = 0

            board[pos] = white_count - black_count
            white_remaining -= white_count
            black_remaining -= black_count
        elif white_remaining > 0:
            white_count = random.randint(0, white_remaining)
            board[pos] = white_count
            white_remaining -= white_count
        elif black_remaining > 0:
            black_count = random.randint(0, black_remaining)
            board[pos] = -black_count
            black_remaining -= black_count

    # Set escaped and eaten pieces (indices 25-28)
    board[24] = random.randint(0, white_remaining)  # Captured white
    white_remaining -= board[24]
    board[25] = random.randint(0, black_remaining)  # Captured black
    black_remaining -= board[25]
    board[26] = total_pieces - white_remaining  # Escaped white
    board[27] = total_pieces - black_remaining  # Escaped black

    return board

def _compute_validation_metrics(model, criterion, val_data):
    """
    Runs a simple validation pass and returns average MSE loss.
    Since the output is 0..1, you can easily adapt this to compute accuracy or other metrics if desired.
    """
    model.eval()
    if not val_data:
        return None

    with torch.no_grad():
        boards, values = zip(*val_data)
        boards_tensor = torch.tensor(boards, dtype=torch.float32)
        values_tensor = torch.tensor(values, dtype=torch.float32).unsqueeze(1)

        predictions = model(boards_tensor)
        val_loss = criterion(predictions, values_tensor).item()
    return val_loss

# Train the Neural Network
def train_network(model, criterion, optimizer, data, epochs=EPOCHS_NUM, batch_size=32, val_data=None):
    """
    Train the neural network using the provided data.
    """
    # Prepare data
    boards, values = zip(*data)
    boards = torch.tensor(boards, dtype=torch.float32)
    values = torch.tensor(values, dtype=torch.float32).unsqueeze(1)  # Reshape to (N, 1)

    dataset = torch.utils.data.TensorDataset(boards, values)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size, shuffle=True)

    # Training loop
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        for batch_boards, batch_values in dataloader:
            optimizer.zero_grad()
            predictions = model(batch_boards)
            loss = criterion(predictions, batch_values)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        avg_loss = epoch_loss / len(dataloader)
        # Compute validation metrics if val_data is provided
        val_loss = _compute_validation_metrics(model, criterion, val_data) if val_data else None
        if val_loss is not None:
            print(f"Epoch {epoch + 1}/{epochs}, Train Loss: {avg_loss:.4f}, Val Loss: {val_loss:.4f}")
        else:
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")

    return model

# Train the Neural Network using boards
def boards_based_training(board_history):
    # Step 1: load initial network
    model = HeuristicNet(BOARD_SIZE)
    model.load_state_dict(torch.load(PATH, weights_only=True))
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    model.eval()
    print("Initial network loaded and trained.")
    
    model = train_network(model, criterion, optimizer, generate_data_from_boards(board_history))

    torch.save(model.state_dict(), PATH)
    print("Training complete and model saved!")

# Iterations training Process
def iter_training():
    # Step 1: load initial network
    model = HeuristicNet(BOARD_SIZE)
    model.load_state_dict(torch.load(PATH, weights_only=True))
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    model.eval()
    print("Initial network loaded and trained.")
    print(f"Running...")

    # Step 2: Refine the network with game simulations
    current_iter = 0
    while True:
        # Check if a key was pressed
        if msvcrt.kbhit():
            key_pressed = msvcrt.getch()
            # b'q' is the byte representation of the 'q' character
            if key_pressed.lower() == b'q':
                print("User requested to quit. Stopping training.")
                break
        # Perform your training or evaluation steps here
        print(f"\nIteration {current_iter}")
        labeled_data = generate_data(NUM_SAMPLES=NUM_SAMPLES, BOARD_SIZE=BOARD_SIZE, heuristic_func=evaluate_position)
        model = train_network(model, criterion, optimizer, labeled_data)
        current_iter += 1
    print(f"Completed {current_iter} iterations.")

    torch.save(model.state_dict(), PATH)
    print(f"Model saved to {PATH}!")
    print("Training complete!")

def neural_eval(board, color, model_path=PATH):
    """
    Evaluate a board configuration using a trained model.

    Args:
        board (list): The board configuration (length is BOARD_SIZE).
        model_path (str): Path to the trained model.
        turn (int): 1 indicates White, -1 indicates Black.

    Returns:
        float: The evaluation score between 0 and 1 (favoring the player as score approaches 1).
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = HeuristicNet(BOARD_SIZE).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=False))
    model.eval()

    with torch.no_grad():
        x = torch.tensor(board + [1 if color == WHITE else -1], dtype=torch.float32, device=device)
        x = x.unsqueeze(0)  # Add batch dimension
        prediction = model(x)
    return prediction.item()
   
# Main function

if __name__ == "__main__":
    if not NETWORK_TRAINING:
        iter_training()
