from agents.grave import GRaveMctsAgent
from game import HexState
from args import MCTS_ARGS
import math
from copy import deepcopy
from random import choice, random
from time import time

class DMMctsAgent(GRaveMctsAgent):
    def roll_out(self, state):
        moves = state.valid_moves
        good_moves = moves.copy()
        good_opponent_moves = moves.copy()

        while not state.winner:
            done = False
            while len(good_moves) > 0 and not done:
                move = choice(good_moves)
                good_moves.remove(move)

                if state.would_win(move):
                    state.play(move)
                    moves.remove(move)
                    if move in good_opponent_moves:
                        good_opponent_moves.remove(move)
                    done = True

            if not done:
                move = choice(moves)

                if move == 121 and not state.can_swap:
                    moves.remove(move)
                    continue

                state.play(move)
                moves.remove(move)

                if move == 121:
                    moves = state.valid_moves
                    good_moves = moves.copy()
                    good_opponent_moves = moves.copy()

                if move in good_opponent_moves:
                    good_opponent_moves.remove(move)

            good_moves, good_opponent_moves = good_opponent_moves, good_moves


        moves = {-1: [], 1: []}

        for x in range(state.size):
            for y in range(state.size):
                if not state.board[x, y]:
                    continue

                moves[state.board[x, y]].append(x * 11 + y)

        return state.winner, moves
