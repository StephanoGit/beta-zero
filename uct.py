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
        self.Q_RAVE = 0  # times this move has been critical in a rollout
        self.N_RAVE = 0  # times this move has appeared in a rollout
        self.children = {}
        self.outcome = None

    def add_children(self, children):
        for child in children:
            self.children[child.move] = child

    @property
    def value(self, explore = MCTS_ARGS.EXPLORATION):
        if self.N == 0:
            return 0 if explore == 0 else math.inf
        else:
            # exploitation + exploration
            return self.Q / self.N + explore * math.sqrt(2 * math.log(self.parent.N) / self.N)

class UctMctsAgent:
    def __init__(self, state=HexState()):
        self.root_state = deepcopy(state)
        self.root = Node()
        self.run_time = 0  # s?
        self.node_count = 0
        self.num_rollouts = 0

    def search(self, time_budget):
        start_time = time()
        num_rollouts = 0

        while time() - start_time < time_budget:
            node, state = self.select_node()
            outcome = self.roll_out(state)
            self.backup(node, state.player, outcome)
            num_rollouts += 1

        run_time = time() - start_time
        node_count = self.tree_size()
        self.run_time = run_time
        self.node_count = node_count
        self.num_rollouts = num_rollouts

    def select_node(self) -> tuple:
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

    @staticmethod
    def expand(parent, state):
        children = []
        if state.winner:
            return False

        for move in state.valid_moves:
            children.append(Node(move, parent))

        parent.add_children(children)
        return True

    @staticmethod
    def roll_out(state):
        moves = state.valid_moves
        while not state.winner:
            move = choice(moves)
            if move == 121:
                if state.white_played != 1 or state.black_played != 0:
                    moves.remove(move)
                else:
                    state.play(move)
                    moves = state.valid_moves
                continue

            state.play(move)
            moves.remove(move)

        return state.winner

    @staticmethod
    def backup(node, player, outcome):
        reward = 0 if outcome == player else 1

        while node is not None:
            node.N += 1
            node.Q += reward
            node = node.parent
            reward = 0 if reward == 1 else 1

    def best_move(self):
        if self.root_state.winner:
            return None

        # choose the move of the most simulated node breaking ties randomly
        max_value = max(self.root.children.values(), key=lambda n: n.N).N
        max_nodes = [n for n in self.root.children.values() if n.N == max_value]
        bestchild = choice(max_nodes)
        return bestchild.move

    def move(self, move):
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

    def set_gamestate(self, state):
        self.root_state = deepcopy(state)
        self.root = Node()

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

if __name__ == "__main__":
   agent = UctMctsAgent()
   agent.search(2)
   print(agent.best_move())
