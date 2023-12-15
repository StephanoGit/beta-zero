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
        if self.N == 0:
            return 0 if explore == 0 else GameMeta.INF
        else:
            return self.Q / self.N + explore * sqrt(2 * log(self.parent.N) / self.N)


class UctMctsAgent(MCTS):
    @staticmethod
    def expand(parent: Node, state: GameState) -> bool:
        children = []
        if state.winner != GameMeta.PLAYERS['none']:
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

        self.root_state.play(move)
        self.root = Node()

    def set_gamestate(self, state: GameState) -> None:
        self.root_state = deepcopy(state)
        self.root = Node()
