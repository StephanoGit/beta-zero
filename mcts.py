from math import sqrt, log
from copy import deepcopy
from queue import Queue
from random import choice
from time import time as clock
from game import GameState, GameMeta

class MCTS_ARGS:
    EXPLORATION = 0.7
    RAVE_CONST = 300
    GRAVE_REF = 300
    RANDOMNESS = 0.5
    POOLRAVE_CAPACITY = 10
    K_CONST = 10
    A_CONST = 0.25
    WARMUP_ROLLOUTS = 7

class Node:
    def __init__(self, move: tuple = None, parent: object = None):
        self.move = move
        self.parent = parent
        self.N = 0  # times this position was visited
        self.Q = 0  # average reward (wins-losses) from this position
        self.children = {}
        self.outcome = GameMeta.PLAYERS['none']

    def add_children(self, children: dict) -> None:
        for child in children:
            self.children[child.move] = child

    @property
    def value(self, explore: float = MCTS_ARGS.EXPLORATION):
        pass

class MCTS:
    def __init__(self, state=GameState(11)):
        self.root_state = deepcopy(state)
        self.root = Node()
        self.run_time = 0
        self.node_count = 0
        self.num_rollouts = 0


    @staticmethod
    def expand(parent: Node, state: GameState) -> bool:
        pass

    @staticmethod
    def roll_out(state: GameState) -> int:
        pass

    @staticmethod
    def backup(node: Node, turn: int, outcome: int) -> None:
        pass

    def move(self, move: tuple) -> None:
        pass

    def search(self, time_budget: int) -> None:
        """
        Search and update the search tree for a
        specified amount of time in seconds.

        """
        start_time = clock()
        num_rollouts = 0

        # do until we exceed our time budget
        while clock() - start_time < time_budget:
            node, state = self.select_node()
            turn = state.turn()
            self.backup(node, turn, *self.roll_out(state))
            num_rollouts += 1
        run_time = clock() - start_time
        node_count = self.tree_size()
        self.run_time = run_time
        self.node_count = node_count
        self.num_rollouts = num_rollouts

    def select_node(self) -> tuple:
        """
        Select a node in the tree to preform a single simulation from.

        """
        node = self.root
        state = deepcopy(self.root_state)

        # stop if we find reach a leaf node
        while len(node.children) != 0:
            # descend to the maximum value node, break ties at random
            children = node.children.values()
            max_value = max(children, key=lambda n: n.value).value
            max_nodes = [n for n in node.children.values()
                         if n.value == max_value]
            node = choice(max_nodes)
            state.play(node.move)

            # if some child node has not been explored select it before expanding
            # other children
            if node.N == 0:
                return node, state

        # if we reach a leaf node generate its children and return one of them
        # if the node is terminal, just return the terminal node
        if self.expand(node, state):
            node = choice(list(node.children.values()))
            state.play(node.move)
        return node, state

    def best_move(self) -> tuple:
        """
        Return the best move according to the current tree.
        Returns:
            best move in terms of the most simulations number unless the game is over
        """
        if self.root_state.winner != GameMeta.PLAYERS['none']:
            return GameMeta.GAME_OVER

        # choose the move of the most simulated node breaking ties randomly
        max_value = max(self.root.children.values(), key=lambda n: n.N).N
        max_nodes = [n for n in self.root.children.values() if n.N == max_value]
        bestchild = choice(max_nodes)
        return bestchild.move

    def set_gamestate(self, state: GameState) -> None:
        """
        Set the root_state of the tree to the passed gamestate, this clears all
        the information stored in the tree since none of it applies to the new
        state.

        """
        self.root_state = deepcopy(state)
        self.root = Node()

    def statistics(self) -> tuple:
        return self.num_rollouts, self.node_count, self.run_time

    def tree_size(self) -> int:
        """
        Count nodes in tree by BFS.
        """
        Q = Queue()
        count = 0
        Q.put(self.root)
        while not Q.empty():
            node = Q.get()
            count += 1
            for child in node.children.values():
                Q.put(child)
        return count
