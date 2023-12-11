from mcts import MCTS, Node
from game import HexState
from args import MCTS_ARGS
import math
from copy import deepcopy
from random import choice, random
from time import time

class RaveNode(Node):
    def __init__(self, move=None, parent=None):
        super().__init__(move, parent)

        self.Q_RAVE = 0  # times this move has been critical in a rollout
        self.N_RAVE = 0  # times this move has appeared in a rollout

    @property
    def value(self, explore=MCTS_ARGS.EXPLORATION, rave_const=MCTS_ARGS.RAVE_CONST):
        # unless explore is set to zero, maximally favor unexplored nodes
        if self.N == 0:
            return 0 if explore == 0 else math.inf

        # rave valuation:
        alpha = max(0, (rave_const - self.N) / rave_const)
        UCT = self.Q / self.N + explore * math.sqrt(2 * math.log(self.parent.N) / self.N)
        AMAF = self.Q_RAVE / self.N_RAVE if self.N_RAVE != 0 else 0

        return (1 - alpha) * UCT + alpha * AMAF


class RaveMctsAgent(MCTS):
    def __init__(self, state=HexState()):
        super().__init__(state)
        self.root = RaveNode()

    @staticmethod
    def roll_out(state) -> tuple:
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

        moves = {-1: [], 1: []}

        for x in range(state.size):
            for y in range(state.size):
                if not state.board[x, y]:
                    continue

                moves[state.board[x, y]].append(x * 11 + y)

        return state.winner, moves

    @staticmethod
    def expand(parent, state):
        children = []
        if state.winner:
            return False

        for move in state.valid_moves:
            children.append(RaveNode(move, parent))

        parent.add_children(children)
        return True

    def backup(self, node, player, outcome, moves):
        reward = outcome * -player

        while node is not None:
            for move in moves[player]:
                if move in node.children:
                    node.children[move].Q_RAVE += -reward
                    node.children[move].N_RAVE += 1

            node.N += 1
            node.Q += reward
            player *= -1
            reward = -reward
            node = node.parent

    def move(self, move):
        if move in self.root.children:
            child = self.root.children[move]
            child.parent = None
            self.root = child
            self.root_state.play(child.move)
            return

        self.root_state.play(move)
        self.root = RaveNode()

    def set_gamestate(self, state):
        self.root_state = deepcopy(state)
        self.root = RaveNode()
