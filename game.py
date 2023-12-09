"""Hex Game State."""
import numpy as np

class Hex:
    def __init__(self):
        self.size = 11
        self.action_size = self.size ** 2 + 1
        self.turn = 1

    def __repr__(self):
        return "Hex"

    def get_initial_state(self):
        return np.zeros((self.size, self.size))

    def get_next_state(self, state, action, player):
        self.turn += 1
        if action == self.action_size - 1:
            assert player == -1
            return self._swap(state)

        r = action // self.size
        c = action % self.size
        state[r, c] = player

        return state

    def check_win(self, state, action):
        if action is None or action == self.action_size - 1:
            return False

        r = action // self.size
        c = action % self.size
        player = np.sign(state[r, c])

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
            for rn, cn in self._neighbours(a):
                if rn != -1 and state[rn, cn] == player and dfs(rn * self.size + cn):
                    return True
            return False

        end = range(self.size) if player == 1 else range(0, self.action_size - 1, self.size)

        for a in end:
            if state[a // self.size, a % self.size] == player and dfs(a):
                return True
        return False

    def get_value_and_terminated(self, state, action):
        if self.check_win(state, action):
            return 1, True
        return 0, False

    def get_opponent(self, player):
        return -player

    def get_opponent_value(self, value):
        return -value

    def get_opponent_action(self, action):
        if action == self.action_size - 1:
          return action
        r, c = action // self.size, action % self.size
        return c * self.size + r

    def change_perspective(self, state):
        # Why should we care what player
        if len(state.shape) == 3:
          return np.swapaxes(state, 1, 2) * -1
        assert len(state.shape) == 2
        return state.T * -1

    def get_encoded_state(self, state, player):
        if player == -1:
            state = self.change_perspective(state)

        my_board = state > 0
        op_board = state < 0
        no_board = state == 0
        can_swap = np.ones_like(my_board) * self.turn == 2

        encoded_state = np.stack((my_board, op_board, no_board, can_swap)).astype(np.float32)

        if len(state.shape) == 3:
            encoded_state = np.swapaxes(encoded_state, 0, 1)

        return encoded_state

    def get_valid_moves(self, state):
        return np.append((state.reshape(-1) == 0).astype(np.uint8), [self.turn == 2])


    def _swap(self, state):
        return state * -1


    def _neighbours(self, rc):
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


    def pretty_please_state(self, state):
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
                print(int(state[j, i]), end=" ")
            if sum < self.size - 1:
                print(f"{chr(sum + 66)}")
            else:
                print(no_to_symbol[-1])
        print("            # O")


    def str_to_action(self, p_str: str):
        """Return action from human-readable position."""
        if p_str == "swap":
            return self.action_size - 1

        col = ord(p_str[0]) - 65
        row = int(p_str[1:len(p_str)]) - 1
        return row * self.size + col

    def action_to_str(self, action):
        """Return human-readable position from grid position."""
        if action == self.action_size - 1:
            return "swap"
        row, col = action // self.size, action % self.size
        row = row + 1
        col = chr(65 + col)
        return col + str(row)

    def debug_game(self, moves):
        import os
        state = self.get_initial_state()
        player = 1
        for move in moves:
            _ = input("Enter for next move...")
            os.system('clear')
            action = self.str_to_action(move)
            if not 0 <= action < self.action_size or not self.get_valid_moves(state)[action]:
                print(f"[ERR]: Invalid move {move} (action: {action})")
            else:
                print(f"{player} played {move}")
            state = self.get_next_state(state, action, player)
            print(self.get_value_and_terminated(state, action))
            self.pretty_please_state(state)
            player *= -1

if __name__ == "__main__":
    moves = open("test.txt").read().splitlines()
    hex = Hex()
    # hex.debug_game(moves)

    state = np.zeros((11, 11))
    state[:, 0] = 1
    hex.pretty_please_state(state)
    print(hex.check_win(state, 0))
    state = np.zeros((11, 11))
    state[3, :] = -1
    state[3, -1] = 1
    hex.pretty_please_state(state)
    print(hex.check_win(state, 33))
