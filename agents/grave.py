from agents.rave import RaveNode, RaveMctsAgent
from game import HexState
from args import MCTS_ARGS
import math
from copy import deepcopy
from random import choice, random
from time import time

class GRaveNode(RaveNode):
    def __init__(self, move=None, parent=None):
        super().__init__(move, parent)

    @property
    def value(self, explore_weight=MCTS_ARGS.EXPLORATION, rave_const=MCTS_ARGS.RAVE_CONST, ref=MCTS_ARGS.GRAVE_REF):
        # unless explore is set to zero, maximally favor unexplored nodes
        if self.N == 0:
            return 0 if explore_weight == 0 else math.inf

        explore = math.sqrt(2 * math.log(self.parent.N) / self.N)
        exploit = self.Q / self.N
        UCT = exploit + explore_weight * explore

        N_RAVE = self.N_RAVE
        Q_RAVE = self.Q_RAVE
        alpha = 0
        AMAF = 0

        if self.N_RAVE < ref:
            node = self
            c = 0
            while node.parent is not None:
                c += 1
                node = node.parent
                if node.N_RAVE >= ref:
                    N_RAVE = node.N_RAVE
                    Q_RAVE = node.Q_RAVE
                    break
            alpha = max(0, (rave_const - self.N) / rave_const)
            AMAF = self.Q_RAVE / self.N_RAVE if self.N_RAVE != 0 else 0

        return (1 - alpha) * UCT + alpha * AMAF

class GRaveMctsAgent(RaveMctsAgent):
    def __init__(self, state=HexState()):
        super().__init__(state)

    @staticmethod
    def expand(parent, state):
        children = []
        if state.winner:
            return False

        for move in state.valid_moves:
            children.append(GRaveNode(move, parent))

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
        self.root = GRaveNode()

    def set_gamestate(self, state):
        self.root_state = deepcopy(state)
        self.root = GRaveNode()
