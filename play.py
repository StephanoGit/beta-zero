"""Demo of AlphaHex."""
import os
import numpy as np
from game import Hex


hexgame = Hex()
player = 1
move_history = []

state = hexgame.get_initial_state()

while True:
    os.system('clear')
    hexgame.pretty_please_state(state)
    print("History: ", end="")
    for move in move_history:
        print(f"{move}, ", end=" ")
    print()

    action_table = hexgame.get_valid_moves(state)
    valid_actions = [i for i in range(hexgame.action_size) if action_table[i] == 1]
    valid_moves_str = list(map(lambda x: hexgame.action_to_str(x) if x < hexgame.action_size - 1 else "swap", valid_actions))

    print("Valid moves: ", valid_moves_str)
    move_str = input(f"{player}:")
    while move_str not in valid_moves_str:
        if move_str == "q":
            break
        print(f"'{move_str}' is not a valid move")
        print("Possible moves are: ", valid_moves_str)
        move_str = input(f"{player}:")

    if move_str == "q":
        print("quitting game ...")
        break

    move_history.append(move_str)

    action = hexgame.str_to_action(move_str)
    state = hexgame.get_next_state(state, action, player)
    value, is_terminal = hexgame.get_value_and_terminated(state, action)

    if is_terminal:
        hexgame.pretty_please_state(state)
        print(move_history)
        hexgame.pretty_please_state(state)
        if value == 1:
            print(player, "won")
        break

    player = hexgame.get_opponent(player)
