"""Generic MCTS agent class."""
from game import HexState
from args import MCTS_ARGS
from copy import deepcopy
from time import time
from random import choice
from queue import Queue
import math

class Node:
    def __init__(self, move=None, parent=None):
        self.move = move
        self.parent = parent
        self.N = 0       # times this position was visited
        self.Q = 0       # average reward (wins-losses) from this position
        self.children = {}
        self.outcome = None

    def add_children(self, children):
        for child in children:
            self.children[child.move] = child

    @property
    def value(self, explore=MCTS_ARGS.EXPLORATION):
        pass


class MCTS:
    def __init__(self, state=HexState()):
        self.root_state = deepcopy(state)
        self.run_time = 0
        self.node_count = 0
        self.num_rollouts = 0
        self.root = None

    @staticmethod
    def roll_out(state):
        pass

    @staticmethod
    def expand(parent, state):
        pass

    @staticmethod
    def backup(node, player, *args):
        pass

    def move(self, move):
        pass

    def set_gamestate(self, state):
        pass

    def search(self, time_budget):
        start_time = time()
        num_rollouts = 0

        while time() - start_time < time_budget:
            node, state = self.select_node()
            self.backup(node, state.player, *self.roll_out(state))
            num_rollouts += 1

        run_time = time() - start_time
        node_count = self.tree_size()
        self.run_time = run_time
        self.node_count = node_count
        self.num_rollouts = num_rollouts

    def select_node(self):
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

    def best_move(self):
        if self.root_state.winner:
            return None

        # choose the move of the most simulated node breaking ties randomly
        max_value = max(self.root.children.values(), key=lambda n: n.N).N
        max_nodes = [n for n in self.root.children.values() if n.N == max_value]
        bestchild = choice(max_nodes)
        return bestchild.move

    def statistics(self):
        return self.num_rollouts, self.node_count, self.run_time

    def tree_size(self):
        q = Queue()
        count = 0
        q.put(self.root)
        while not q.empty():
            node = q.get()
            count += 1
            for child in node.children.values():
                q.put(child)
        return count
