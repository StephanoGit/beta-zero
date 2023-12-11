from game import HexState
from args import MCTS_ARGS
from copy import deepcopy
from mcts import MCTS, Node
from time import time
from random import choice
import math


class UctNode(Node):
    def __init__(self, move=None, parent=None):
        super().__init__(move, parent)

    @property
    def value(self, explore = MCTS_ARGS.EXPLORATION):
        if self.N == 0:
            return 0 if explore == 0 else math.inf
        else:
            # exploitation + exploration
            return self.Q / self.N + explore * math.sqrt(2 * math.log(self.parent.N) / self.N)

class UctMctsAgent(MCTS):
    def __init__(self, state=HexState()):
        super().__init__(state)
        self.root = UctNode()

    @staticmethod
    def roll_out(state):
        moves = state.valid_moves
        while not state.winner:
            move = choice(moves)

            if move == 121 and not state.can_swap:
                moves.remove(move)
                continue

            state.play(move)
            moves.remove(move)

            if move == 121:
                moves = state.valid_moves

        return (state.winner,)

    @staticmethod
    def expand(parent, state):
        children = []
        if state.winner:
            return False

        for move in state.valid_moves:
            children.append(UctNode(move, parent))

        parent.add_children(children)
        return True

    @staticmethod
    def backup(node, player, outcome):
        reward = 0 if outcome == player else 1

        while node is not None:
            node.N += 1
            node.Q += reward
            node = node.parent
            reward = 0 if reward == 1 else 1

    def move(self, move):
        if move in self.root.children:
            child = self.root.children[move]
            child.parent = None
            self.root = child
            self.root_state.play(child.move)
            return

        self.root_state.play(move)
        self.root = UctNode()

    def set_gamestate(self, state):
        self.root_state = deepcopy(state)
        self.root = UctNode()
