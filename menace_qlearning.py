import random
import math
import functools
from menace_board import *
from menace2 import *

print = functools.partial(print, flush=True)


class QLearningEngine:
    def __init__(self, name, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.8):
        self.q_table = {}
        self.played_positions = []
        self.is_learning = True
        self.name = name
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate

    def state_action_str(self, state, action):
        return f"{state}_{action}"

    def get_q_value(self, state, action):
        return self.q_table.get(self.state_action_str(state, action), 0.0)

    def update_q_table(self, state, action, reward, next_state):
        best_next_action = max([(self.get_q_value(next_state, a), a) for a in self.get_possible_actions(next_state)])[1]
        current_q_value = self.get_q_value(state, action)
        learned_value = reward + self.discount_factor * self.get_q_value(next_state, best_next_action)
        new_q_value = (1 - self.learning_rate) * current_q_value + self.learning_rate * learned_value
        self.q_table[self.state_action_str(state, action)] = new_q_value

    def choose_action(self, state):
        if random.random() < self.exploration_rate:
            possible_actions = self.get_possible_actions(state)
            return random.choice(possible_actions)
        else:
            q_values = [self.get_q_value(state, action) for action in self.get_possible_actions(state)]
            return self.get_possible_actions(state)[np.argmax(q_values)]

    def get_possible_actions(self, state):
        return [i for i in range(9) if state[math.floor(i / 3)][i % 3] == 0]

    def play(self, board_state):
        action = self.choose_action(board_state)
        self.played_positions.append(action)
        return action

    def resolve_game(self, result):
        if not self.is_learning:
            self.played_positions = []
            return

        if result == 'W':
            reward = 1.0
        elif result == 'L':
            reward = -1.0
        else:
            reward = 0.5

        for state, action in zip(self.played_positions, self.played_positions[1:]):
            next_state = make_move(state, math.floor(action / 3), action % 3, 1)
            self.update_q_table(state, action, reward, next_state)

        self.played_positions = []

    def set_learning(self, is_learning):
        self.is_learning = is_learning

# Example usage:

import numpy as np

def play_game(player1, player2, to_print=True, to_return_winner=False):
    # Initialize the game board
    board = np.zeros((3, 3), dtype=int)

    if to_print:
        print("Initial Board:")
        print_board(board)

    current_player = player1
    while True:
        print(f"{current_player.name}'s turn:")
        action = current_player.play(board)

        row, col = divmod(action, 3)
        board[row, col] = 1 

        if to_print:
            print_board(board)

        game_result = check_game_result(board)
        if game_result is not None:
            player1.resolve_game(game_result)
            player2.resolve_game(game_result)

            if to_print:
                print("Final Board:")
                print_board(board)
                print(f"Result: {game_result}")

            print(f"Game Result: {game_result}")

            if to_return_winner:
                return game_result

            break

        current_player = player2 if current_player == player1 else player1

def check_game_result(board):
    for player in [1, 2]:
        for i in range(3):
            if all(board[i, j] == player for j in range(3)) or all(board[j, i] == player for j in range(3)):
                return 'L' if player == 1 else 'W' 

            if all(board[i, i] == player for i in range(3)) or all(board[i, 2 - i] == player for i in range(3)):
                 return 'W' if player == 1 else 'L' 

    # Check for a draw
    if all(board[i, j] != 0 for i in range(3) for j in range(3)):
        print("Debug - Board is filled. Draw!")
        return 'D'

    return None

def check_game_result_sub(board, player):
    for i in range(3):
        if all(board[i, j] == player for j in range(3)) or all(board[j, i] == player for j in range(3)):
            return 'L' 

    if all(board[i, i] == player for i in range(3)) or all(board[i, 2 - i] == player for i in range(3)):
        return 'L'  

    return None

def print_board(board):
    for row in board:
        print(" ".join(map(str, row)))
    print()

qLearningEngineA = QLearningEngine(name='qLearningEngineA', learning_rate=0.01, exploration_rate=0.6)
qLearningEngineB = QLearningEngine(name='qLearningEngineB', learning_rate=0.01, exploration_rate=0.6)

# Play a game and print the Q-table of qLearningEngineA
play_game(qLearningEngineA, qLearningEngineB, to_print=True)
print(qLearningEngineA.q_table)

for i in range(1000):
    play_game(qLearningEngineA, qLearningEngineB, to_print=False)

# Play another game and print the updated Q-table
play_game(qLearningEngineA, qLearningEngineB, to_print=True)
print(qLearningEngineA.q_table)

for i in range(200):
    result = play_game(qLearningEngineA, qLearningEngineB, to_print=False)

