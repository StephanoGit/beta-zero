import os
import numpy as np
from game import HexState


hexgame = HexState()
move_history = []

while True:
    os.system('clear')
    hexgame.pretty_please_state()
    print("History: ", end="")
    for move in move_history:
        print(f"{move}, ", end=" ")
    print()

    valid_actions = hexgame.valid_moves
    valid_moves_str = list(map(lambda x: hexgame.action_to_str(x) if x < hexgame.actions - 1 else "swap", valid_actions))

    print("Valid moves: ", valid_moves_str)
    move_str = input(f"{hexgame.player}:")
    while move_str not in valid_moves_str:
        if move_str == "q":
            break
        print(f"'{move_str}' is not a valid move")
        print("Possible moves are: ", valid_moves_str)
        move_str = input(f"{hexgame.player}:")

    if move_str == "q":
        print("quitting game ...")
        break

    move_history.append(move_str)

    action = hexgame.str_to_action(move_str)
    if not hexgame.would_win(action):
        hexgame.play(action)
        continue

    hexgame.play(action)
    print(move_history)
    hexgame.pretty_please_state()
    print(hexgame.player * -1, "won")
    break
