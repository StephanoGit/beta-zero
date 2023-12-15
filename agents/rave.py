from math import sqrt, log
from copy import deepcopy
from random import choice, random
from time import time as clock

from game import GameState, GameMeta
from mcts import Node, MCTS, MCTS_ARGS

class RaveNode(Node):
    def __init__(self, move: tuple = None, parent: Node = None):
        super().__init__(move, parent)

        self.Q_RAVE = 0  # times this move has been critical in a rollout
        self.N_RAVE = 0  # times this move has appeared in a rollout

    @property
    def value(self, explore: float = MCTS_ARGS.EXPLORATION, rave_const: float = MCTS_ARGS.RAVE_CONST) -> float:
        # unless explore is set to zero, maximally favor unexplored nodes
        if self.N == 0:
            return 0 if explore == 0 else GameMeta.INF

        # rave valuation:
        alpha = max(0, (rave_const - self.N) / rave_const)
        UCT = self.Q / self.N + explore * sqrt(2 * log(self.parent.N) / self.N)
        AMAF = self.Q_RAVE / self.N_RAVE if self.N_RAVE != 0 else 0

        return (1 - alpha) * UCT + alpha * AMAF


class RaveMctsAgent(MCTS):
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

    @staticmethod
    def roll_out(state: GameState) -> tuple:
        """
        Simulate a random game except that we play all known critical
        cells first, return the winning player and record critical cells at the end.

        """
        moves = state.moves()
        while state.winner == GameMeta.PLAYERS["none"]:
            move = choice(moves)
            state.play(move)
            moves.remove(move)

        rave_pts = {
           GameMeta.PLAYERS['white']: [],
           GameMeta.PLAYERS['black']: [],
        }

        for x in range(state.size):
            for y in range(state.size):
                if state.board[x, y]:
                    rave_pts[state.board[x, y]].append((x,y))

        return state.winner, rave_pts

    def backup(self, node: RaveNode, player: int, outcome: int, rave_pts: dict) -> None:
        """
        Update the node statistics on the path from the passed node to root to reflect
        the outcome of a randomly simulated playout.
        """
        # note that reward is calculated for player who just played
        # at the node and not the next player to play
        reward = -1 if outcome == player else 1
        # reward = outcome * player

        while node is not None:
            for point in rave_pts[player]:
                if point in node.children:
                    node.children[point].Q_RAVE += -reward
                    node.children[point].N_RAVE += 1

            node.N += 1
            node.Q += reward
            player = 3 - player
            reward = -reward
            node = node.parent
