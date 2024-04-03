import random
import math
from itertools import chain
import functools
from menace_board import *
from menace2 import *

print = functools.partial(print, flush=True)

def tuple_state_to_dict(st):
    st_list = []
    pos = 0
    for i in st:
        for j in i:
            st_list.append(pos)
            pos += 1
            st_list.append(j)
    it = iter(st_list)
    st_dict = dict(zip(it, it))
    return st_dict

class TokenBag:
    def __init__(self, start_tokens=3):
        board_dict = {}
        for i in range(9):
            board_dict[i] = start_tokens

        self.token_counts = board_dict

    def __str__(self):
        return str(self.token_counts)

class MatchBoxes:
    def __init__(self):
        self.set_box_values()

    def tuple_state_to_dict(self, st):
        st_list = []
        pos = 0
        for i in st:
            for j in i:
                st_list.append(pos)
                pos += 1
                st_list.append(j)
        it = iter(st_list)
        st_dict = dict(zip(it, it))
        return st_dict

    def set_box_values(self):
        new_dict = {}
        all_states = all_states_and_groups()
        for key, value in all_states.items():
            if value not in new_dict:
                new_dict[value] = [TokenBag(), [key]]

        for key, value in new_dict.items():
            canonical_state = value[1][0]
            new_dict[key][1] = get_symmetries(canonical_state)
            board_state_dict = self.tuple_state_to_dict(new_dict[key][1][0])
            for pos in board_state_dict:
                if board_state_dict[pos] != 0:
                    new_dict[key][0].token_counts[pos] = 0

        self.boxes = new_dict

    def show_token_bag(self, box_number):
        print(f"Token Bag for Box {box_number}: {self.boxes[box_number][0]}")
        
    def get_token(self, board_state):
        board_position_symmetries = get_symmetries(((0, 1, 2), (3, 4, 5), (6, 7, 8)))
        all_states = all_states_and_groups()
        if board_state not in all_states:
            print('ERROR: Board state not among allowed states.')
            print_state(board_state)
            return

        box_number = all_states[board_state]
        box = self.boxes[box_number]

        total_tokens = sum(box[0].token_counts.values())
        if total_tokens == 0:
            box[0] = TokenBag()
            board_state_dict = self.tuple_state_to_dict(box[1][0])
            for pos in board_state_dict:
                if board_state_dict[pos] != 0:
                    box[0].token_counts[pos] = 0

            total_tokens = sum(box[0].token_counts.values())

        try:
            random_number = random.randint(1, total_tokens)
        except ValueError:
            print(f'ERROR: No tokens in box {box_number}. {box[0].token_counts}')
            return

        tokens_counted = 0
        for position, count in box[0].token_counts.items():
            tokens_counted += count
            if random_number <= tokens_counted:
                chosen_token = position
                break

        symmetry_state_index = box[1].index(board_state)
        board_position_symmetry_dict = self.tuple_state_to_dict(board_position_symmetries[symmetry_state_index])
        symmetry_position = [k for k, v in board_position_symmetry_dict.items() if v == chosen_token][0]

        return box_number, chosen_token, symmetry_position
    

class MenaceEngine:
    def __init__(self, name):
        self.boxes = MatchBoxes()
        self.played_positions = []
        self.is_learning = True
        self.name = name

    def play(self, board_state):
        box_number, chosen_token, symmetry_position = self.boxes.get_token(board_state)
        self.played_positions.append((box_number, chosen_token))
        return symmetry_position

    def resolve_game(self, result):
        if not self.is_learning:
            self.played_positions = []
            return

        if result == 'W':
            for box_number, position in self.played_positions:
                self.boxes.set_box_values()
        elif result == 'L':
            # Handle the case for a loss
            pass
        elif result == 'D':
            # Handle the case for a draw
            pass

        self.played_positions = []

    def set_box_values(self):
        new_dict = {}
        all_states = all_states_and_groups()
        for key, value in all_states.items():
            if value not in new_dict:
                new_dict[value] = [TokenBag(), [key]]

        for key, value in new_dict.items():
            canonical_state = value[1][0]
            new_dict[key][1] = get_symmetries(canonical_state)
            board_state_dict = self.tuple_state_to_dict(new_dict[key][1][0])
            for pos in board_state_dict:
                if board_state_dict[pos] != 0:
                    new_dict[key][0].token_counts[pos] = 0

        self.boxes = new_dict

    def set_learning(self, is_learning):
        self.is_learning = is_learning

