import numpy as np

class HexState:
    def __init__(self):
        self.size = 11
        self.actions = self.size * self.size + 1
        self.player = 1
        self.board = np.zeros((self.size, self.size), dtype="int8")
        self.white_played = 0
        self.black_played = 0

    def play(self, rc):
        # ! Assumes move is valid
        if rc == self.actions - 1:
            if not self.can_swap:
                raise ValueError("Cannot swap")
            self.board = self.board.T * -1
        else:
            r, c = rc // self.size, rc % self.size
            if self.board[r, c] != 0:
                raise ValueError("Cell is occupied")
            self.board[r, c] = self.player

        self.white_played += self.player == 1
        self.black_played += self.player == -1
        self.player *= -1

    def would_win(self, action):
        if action is None or action == self.actions - 1:
            return False

        r = action // self.size
        c = action % self.size

        self.board[r, c] = self.player
        win = self.check_win(self.player)
        self.board[r, c] = 0

        return win

    @property
    def winner(self):
        if self.check_win(1):
            return 1
        if self.check_win(-1):
            return -1
        return 0

    def check_win(self, player):
        if player == 1:
            condition = lambda a: a // self.size == self.size - 1
        else:
            condition = lambda a: a % self.size == self.size - 1

        visited = set()
        def dfs(a):
            if condition(a):
                return True
            if a in visited:
                return False
            visited.add(a)
            for rn, cn in self.neighbours(a):
                if rn != -1 and self.board[rn, cn] == player and dfs(rn * self.size + cn):
                    return True
            return False

        end = range(self.size) if player == 1 else range(0, self.size * self.size - 1, self.size)

        for a in end:
            if self.board[a // self.size, a % self.size] == player and dfs(a):
                return True
        return False

    @property
    def valid_moves(self):
        moves = np.append((self.board.reshape(-1) == 0).astype(np.uint8), self.can_swap)
        return [i for i, move in enumerate(moves) if move]

    @property
    def can_swap(self):
        return self.white_played == 1 and self.black_played == 0

    def neighbours(self, rc):
        """
            (r-1,c)   (r-1,c+1)
        (r,c-1)    (r,c)    (r,c+1)
            (r+1,c-1)   (r+1,c)
        """
        r = rc // self.size
        c = rc % self.size

        rs = np.array([r-1, r-1, r, r+1, r+1, r])
        cs = np.array([c, c+1, c+1, c, c-1, c-1])

        on_board = (0 <= rs) & (rs < self.size) & (0 <= cs) & (cs < self.size)
        return np.swapaxes(np.where(on_board, (rs, cs), -1), 0, 1)


    def pretty_please_state(self):
        """Display the current state (nicely)."""
        no_to_symbol = {
                -1: "O",
                0: ".",
                1: "#"
        }
        mid_sum = (self.size + self.size - 2) // 2
        print("            1 A")
        for sum in range(self.size + self.size - 1):
            space_no = abs(mid_sum - sum)
            print(" " * space_no, end="")
            if sum < self.size - 1:
                if len(str(sum+2)) < 2:
                    print(" ", end="")
                print(f"{sum+2} ", end="")
            else:
                print(f" {no_to_symbol[1]} ", end="")

            for i in range(sum + 1):
                if i >= self.size:
                    break
                j = sum - i
                if j >= self.size:
                    continue
                print(no_to_symbol[self.board[j, i]], end=" ")
            if sum < self.size - 1:
                print(f"{chr(sum + 66)}")
            else:
                print(no_to_symbol[-1])
        print("            # O")


    def str_to_action(self, p_str: str):
        """Return action from human-readable position."""
        if p_str == "swap":
            return self.actions - 1

        col = ord(p_str[0]) - 65
        row = int(p_str[1:len(p_str)]) - 1
        return row * self.size + col

    def action_to_str(self, action):
        """Return human-readable position from grid position."""
        if action == self.actions - 1:
            return "swap"
        row, col = action // self.size, action % self.size
        row = row + 1
        col = chr(65 + col)
        return col + str(row)

    def debug_game(self, moves):
        import os
        for move in moves:
            _ = input("Enter for next move...")
            os.system('clear')
            action = self.str_to_action(move)
            if not 0 <= action < self.actions or action not in self.valid_moves:
                print(f"[ERR]: Invalid move {move} (action: {action})")
            else:
                print(f"{self.player} played {move}")
            print(self.would_win(action))
            self.play(action)
            self.pretty_please_state()

def test():
    hex_state = HexState()
    hex_state.board[1:, 0] = 1
    hex_state.pretty_please_state()
    print(f"Move A1 wins: {hex_state.would_win(0)}")
    print(f"Move B1 wins: {hex_state.would_win(1)}")
    print(f"Move C1 wins: {hex_state.would_win(2)}")
    print(hex_state.winner)
    hex_state.play(1)
    print(hex_state.winner)
    hex_state = HexState()
    hex_state.board[0, 1:] = -1
    hex_state.player = -1
    hex_state.pretty_please_state()
    print(f"Move A1 wins: {hex_state.would_win(0)}")
    print(f"Move A2 wins: {hex_state.would_win(11)}")
    print(f"Move A3 wins: {hex_state.would_win(22)}")
    print(hex_state.winner)
    hex_state.play(11)
    print(hex_state.winner)


def debug(file_name):
    moves = open(file_name).read().strip().splitlines()
    hex_state = HexState()
    hex_state.debug_game(moves)


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        if sys.argv[1] == "test":
            test()
        if sys.argv[1] == "debug":
            debug(sys.argv[2])
