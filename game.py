from numpy import zeros, int_
from union import UnionFind

class GameMeta:
    PLAYERS = {'none': 0, 'white': 1, 'black': 2}
    INF = float('inf')
    GAME_OVER = -1
    EDGE1 = 1
    EDGE2 = 2
    NEIGHBOR_PATTERNS = ((-1, 0), (0, -1), (-1, 1), (0, 1), (1, 0), (1, -1))
    BRIDGE_PATTERNS = ((-1, -1), (1, -2), (2, -1), (1, 1), (-1, 2), (-2, 1))

class GameState:
    """
    Stores information representing the current state of a game of hex, namely
    the board and the current turn. Also provides functions for playing game.
    """
    def __init__(self, size):
        """
        Initialize the game board and give white first turn.
        Also create our union find structures for win checking.

        Args:
            size (int): The board size
        """
        self.size = size
        self.to_play = GameMeta.PLAYERS['white']
        self.board = zeros((size, size))
        self.board = int_(self.board)
        self.white_played = 0
        self.black_played = 0
        white_groups = UnionFind()
        black_groups = UnionFind()
        white_groups.set_ignored_elements([GameMeta.EDGE1, GameMeta.EDGE2])
        black_groups.set_ignored_elements([GameMeta.EDGE1, GameMeta.EDGE2])

        self.groups = {
            GameMeta.PLAYERS['white']: white_groups,
            GameMeta.PLAYERS['black']: black_groups,
        }

        self.bridges = {
            GameMeta.PLAYERS['white']: set(),
            GameMeta.PLAYERS['black']: set(),
        }


    def play(self, cell: tuple) -> None:
        """
        Play a stone of the player that owns the current turn in input cell.
        Args:
            cell (tuple): row and column of the cell
        """
        if not self.board[cell] == GameMeta.PLAYERS['none']:
            raise ValueError("Cell occupied")

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

        for b in self.bridge_neighbors(cell):
            if self.board[b] == GameMeta.PLAYERS['none']:
                self.bridges[self.to_play].add(cell)

        self.to_play = 3 - self.to_play

    def get_num_played(self) -> dict:
        return {'white': self.white_played, 'black': self.black_played}

    def would_lose(self, cell: tuple, color: int) -> bool:
        """
        Return True is the move indicated by cell and color would lose the game,
        False otherwise.
        """
        connect1 = False
        connect2 = False
        rc = int(self.to_play == GameMeta.PLAYERS['black'])

        if cell[rc] == 0:
            connect1 = True
        elif cell[rc] == self.size - 1:
            connect2 = True
        for n in self.neighbors(cell):
            if self.groups[color].connected(GameMeta.EDGE1, n):
                connect1 = True
            elif self.groups[color].connected(GameMeta.EDGE2, n):
                connect2 = True

        return connect1 and connect2

    def turn(self) -> int:
        """
        Return the player with the next move.
        """
        return self.to_play

    def set_turn(self, player: int) -> None:
        """
        Set the player to take the next move.
        Raises:
            ValueError if player turn is not 1 or 2
        """
        if player in GameMeta.PLAYERS.values() and player != GameMeta.PLAYERS['none']:
            self.to_play = player
        else:
            raise ValueError('Invalid turn: ' + str(player))

    @property
    def winner(self) -> int:
        """
        Return a number corresponding to the winning player,
        or none if the game is not over.
        """
        if self.groups[GameMeta.PLAYERS['white']].connected(GameMeta.EDGE1, GameMeta.EDGE2):
            return GameMeta.PLAYERS['white']
        if self.groups[GameMeta.PLAYERS['black']].connected(GameMeta.EDGE1, GameMeta.EDGE2):
            return GameMeta.PLAYERS['black']
        return GameMeta.PLAYERS['none']

    def neighbors(self, cell: tuple) -> list:
        """
        Return list of neighbors of the passed cell.

        Args:
            cell (tuple):
        """
        x, y = cell

        return [(n[0] + x, n[1] + y) for n in GameMeta.NEIGHBOR_PATTERNS
                if (0 <= n[0] + x < self.size and 0 <= n[1] + y < self.size)]

    def bridge_neighbors(self, cell: tuple) -> list:
        """
        Return list of neighbors of the passed cell.

        Args:
            cell (tuple):
        """
        x, y = cell

        return [(n[0] + x, n[1] + y) for n in GameMeta.BRIDGE_PATTERNS
                if (0 <= n[0] + x < self.size and 0 <= n[1] + y < self.size)]

    def moves(self) -> list:
        """
        Get a list of all moves possible on the current board.
        """
        moves = []
        for y in range(self.size):
            for x in range(self.size):
                if self.board[x, y] == GameMeta.PLAYERS['none']:
                    moves.append((x, y))
        return moves

    def __str__(self):
        """
        Print an ascii representation of the game board.
        Notes:
            Used for gtp interface
        """
        white = 'W'
        black = 'B'
        empty = '.'
        ret = '\n'
        coord_size = len(str(self.size))
        offset = 1
        ret += ' ' * (offset + 1)
        for x in range(self.size):
            ret += str(x + 1) + ' ' * offset * 2
        ret += '\n'
        for y in range(self.size):
            ret += chr(ord('A') + y) + ' ' * (offset * 2 + coord_size - len(str(y + 1)))
            for x in range(self.size):
                if self.board[x, y] == GameMeta.PLAYERS['white']:
                    ret += white
                elif self.board[x, y] == GameMeta.PLAYERS['black']:
                    ret += black
                else:
                    ret += empty
                ret += ' ' * offset * 2
            ret += white + "\n" + ' ' * offset * (y + 1)
        ret += ' ' * (offset * 2 + 1) + (black + ' ' * offset * 2) * self.size
        return ret

    def action_to_str(self, move):
        r, c = move
        return f"{chr(ord('A') + c)}{r + 1}"