def play_game(playerA, playerB, to_print=True, to_return_winner=False):
    if random.randint(0, 1) == 0:
        player1, player2 = playerA, playerB
    else:
        player1, player2 = playerB, playerA

    board_state = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
    is_game_over = False
    winner = None
    turn = 0
    to_print = to_print

    def tuple_state_to_list(st):
        l = []
        for t in st:
            l.append(list(t))
        return l

    def list_state_to_tuple(st):
        t = []
        for l in st:
            t.append(tuple(l))
        return tuple(t)

    if to_print:
        print(f"Player 1: {player1.name} vs. Player 2: {player2.name}")
        print(f"Turn {turn}")
        print_state(board_state)
        print('\n')
    turn += 1

    while not is_game_over:
        position = player1.play(board_state)
        board_state = tuple_state_to_list(board_state)
        board_state[math.floor(position / 3)][position % 3] = 1
        board_state = list_state_to_tuple(board_state)
        if to_print:
            print(f"Turn {turn}, {player1.name}")
            print_state(board_state)
            print('\n')
        turn += 1
        is_game_over = is_end(board_state)
        if is_game_over:
            winner = 1
            if to_print:
                print(f"{player1.name} wins!")
            break

        if list(chain.from_iterable(tuple_state_to_list(board_state))).count(0) == 0:
            is_game_over = True
            winner = 0
            if to_print:
                print("The game is a draw!")
            break

        position = player2.play(board_state)
        board_state = tuple_state_to_list(board_state)
        board_state[math.floor(position / 3)][position % 3] = 2
        board_state = list_state_to_tuple(board_state)
        if to_print:
            print(f"Turn {turn}, {player2.name}")
            print_state(board_state)
            print('\n')
        turn += 1
        is_game_over = is_end(board_state)
        if is_game_over:
            winner = 2
            if to_print:
                print(f"{player2.name} wins!")
            break

    if is_game_over:
        if winner == 1:
            player1.resolve_game('W')
            player2.resolve_game('L')
            winning_player = player1.name
        elif winner == 2:
            player1.resolve_game('L')
            player2.resolve_game('W')
            winning_player = player2.name
        else:
            player1.resolve_game('D')
            player2.resolve_game('D')
            winning_player = 'Draw'

    if to_return_winner:
        return winning_player

testEngineA = MenaceEngine(name='testEngineA')
testEngineB = MenaceEngine(name='testEngineB')
play_game(testEngineA, testEngineB, to_print=True)
testEngineA.boxes.show_token_bag(1)

for i in range(100):
    play_game(testEngineA, testEngineB, to_print=False)

play_game(testEngineA, testEngineB, to_print=True)

for i in range(1000):
    play_game(testEngineA, testEngineB, to_print=False)

play_game(testEngineA, testEngineB, to_print=True)

draws_and_games = [0, 0]
for i in range(100):
    result = play_game(testEngineA, testEngineB, to_print=False, to_return_winner=True)
    draws_and_games[1] += 1
    if result == 'Draw':
        draws_and_games[0] += 1

print(f"{(draws_and_games[0] / draws_and_games[1] * 100):.0f}% of games end in a draw.")

for i in range(1000):
    play_game(testEngineA, testEngineB, to_print=False)
    draws_and_games = [0, 0]
    for i in range(100):
        result = play_game(testEngineA, testEngineB, to_print=False, to_return_winner=True)
        draws_and_games[1] += 1
        if result == 'Draw':
            draws_and_games[0] += 1

    print(f"{(draws_and_games[0] / draws_and_games[1] * 100):.0f}% of games end in a draw.")

for i in range(5000):
    play_game(testEngineA, testEngineB, to_print=False)
    draws_and_games = [0, 0]
    for i in range(100):
        result = play_game(testEngineA, testEngineB, to_print=False, to_return_winner=True)
        draws_and_games[1] += 1
        if result == 'Draw':
            draws_and_games[0] += 1

    print(f"{(draws_and_games[0] / draws_and_games[1] * 100):.0f}% of games end in a draw.")

play_game(testEngineA, testEngineB, to_print=True)

class HumanPlayer:
    def __init__(self, name):
        self.name = name

    def play(self, board_state):
        print("Enter a position (0-8):")
        position = int(input())
        return position

    def resolve_game(self, result):
        pass

play_game(HumanPlayer('I, the player'), testEngineA, to_print=True)

untrainedMENACE = MenaceEngine(name='untrainedMENACE')
untrainedMENACE.set_learning(False)
play_game(untrainedMENACE, testEngineA, to_print=True)

untrainedwins_and_games = [0, 0, 0]
for i in range(100):
    result = play_game(untrainedMENACE, testEngineA, to_print=False, to_return_winner=True)
    untrainedwins_and_games[2] += 1
    if result == 'untrainedMENACE':
        untrainedwins_and_games[0] += 1
    if result == 'Draw':
        untrainedwins_and_games[1] += 1

print(
    f"The untrained engine wins {(untrainedwins_and_games[0] / untrainedwins_and_games[2] * 100):.0f}% \
of games and {(untrainedwins_and_games[1] / untrainedwins_and_games[2] * 100):.0f}% end in a draw.")
