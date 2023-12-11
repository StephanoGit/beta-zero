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

        if self.N_RAVE < ref:
            node = self
            while node.parent is not None:
                node = self.parent
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
