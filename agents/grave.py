from math import sqrt, log
from copy import deepcopy
from random import choice, random
from time import time as clock

from game import GameState
from mcts import MCTS_ARGS
from game import GameMeta
from agents.rave import RaveNode, RaveMctsAgent

class GRaveNode(RaveNode):
    @property
    def value(self, explore_weight=MCTS_ARGS.EXPLORATION, rave_const=MCTS_ARGS.RAVE_CONST, ref=MCTS_ARGS.GRAVE_REF):
        # unless explore is set to zero, maximally favor unexplored nodes
        if self.N == 0:
            return 0 if explore_weight == 0 else GameMeta.INF

        explore = sqrt(2 * log(self.parent.N) / self.N)
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
    def set_gamestate(self, state: GameState) -> None:
        self.root_state = deepcopy(state)
        self.root = RaveNode()

    def move(self, move: tuple) -> None:
        if move in self.root.children:
            child = self.root.children[move]
            child.parent = None
            self.root = child
            self.root_state.play(child.move)
            return

        # if for whatever reason the move is not in the children of
        # the root just throw out the tree and start over
        self.root_state.play(move)
        self.root = RaveNode()

    @staticmethod
    def expand(parent: RaveNode, state: GameState) -> bool:
        """
        Generate the children of the passed "parent" node based on the available
        moves in the passed gamestate and add them to the tree.

        Returns:
            object:
        """
        children = []
        if state.winner != GameMeta.PLAYERS["none"]:
            # game is over at this node so nothing to expand
            return False

        for move in state.moves():
            children.append(RaveNode(move, parent))

        parent.add_children(children)
        return True
