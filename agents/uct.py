from math import sqrt, log
from copy import deepcopy
from queue import Queue
from random import choice
from time import time as clock
from game import GameState, GameMeta
from mcts import Node, MCTS, MCTS_ARGS

class UctNode(Node):
    @property
    def value(self, explore: float = MCTS_ARGS.EXPLORATION):
        """
        Calculate the UCT value of this node relative to its parent, the parameter
        "explore" specifies how much the value should favor nodes that have
        yet to be thoroughly explored versus nodes that seem to have a high win
        rate.
        Currently explore is set to 0.5.

        """
        if self.N == 0:
            return 0 if explore == 0 else GameMeta.INF
        else:
            return self.Q / self.N + explore * sqrt(2 * log(self.parent.N) / self.N)


class UctMctsAgent(MCTS):
    """
    Attributes:
        root_state (GameState): Game simulator that helps us to understand the game situation
        root (Node): Root of the tree search
        run_time (int): time per each run
        node_count (int): the whole nodes in tree
        num_rollouts (int): The number of rollouts for each search
        EXPLORATION (int): specifies how much the value should favor
                           nodes that have yet to be thoroughly explored versus nodes
                           that seem to have a high win rate.
    """
    @staticmethod
    def expand(parent: Node, state: GameState) -> bool:
        children = []
        if state.winner != GameMeta.PLAYERS['none']:
            # game is over at this node so nothing to expand
            return False

        for move in state.moves():
            children.append(Node(move, parent))

        parent.add_children(children)
        return True

    @staticmethod
    def roll_out(state: GameState) -> int:
        moves = state.moves()

        while state.winner == GameMeta.PLAYERS['none']:
            move = choice(moves)
            state.play(move)
            moves.remove(move)

        return state.winner

    @staticmethod
    def backup(node: Node, turn: int, outcome: int) -> None:
        """
        Update the node statistics on the path from the passed node to root to reflect
        the outcome of a randomly simulated playout.

        Args:
            node:
            turn: winner turn
            outcome: outcome of the rollout

        Returns:
            object:

        """
        # Careful: The reward is calculated for player who just played
        # at the node and not the next player to play
        reward = 0 if outcome == turn else 1

        while node is not None:
            node.N += 1
            node.Q += reward
            node = node.parent
            reward = 0 if reward == 1 else 1

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
        self.root = Node()

    def set_gamestate(self, state: GameState) -> None:
        """
        Set the root_state of the tree to the passed gamestate, this clears all
        the information stored in the tree since none of it applies to the new
        state.

        """
        self.root_state = deepcopy(state)
        self.root = Node()
