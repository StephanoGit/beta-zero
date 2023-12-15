from game import GameState, GameMeta
from copy import deepcopy
from union import UnionFind
import random

class BridgeState(GameState):
    """
    Game State that additionally tracks bridge connections.
    """
    bridge_patterns = (((-1,-1), ((-1, 0),( 0,-1))),
                       ((-2, 1), ((-1, 0),(-1, 1))),
                       ((-1, 2), ((-1, 1),( 0, 1))),
                       (( 1, 1), (( 1, 0),( 0, 1))),
                       (( 2,-1), (( 1, 0),( 1,-1))),
                       (( 1,-2), (( 1,-1),( 0,-1))))

    def __init__(self, state: GameState):
        self.size = state.size
        self.to_play = state.to_play
        self.board = deepcopy(state.board)
        white_groups = deepcopy(state.groups[GameMeta.PLAYERS['white']])
        black_groups = deepcopy(state.groups[GameMeta.PLAYERS['black']])
        self.groups = {
            GameMeta.PLAYERS['white']: white_groups,
            GameMeta.PLAYERS['black']: black_groups,
        }
        self.pairs = {
            GameMeta.PLAYERS['white']: {},
            GameMeta.PLAYERS['black']: {},
        }
        self.compute_bridges()
        self.lastmove = None
        self.white_played = state.white_played
        self.black_played = state.black_played

    def recompute_groups(self):
        # Should ignore edges?
        self.groups = {
            GameMeta.PLAYERS['white']: UnionFind(),
            GameMeta.PLAYERS['black']: UnionFind(),
        }

        for i in range(self.size):
            for j in range(self.size):
                cell = (i,j)
                if self.board[cell] == GameMeta.PLAYERS["none"]:
                    continue

                rc = int(self.board[cell] == GameMeta.PLAYERS["black"])
                if cell[rc] == 0:
                    self.groups[self.board[cell]].join(GameMeta.EDGE1, cell)
                if cell[rc] == self.size - 1:
                    self.groups[self.board[cell]].join(GameMeta.EDGE2, cell)
                for n in self.neighbors(cell):
                    if self.board[n] == self.board[cell]:
                        self.groups[self.board[cell]].join(cell, n)

    def compute_bridges(self):
        self.pairs = {
            GameMeta.PLAYERS['white']: {},
            GameMeta.PLAYERS['black']: {},
        }
        shuffled_i = list(range(self.size))
        shuffled_j = list(range(self.size))
        random.shuffle(shuffled_i)
        random.shuffle(shuffled_j)
        for i in shuffled_i:
            for j in shuffled_j:
                if self.board[i, j] !=  GameMeta.PLAYERS["none"]:
                    self.update_bridges((i, j))

    def update_bridges(self, cell):
        player = self.board[cell]
        pairs = self.pairs[player]

        shuffled_bridge_patterns = list(self.bridge_patterns)
        random.shuffle(shuffled_bridge_patterns)
        for b, (m1, m2) in shuffled_bridge_patterns:
            c =  (b[0]    + cell[0], b[1]    + cell[1])  # potential connection
            m1 = (m1[0] + cell[0], m1[1] + cell[1])      # associated bridge pair
            m2 = (m2[0] + cell[0], m2[1] + cell[1])


            # if the potential connection is out of bounds need only check for bridge
            # connections with player owned edges
            if c[0] < 0 or c[0] >= self.size or c[1] < 0 or c[1] >= self.size:
                if m1[0] < 0 or m1[0] >= self.size or m1[1] < 0 or m1[1] >= self.size or \
                   m2[0] < 0 or m2[0] >= self.size or m2[1] < 0 or m2[1] >= self.size:
                    continue

                rc = int(player == GameMeta.PLAYERS['black'])
                if c[rc] == -1:
                    c = GameMeta.EDGE1
                elif c[rc] == self.size:
                    c = GameMeta.EDGE2
                else:
                    continue


            # if the two cells invloved in the bridge pair are not both empty there
            # is no bridge connection
            if not (self.board[m1] == self.board[m2] == GameMeta.PLAYERS["none"]):
                continue

            # if we don't control the potential connected cell there is no
            # bridge connection
            if not (c == GameMeta.EDGE1 or c == GameMeta.EDGE2 or self.board[c] == player):
                continue

            #if either of the two cells in the bridge pair is involved in another
            #bridge connection, we cannot also involve it in this one
            if m1 in pairs or m2 in pairs:
                continue

            #join the newly bridge-connected groups
            if self.groups[player].join(cell, c):
                # add the associated bridge pair to the pairs dictionary
                # unless the groups are already the same in which case this connection
                # is redundant
                self.set_bridge(m1, m2, player)
                assert self.board[m1] == self.board[m2] == 0

    def clear_bridge(self, cell, player):
        if cell in self.pairs[player]:
            other = self.pairs[player][cell]
            del self.pairs[player][cell]
            del self.pairs[player][other]

    def set_bridge(self, cell1, cell2, player):
        self.pairs[player][cell1] = cell2
        self.pairs[player][cell2] = cell1


    def get_bridge(self, cell, player=None):
        player = player or self.to_play

        if cell not in self.pairs[player]:
            return None
        return self.pairs[player][cell]


    def bridge_winner(self):
        """
        Return a number corresponding to the winning player (including wins by
        virtual connection), or none if the game is not over.
        """
        if self.groups[GameMeta.PLAYERS['white']].connected(GameMeta.EDGE1, GameMeta.EDGE2):
            return GameMeta.PLAYERS["white"]
        if self.groups[GameMeta.PLAYERS['black']].connected(GameMeta.EDGE1, GameMeta.EDGE2):
            return GameMeta.PLAYERS["black"]
        return GameMeta.PLAYERS["none"]

    def winner(self):
        return self.bridge_winner

    def play(self, cell: tuple) -> None:
        if not self.board[cell] == GameMeta.PLAYERS['none']:
            raise ValueError("Cell occupied")

        if cell in self.pairs[self.to_play]:
            self.clear_bridge(cell, self.to_play)

        self.board[cell] = self.to_play
        self.white_played += self.to_play == GameMeta.PLAYERS['white']
        self.black_played += self.to_play == GameMeta.PLAYERS['black']

        rc = int(self.to_play == GameMeta.PLAYERS['black'])
        if cell[rc] == 0:
            self.groups[self.to_play].join(GameMeta.EDGE1, cell)
        if cell[rc] == self.size - 1:
            self.groups[self.to_play].join(GameMeta.EDGE2, cell)

        for n in self.neighbors(cell):
            if self.board[n] == self.to_play:
                self.groups[self.to_play].join(n, cell)

        if self.lastmove in self.pairs[self.to_play]:
            if self.pairs[self.to_play] != cell:
                self.recompute_groups()
                self.compute_bridges()
            else:
                self.clear_bridge(self.lastmove, self.to_play)
        else:
            self.update_bridges(cell)
            self.lastmove = cell

        self.to_play = 3 - self.to_play
